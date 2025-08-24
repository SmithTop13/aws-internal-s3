import os
import json
from flask import Flask, request, jsonify, render_template, send_from_directory
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size

# Initialize S3 client
try:
    s3_client = boto3.client('s3')
except NoCredentialsError:
    print("Error: AWS credentials not found. Please configure AWS credentials via environment variables or IAM role.")
    exit(1)

# Get bucket name from environment variable
BUCKET_NAME = os.environ.get('S3_BUCKET_NAME')
if not BUCKET_NAME:
    print("Error: S3_BUCKET_NAME environment variable is required.")
    exit(1)

# Check if bucket supports ACLs
def bucket_supports_acls():
    try:
        response = s3_client.get_bucket_ownership_controls(Bucket=BUCKET_NAME)
        ownership_rules = response.get('OwnershipControls', {}).get('Rules', [])
        for rule in ownership_rules:
            if rule.get('ObjectOwnership') == 'BucketOwnerEnforced':
                return False
        return True
    except ClientError:
        # If we can't get ownership controls, assume ACLs are supported
        return True

BUCKET_SUPPORTS_ACLS = bucket_supports_acls()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/bucket-info')
def bucket_info():
    return jsonify({
        'success': True,
        'bucket_name': BUCKET_NAME,
        'supports_acls': BUCKET_SUPPORTS_ACLS
    })

@app.route('/api/files')
def list_files():
    prefix = request.args.get('prefix', '')
    
    try:
        response = s3_client.list_objects_v2(
            Bucket=BUCKET_NAME,
            Prefix=prefix,
            Delimiter='/'
        )
        
        files = []
        folders = []
        
        # Process folders (common prefixes)
        if 'CommonPrefixes' in response:
            for prefix_info in response['CommonPrefixes']:
                folder_name = prefix_info['Prefix'].rstrip('/').split('/')[-1]
                folders.append({
                    'name': folder_name,
                    'type': 'folder',
                    'path': prefix_info['Prefix']
                })
        
        # Process files
        if 'Contents' in response:
            for obj in response['Contents']:
                # Skip the prefix itself if it's a folder
                if obj['Key'].endswith('/'):
                    continue
                    
                file_name = obj['Key'].split('/')[-1]
                if file_name:  # Skip empty names
                    files.append({
                        'name': file_name,
                        'type': 'file',
                        'path': obj['Key'],
                        'size': obj['Size'],
                        'last_modified': obj['LastModified'].isoformat(),
                        'download_url': f"/api/download?key={obj['Key']}"
                    })
        
        return jsonify({
            'success': True,
            'files': files,
            'folders': folders,
            'current_prefix': prefix
        })
        
    except ClientError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/upload', methods=['POST'])
def upload_file():
    files = request.files.getlist('files')
    if not files or len(files) == 0:
        # Try single file parameter for backward compatibility
        single_file = request.files.get('file')
        if single_file:
            files = [single_file]
        else:
            return jsonify({'success': False, 'error': 'No files provided'}), 400
    
    prefix = request.form.get('prefix', '')
    acl = request.form.get('acl', 'private')
    
    # Validate ACL value
    valid_acls = ['private', 'public-read', 'public-read-write', 'authenticated-read']
    if acl not in valid_acls:
        return jsonify({
            'success': False,
            'error': f'Invalid ACL value: {acl}. Must be one of: {", ".join(valid_acls)}'
        }), 400
    
    # Check if bucket supports ACLs for non-private settings
    if not BUCKET_SUPPORTS_ACLS and acl != 'private':
        return jsonify({
            'success': False,
            'error': f'Bucket does not support ACLs (BucketOwnerEnforced). Only private uploads are allowed.'
        }), 400
    
    # Filter out empty files
    valid_files = [f for f in files if f.filename != '']
    if not valid_files:
        return jsonify({'success': False, 'error': 'No valid files selected'}), 400
    
    results = []
    errors = []
    
    for file in valid_files:
        try:
            filename = secure_filename(file.filename)
            if not filename:  # Skip if filename becomes empty after sanitization
                errors.append(f'Invalid filename: {file.filename}')
                continue
                
            s3_key = f"{prefix}{filename}" if prefix else filename
            
            # Prepare upload arguments
            upload_args = {'ServerSideEncryption': 'AES256'}
            
            # Only add ACL if not using default private setting
            # Some buckets have ACLs disabled (BucketOwnerEnforced)
            if acl != 'private':
                upload_args['ACL'] = acl
            
            s3_client.upload_fileobj(
                file,
                BUCKET_NAME,
                s3_key,
                ExtraArgs=upload_args
            )
            
            results.append({
                'filename': filename,
                'key': s3_key,
                'success': True
            })
            
        except ClientError as e:
            errors.append(f'Failed to upload {file.filename}: {str(e)}')
        except Exception as e:
            errors.append(f'Error processing {file.filename}: {str(e)}')
    
    # Determine response based on results
    if results and not errors:
        return jsonify({
            'success': True,
            'message': f'Successfully uploaded {len(results)} file(s)',
            'uploaded_files': results
        })
    elif results and errors:
        return jsonify({
            'success': True,
            'message': f'Uploaded {len(results)} file(s) with {len(errors)} error(s)',
            'uploaded_files': results,
            'errors': errors
        }), 207  # Multi-status
    else:
        return jsonify({
            'success': False,
            'error': 'Failed to upload any files',
            'errors': errors
        }), 500

@app.route('/api/acl', methods=['POST'])
def update_acl():
    data = request.get_json()
    
    if not data or 'key' not in data or 'acl' not in data:
        return jsonify({
            'success': False,
            'error': 'Missing required fields: key and acl'
        }), 400
    
    s3_key = data['key']
    acl = data['acl']
    
    # Validate ACL value
    valid_acls = ['private', 'public-read', 'public-read-write', 'authenticated-read']
    if acl not in valid_acls:
        return jsonify({
            'success': False,
            'error': f'Invalid ACL. Must be one of: {", ".join(valid_acls)}'
        }), 400
    
    try:
        s3_client.put_object_acl(
            Bucket=BUCKET_NAME,
            Key=s3_key,
            ACL=acl
        )
        
        return jsonify({
            'success': True,
            'message': f'ACL updated to {acl} for {s3_key}'
        })
        
    except ClientError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/create-directory', methods=['POST'])
def create_directory():
    data = request.get_json()
    
    if not data or 'name' not in data:
        return jsonify({
            'success': False,
            'error': 'Missing required field: name'
        }), 400
    
    directory_name = data['name'].strip()
    prefix = data.get('prefix', '')
    
    # Validate directory name
    if not directory_name:
        return jsonify({
            'success': False,
            'error': 'Directory name cannot be empty'
        }), 400
    
    # Remove any slashes from the directory name and add trailing slash
    directory_name = directory_name.strip('/').replace('/', '-')
    
    # Validate directory name characters
    import re
    if not re.match(r'^[a-zA-Z0-9\-_.]+$', directory_name):
        return jsonify({
            'success': False,
            'error': 'Directory name can only contain letters, numbers, hyphens, underscores, and periods'
        }), 400
    
    # Create the full directory path
    directory_key = f"{prefix}{directory_name}/"
    
    try:
        # Check if directory already exists
        response = s3_client.list_objects_v2(
            Bucket=BUCKET_NAME,
            Prefix=directory_key,
            MaxKeys=1
        )
        
        if 'Contents' in response and len(response['Contents']) > 0:
            return jsonify({
                'success': False,
                'error': f'Directory "{directory_name}" already exists'
            }), 409
        
        # Create directory by uploading empty object with trailing slash
        s3_client.put_object(
            Bucket=BUCKET_NAME,
            Key=directory_key,
            Body=b'',
            ServerSideEncryption='AES256'
        )
        
        return jsonify({
            'success': True,
            'message': f'Directory "{directory_name}" created successfully',
            'directory_key': directory_key
        })
        
    except ClientError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/download')
def download_file():
    key = request.args.get('key')
    
    if not key:
        return jsonify({'error': 'Missing key parameter'}), 400
    
    try:
        # Generate a presigned URL for download
        download_url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': BUCKET_NAME, 'Key': key},
            ExpiresIn=3600  # URL expires in 1 hour
        )
        
        return jsonify({
            'success': True,
            'download_url': download_url
        })
        
    except ClientError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.errorhandler(413)
def request_entity_too_large(error):
    return jsonify({
        'success': False,
        'error': 'File too large. Maximum size is 100MB.'
    }), 413

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
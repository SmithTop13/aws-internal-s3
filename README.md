# AWS S3 Internal Browser

A simple, self-hosted web-based file browser for Amazon S3 buckets, designed for internal use. Built with Python Flask backend and vanilla JavaScript frontend.

## Features

### 🗂️ File Management
- **Browse S3 buckets** with folder navigation
- **Upload single or multiple files** with drag-and-drop support
- **Download files** with presigned URLs
- **Navigate directories** with breadcrumb navigation and direct path input

### 🔒 Access Control
- **ACL management** during upload (Private, Public Read, etc.)
- **Automatic ACL detection** for bucket compatibility
- **IAM-based authentication** using AWS credentials

### 🚀 User Experience
- **Real-time progress tracking** for uploads
- **File preview** with size information
- **Responsive design** with clean AWS-style UI
- **Error handling** with detailed feedback
- **Multiple file selection** with batch operations

### 🛠️ Technical Features
- **AWS connectivity checks** before startup
- **Automatic dependency installation**
- **tmux session management** for background operation
- **Environment-based configuration**
- **Least-privilege IAM policy** included

## Prerequisites

- **Python 3.7+**
- **AWS CLI** (automatically installed if not present)
- **tmux** (for session management)
- **Valid AWS credentials** configured
- **S3 bucket** with appropriate permissions

## Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/aws-internal-s3.git
cd aws-internal-s3
```

### 2. Set Environment Variables
```bash
export S3_BUCKET_NAME=your-bucket-name
```

### 3. Configure AWS Credentials
Choose one of the following methods:

**Option A: AWS CLI**
```bash
aws configure
```

**Option B: Environment Variables**
```bash
export AWS_ACCESS_KEY_ID=your-access-key
export AWS_SECRET_ACCESS_KEY=your-secret-key
export AWS_DEFAULT_REGION=your-region
```

**Option C: IAM Role** (if running on EC2)
- Attach the provided IAM policy to your EC2 instance role

### 4. Start the Application
```bash
chmod +x start.sh
./start.sh
```

The application will:
- ✅ Test AWS connectivity and permissions
- ✅ Create Python virtual environment
- ✅ Install dependencies automatically
- ✅ Start the web server on port 5000

### 5. Access the Web Interface
Open your browser and navigate to: **http://localhost:5000**

## Configuration

### Environment Variables

| Variable | Required | Description | Default |
|----------|----------|-------------|---------|
| `S3_BUCKET_NAME` | Yes | Target S3 bucket name | None |
| `AWS_ACCESS_KEY_ID` | No* | AWS access key | From AWS config |
| `AWS_SECRET_ACCESS_KEY` | No* | AWS secret key | From AWS config |
| `AWS_DEFAULT_REGION` | No* | AWS region | From AWS config |

*Required if not using AWS CLI or IAM roles

### IAM Permissions

Apply the included IAM policy (`iam-policy.json`) to your AWS user or role:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "ListBucketContents",
            "Effect": "Allow",
            "Action": ["s3:ListBucket"],
            "Resource": "arn:aws:s3:::your-bucket-name"
        },
        {
            "Sid": "GetObjectOperations", 
            "Effect": "Allow",
            "Action": ["s3:GetObject", "s3:GetObjectAcl"],
            "Resource": "arn:aws:s3:::your-bucket-name/*"
        },
        {
            "Sid": "PutObjectOperations",
            "Effect": "Allow", 
            "Action": ["s3:PutObject", "s3:PutObjectAcl"],
            "Resource": "arn:aws:s3:::your-bucket-name/*"
        }
    ]
}
```

## Usage

### File Navigation
- **Click folders** to navigate into directories
- **Use breadcrumbs** to navigate up the hierarchy
- **Enter paths directly** in the "Navigate to:" field (e.g., `folder1/folder2/`)

### File Upload
1. **Click "Choose Files"** to select one or multiple files
2. **Preview selected files** in the file list
3. **Select access level** (Private, Public Read, etc.)
4. **Click "Upload"** and monitor progress

### File Management
- **Download files** using the download button
- **Manage ACLs** using the ACL button for individual files
- **View file information** including size and last modified date

## Management Commands

### Application Control
```bash
# View application logs
tmux attach-session -t s3-browser

# Stop the application  
tmux kill-session -t s3-browser

# List active sessions
tmux list-sessions

# Restart application
./start.sh
```

### Development Mode
```bash
# Run in development mode (with debug output)
export S3_BUCKET_NAME=your-bucket-name
source venv/bin/activate
python app.py
```

## Project Structure

```
aws-internal-s3/
├── app.py                 # Flask backend application
├── templates/
│   └── index.html        # Frontend web interface
├── requirements.txt      # Python dependencies
├── start.sh             # Startup script with connectivity checks
├── iam-policy.json      # Least-privilege IAM policy
├── CLAUDE.md           # Project development instructions
├── .gitignore          # Git ignore rules
└── README.md           # This file
```

## API Endpoints

The application provides RESTful API endpoints:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Web interface |
| `/api/files` | GET | List bucket contents |
| `/api/upload` | POST | Upload files with ACL |
| `/api/download` | GET | Generate download URLs |
| `/api/acl` | POST | Update file ACL |
| `/api/bucket-info` | GET | Get bucket information |

## Troubleshooting

### Common Issues

**🔴 "AWS credentials not configured"**
- Ensure AWS credentials are set up via CLI, environment variables, or IAM role
- Test with: `aws sts get-caller-identity`

**🔴 "Cannot access S3 bucket"**
- Verify bucket name is correct
- Check IAM permissions using provided policy
- Ensure bucket exists and is in the correct region

**🔴 "ACL not supported"**
- Bucket has ACLs disabled (BucketOwnerEnforced)
- Use "Private" access level only
- Application automatically detects and handles this

**🔴 "Port 5000 already in use"**
- Kill existing processes: `tmux kill-session -t s3-browser`
- Or use different port by modifying `start.sh`

**🔴 "tmux session already running"**
- Attach to existing session: `tmux attach-session -t s3-browser`
- Or kill and restart: `tmux kill-session -t s3-browser && ./start.sh`

### Debug Mode
Enable debug logging by running the application directly:
```bash
export S3_BUCKET_NAME=your-bucket-name
export FLASK_DEBUG=1
python app.py
```

## Security Considerations

### Best Practices
- ✅ **Use least-privilege IAM policies**
- ✅ **Enable S3 server-side encryption**
- ✅ **Run on internal networks only**
- ✅ **Use IAM roles instead of access keys when possible**
- ✅ **Regular credential rotation**

### Security Features
- **No credential storage** in application code
- **Presigned URLs** for secure downloads
- **ACL validation** before upload
- **Input sanitization** for file paths
- **Error message filtering** to prevent information disclosure

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [Flask](https://flask.palletsprojects.com/) web framework
- AWS SDK for Python ([Boto3](https://boto3.amazonaws.com/))
- [Gunicorn](https://gunicorn.org/) WSGI HTTP Server
- Clean UI inspired by AWS Console design

---

**⚠️ Important**: This application is designed for internal use only. Do not expose it to the public internet without proper authentication and security measures.
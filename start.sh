#!/bin/bash

# AWS S3 Internal Browser - Startup Script
# This script starts the Flask application using gunicorn in a detached tmux session

SESSION_NAME="s3-browser"
APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PATH="$APP_DIR/venv"

echo "AWS S3 Internal Browser - Starting Application"
echo "============================================="

# Check if tmux session already exists
if tmux has-session -t "$SESSION_NAME" 2>/dev/null; then
    echo "❌ Error: tmux session '$SESSION_NAME' is already running."
    echo "   Use 'tmux attach-session -t $SESSION_NAME' to attach to the existing session."
    echo "   Use 'tmux kill-session -t $SESSION_NAME' to stop the existing session."
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "$VENV_PATH" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv "$VENV_PATH"
    if [ $? -ne 0 ]; then
        echo "❌ Error: Failed to create virtual environment."
        exit 1
    fi
fi

# Check if requirements are installed
if [ ! -f "$VENV_PATH/lib/python*/site-packages/flask/__init__.py" ]; then
    echo "📦 Installing Python dependencies..."
    "$VENV_PATH/bin/pip" install --upgrade pip
    "$VENV_PATH/bin/pip" install -r "$APP_DIR/requirements.txt"
    if [ $? -ne 0 ]; then
        echo "❌ Error: Failed to install dependencies."
        exit 1
    fi
fi

# Check for required environment variables
if [ -z "$S3_BUCKET_NAME" ]; then
    echo "⚠️  S3_BUCKET_NAME environment variable is not set."
    echo ""
    read -p "   Please enter your S3 bucket name: " S3_BUCKET_NAME
    
    if [ -z "$S3_BUCKET_NAME" ]; then
        echo "❌ Error: S3 bucket name is required."
        exit 1
    fi
    
    echo "   Using S3 bucket: $S3_BUCKET_NAME"
    export S3_BUCKET_NAME
    echo ""
fi

# Check AWS S3 connectivity
echo "🔍 Checking AWS S3 connectivity..."

# Use AWS CLI from virtual environment
AWS_CMD="$VENV_PATH/bin/aws"

# Test AWS credentials
echo "   • Testing AWS credentials..."
if ! $AWS_CMD sts get-caller-identity &> /dev/null; then
    echo "❌ Error: AWS credentials not configured or invalid."
    echo "   Please configure AWS credentials using one of these methods:"
    echo "   • AWS CLI: aws configure"
    echo "   • Environment variables: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY"
    echo "   • IAM instance role (if running on EC2)"
    echo "   • AWS credentials file (~/.aws/credentials)"
    exit 1
fi

# Get AWS identity info
AWS_IDENTITY=$($AWS_CMD sts get-caller-identity --output text --query 'Arn' 2>/dev/null)
echo "   ✅ AWS credentials valid: $AWS_IDENTITY"

# Test S3 bucket access
echo "   • Testing S3 bucket access..."
if ! $AWS_CMD s3api head-bucket --bucket "$S3_BUCKET_NAME" &> /dev/null; then
    echo "❌ Error: Cannot access S3 bucket '$S3_BUCKET_NAME'."
    echo "   Possible issues:"
    echo "   • Bucket does not exist"
    echo "   • Insufficient permissions"
    echo "   • Incorrect bucket name"
    echo "   • Bucket in different region"
    exit 1
fi

# Get bucket region
BUCKET_REGION=$($AWS_CMD s3api get-bucket-location --bucket "$S3_BUCKET_NAME" --output text --query 'LocationConstraint' 2>/dev/null)
if [ "$BUCKET_REGION" = "None" ] || [ -z "$BUCKET_REGION" ]; then
    BUCKET_REGION="us-east-1"
fi
echo "   ✅ S3 bucket accessible: s3://$S3_BUCKET_NAME (region: $BUCKET_REGION)"

# Test basic S3 operations
echo "   • Testing S3 permissions..."
TEST_KEY=".s3-browser-connectivity-test-$(date +%s)"

# Test ListObjects permission
if ! $AWS_CMD s3api list-objects-v2 --bucket "$S3_BUCKET_NAME" --max-items 1 &> /dev/null; then
    echo "❌ Error: Missing s3:ListBucket permission for bucket '$S3_BUCKET_NAME'."
    exit 1
fi

# Test PutObject permission (create a small test file)
echo "test" | $AWS_CMD s3 cp - "s3://$S3_BUCKET_NAME/$TEST_KEY" &> /dev/null
if [ $? -ne 0 ]; then
    echo "❌ Error: Missing s3:PutObject permission for bucket '$S3_BUCKET_NAME'."
    exit 1
fi

# Test GetObject permission
$AWS_CMD s3 cp "s3://$S3_BUCKET_NAME/$TEST_KEY" /tmp/s3-test-download 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Error: Missing s3:GetObject permission for bucket '$S3_BUCKET_NAME'."
    # Clean up test file if it was created
    $AWS_CMD s3 rm "s3://$S3_BUCKET_NAME/$TEST_KEY" &> /dev/null
    exit 1
fi
# Clean up downloaded test file
rm -f /tmp/s3-test-download

# Clean up test file
$AWS_CMD s3 rm "s3://$S3_BUCKET_NAME/$TEST_KEY" &> /dev/null

echo "   ✅ S3 permissions verified (ListBucket, GetObject, PutObject)"
echo ""

# Create the tmux session and start the application
echo "🚀 Starting application in detached tmux session '$SESSION_NAME'..."

tmux new-session -d -s "$SESSION_NAME" -c "$APP_DIR" \
    "source $VENV_PATH/bin/activate && \
     echo 'Starting AWS S3 Internal Browser...' && \
     echo 'Press Ctrl+C to stop the application' && \
     echo 'Use: tmux attach-session -t $SESSION_NAME to view logs' && \
     echo '' && \
     gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 app:app"

if [ $? -eq 0 ]; then
    echo "✅ Application started successfully!"
    echo ""
    echo "📋 Application Information:"
    echo "   • URL: http://localhost:5000"
    echo "   • tmux session: $SESSION_NAME"
    echo "   • Working directory: $APP_DIR"
    echo ""
    echo "🔧 Useful Commands:"
    echo "   • View logs: tmux attach-session -t $SESSION_NAME"
    echo "   • Stop app: tmux kill-session -t $SESSION_NAME"
    echo "   • List sessions: tmux list-sessions"
    echo ""
    echo "⚠️  Important Notes:"
    echo "   • Make sure to set S3_BUCKET_NAME environment variable"
    echo "   • Ensure AWS credentials are properly configured"
    echo "   • The application runs on port 5000"
else
    echo "❌ Error: Failed to start tmux session."
    exit 1
fi
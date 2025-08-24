Act as a Senior Full-Stack Cloud Developer. Your task is to design and generate the complete source code for a simple, self-hosted S3 web browser UI for internal use.

The application must be built using the Python Flask framework for the backend and vanilla JavaScript/HTML/CSS for the frontend.

---

### ## 1. Backend (Python/Flask)

* Create a file `app.py`.
* The backend must securely get AWS credentials from environment variables or an IAM instance role.
* Implement the following API endpoints:
    * `GET /api/files`: Lists files and folders from a specified S3 prefix.
    * `POST /api/upload`: Handles file uploads to a specified S3 prefix.
    * `POST /api/acl`: Updates the ACL for a specified S3 object.

---

### ## 2. Frontend (HTML/JS/CSS)

* Create a single `templates/index.html` file with a clean UI for navigation, file listing, and uploading.

---

### ## 3. AWS IAM Policy

* Provide the JSON for a least-privilege IAM policy that the application's server role will need.

---

### ## 4. Deployment Scripts (No Docker)

* Provide a `requirements.txt` file listing the necessary Python libraries (`Flask`, `boto3`, `gunicorn`).
* Generate a Bash script named `start.sh` that automates running the application.
* The script must perform the following actions:
    1.  Check if the `tmux` session is already running to prevent duplicates.
    2.  If not running, create a new, **detached** `tmux` session.
    3.  Within the new session, it must activate the Python virtual environment and launch the application using `gunicorn`.
    4.  Provide clear terminal output confirming that the application has started successfully.

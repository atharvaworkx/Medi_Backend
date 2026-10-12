## Atomicloops Django Setup

### Project-Name : <>

### 1. Clone the repository

```
git clone <url>
cd <repo-name>
git checkout -b dev
```

### 2. Install AWS CLI and configurations as per your os

- [Install AWSCLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
- [Install & Configure AWSCLI](https://medium.com/analytics-vidhya/configure-aws-cli-and-execute-commands-fc16a17b0aa2)

### 3. Create a new virtualenv and install requirements (Soon will be deprecated)

- [How to install virtualenv](./docs/Install%20Virtaulenv.pdf)

#### Windows

```
virtualenv venv
.\venv\Scripts\activate
pip install -r requirements.txt
pip install "drf-yasg[validation]"
pip install git+https://github.com/atomic-loops/atomicloops-django-logger
```

#### Linux and Mac OS

```
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
pip install "drf-yasg[validation]"
pip install git+https://github.com/atomic-loops/atomicloops-django-logger
```

### 4. Configure Environment Variables (Security Setup)

**IMPORTANT**: Set up environment variables before running the application.

```bash
# Copy the example file
cp .env.example .env

# Generate secure Flower credentials using Python
python3 << 'EOF'
import secrets
import string

# Generate secure username (alphanumeric, 12 chars)
username = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))

# Generate secure password (24 chars with special characters)
alphabet = string.ascii_letters + string.digits + string.punctuation
password = ''.join(secrets.choice(alphabet) for _ in range(24))

print(f"\nGenerated Flower Credentials:")
print(f"Username: {username}")
print(f"Password: {password}")
print(f"\nAdd these to your .env file:")
print(f"FLOWER_USER={username}")
print(f"FLOWER_PASSWORD={password}")
EOF

# Edit .env with your UID/GID and the generated credentials
# Get your UID/GID: id -u (for UID) and id -g (for GID)
# nano .env  # or use your preferred editor
```

### 5. Download vault file
Note: After downloading please update the vault file with your email credentials.


A. Initial
```
wget -O src/vault.py https://atomicloops-dev.s3.ap-south-1.amazonaws.com/vault.py
```

Windows

```
curl -o src/vault.py https://atomicloops-dev.s3.ap-south-1.amazonaws.com/vault.py
```

B. Latest

```
wget -O src/vault.py https://atomicloops-dev.s3.ap-south-1.amazonaws.com/vault.py
```

Windows

```
curl -o src/vault.py https://atomicloops-dev.s3.ap-south-1.amazonaws.com/vault.py
```

Note :- Update the urls for Lastest Section when you sync the vault file.

### 6. Initialize Project Setup

[Setup Email Password](http://165.232.181.62/books/backend-development/page/generate-password-for-automated-e-mail)

[Atomicloops Django Setup](./docs/ProjectSetup.pdf)

[Atomicloops Custom Commands with Bash](http://165.232.181.62/books/backend-development/page/django-atomicloops-commands-bash)

[Atomicloops Custom Commands python](https://drive.google.com/file/d/1dKK_Eo-7OAAFYTrEtS_N5pQGDLK06Y-a/view?usp=share_link)

### 7. Create the database tables

```
python manage.py makemigrations
python manage.py migrate
```

### 8. Start Server

```sh
./run.sh start-dev
```

### 9. Update and Sync Vault

To Add Secret key add the variable to vault file.

```
./run.sh sync-vault
```

### 10. How to add new libraries
Bash scripts
```

## Production deployment configuration

Set these values in the deployment platform's secret/environment settings; do not
commit them to `.env` or source control:

- `ENV=prod`
- `DJANGO_SECRET_KEY`
- `DATABASE_URL`
- `ALLOWED_HOSTS`
- `GROK_API_KEY` (the xAI key used for report generation)
- `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_STORAGE_BUCKET_NAME`, and
  `AWS_S3_REGION_NAME` for image uploads

The Flutter flow is:

1. POST image metadata to `api/v1/images/request_upload_url/`.
2. Upload the file with HTTP `PUT` to the returned `uploadUrl`, preserving the
   returned `Content-Type`.
3. POST to `api/v1/reports/generate_report/` after all images are uploaded.

The API key is read at runtime from `GROK_API_KEY`; never place the key in the
Flutter app or in this repository.
./run.sh interactive-dev
pip install <package_name>
pip freeze > requirements.txt
exit
./run.sh start-dev
```
Python scripts
```
source venv/bin/activate
pip install <package_name>
pip freeze > requirements.txt
./run.sh start-dev
```

TODO:
Create atomicloops package

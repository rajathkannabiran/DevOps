# GitLab Pipelines Monitor

A Python tool to monitor and display the latest pipeline status for all projects within a GitLab group on a specific release branch.

## Features

- Fetches projects from GitLab groups and subgroups
- Displays latest pipeline status for a specific branch
- Exports results to CSV format
- Concurrent processing for better performance
- Handles authentication and error cases gracefully

## Dependencies

- `python-gitlab` - GitLab API client library
- `python-dotenv` - Environment variable loader

## Setup Instructions

### 1. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
venv\Scripts\activate     # On Windows
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configuration

Update the `.env` file with your GitLab configuration:

```bash
# GitLab Configuration
GITLAB_URL=https://your-gitlab-instance.com
GITLAB_PRIVATE_TOKEN=your-personal-access-token

# Project Configuration
GITLAB_GROUP=12345
RELEASE_BRANCH_NAME=release/q3-2024
```

#### Creating a GitLab Personal Access Token

1. Go to your GitLab instance → User Settings → Access Tokens
2. Create a new token with `read_api` and `read_repository` scopes
3. Copy the token and set it as the `GITLAB_PRIVATE_TOKEN` in your `.env` file

## How to Run

```bash
# Activate virtual environment
source venv/bin/activate

# Run the script
python pipelines.py

# Deactivate when done
deactivate
```

## Output

The tool generates a CSV report with pipeline information and displays progress in the terminal.

## Configuration

- **GITLAB_GROUP**: Group ID (numeric) or full path
- **RELEASE_BRANCH_NAME**: Branch name to monitor
- **GITLAB_URL**: Your GitLab instance URL
- **GITLAB_PRIVATE_TOKEN**: Personal access token with `read_api` scope

## Security

The `.env` file is automatically ignored by Git to protect sensitive credentials.
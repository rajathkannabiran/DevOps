import gitlab
import os
import sys
import csv
from datetime import datetime
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

# Load environment variables from .env file
load_dotenv()

# --- Configuration ---
# Configuration is now loaded from .env file
GITLAB_GROUP = os.getenv('GITLAB_GROUP')
RELEASE_BRANCH_NAME = os.getenv('RELEASE_BRANCH_NAME')

def get_latest_pipelines():
    """
    Connects to GitLab, iterates through projects in a group, and
    fetches the latest pipeline for a specific branch, displaying
    the results in a table.
    """
    # Get GitLab URL and Token from environment variables
    gitlab_url = os.getenv('GITLAB_URL')
    private_token = os.getenv('GITLAB_PRIVATE_TOKEN')

    # Check if environment variables are set
    if not gitlab_url or not private_token or not GITLAB_GROUP or not RELEASE_BRANCH_NAME:
        print("Error: Please configure GITLAB_URL, GITLAB_PRIVATE_TOKEN, GITLAB_GROUP, and RELEASE_BRANCH_NAME in .env file.")
        sys.exit(1)

    # Authenticate with GitLab
    try:
        gl = gitlab.Gitlab(gitlab_url, private_token=private_token)
        gl.auth()
        print(f"Successfully authenticated to {gitlab_url}")
    except Exception as e:
        print(f"Failed to authenticate with GitLab. Error: {e}")
        sys.exit(1)

    try:
        # Get the group object
        group = gl.groups.get(GITLAB_GROUP)
        print(f"\nFetching projects for group: '{group.name}'...")

        # Get all projects in the group, including from subgroups
        projects = group.projects.list(all=True, include_subgroups=True, per_page=100)

        if not projects:
            print(f"No projects found in group '{group.name}'.")
            return

        print(f"Found {len(projects)} projects. Checking for pipelines on branch '{RELEASE_BRANCH_NAME}'...\n")

        table_headers = ["Project Name", "Pipeline URL", "Status", "Created At"]
        table_data = []

        # Process projects concurrently for better performance
        def fetch_project_pipeline(project):
            try:
                # Use lazy loading and limit pipeline results
                proj = gl.projects.get(project.id, lazy=True)
                pipelines = proj.pipelines.list(ref=RELEASE_BRANCH_NAME, order_by='id', sort='desc', per_page=1, get_all=False)

                if pipelines:
                    latest_pipeline = pipelines[0]
                    return [
                        project.name,
                        latest_pipeline.web_url,
                        latest_pipeline.status,
                        latest_pipeline.created_at
                    ]
                else:
                    return [
                        project.name,
                        "N/A",
                        "No pipeline found",
                        "N/A"
                    ]
            except gitlab.exceptions.GitlabError as e:
                return [
                    project.name,
                    "Error",
                    f"Error: {e.error_message}",
                    "N/A"
                ]

        # Use ThreadPoolExecutor for concurrent API calls
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_project = {executor.submit(fetch_project_pipeline, project): project for project in projects}
            
            for future in as_completed(future_to_project):
                result = future.result()
                table_data.append(result)
        
        elapsed_time = time.time() - start_time
        print(f"Completed in {elapsed_time:.2f} seconds\n")

        # Save to CSV file (only projects with pipelines)
        if table_data:
            # Filter out projects without pipelines
            filtered_data = [row for row in table_data if row[1] != "N/A" and "No pipeline found" not in row[2]]
            
            if filtered_data:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"pipeline_report_{timestamp}.csv"
                
                with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(table_headers)
                    writer.writerows(filtered_data)
                
                print(f"Report saved to {filename}")
                print(f"Projects with pipelines: {len(filtered_data)} out of {len(table_data)} total")
            else:
                print("No projects with pipelines found to save.")
        else:
            print("No data to save.")


    except gitlab.exceptions.GitlabGetError as e:
        print(f"Error: Could not find GitLab group with ID or path '{GITLAB_GROUP}'. Please check it.")
        print(f"GitLab API response: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    get_latest_pipelines()

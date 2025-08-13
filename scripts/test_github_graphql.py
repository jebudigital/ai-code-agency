import os
import requests
import json

# Load token from .env
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
load_dotenv(dotenv_path=Path(__file__).parent.parent / '.env')
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')

assert GITHUB_TOKEN, "GITHUB_TOKEN not found in .env"

GRAPHQL_ENDPOINT = "https://api.github.com/graphql"
HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Content-Type": "application/json"
}

def run_query(query, variables=None):
    payload = {"query": query}
    if variables:
        payload["variables"] = variables
    response = requests.post(GRAPHQL_ENDPOINT, headers=HEADERS, json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    return response.json()

if __name__ == "__main__":
    # 1. Get viewer info
    print("--- Viewer Info ---")
    viewer_query = """
    query { viewer { id login } }
    """
    run_query(viewer_query)

    # 2. Try to get organization info (should fail if org doesn't exist)
    org_login = "jebudigital"  # Change if you want to test another org
    print("--- Organization Info ---")
    org_query = """
    query($login: String!) {
      organization(login: $login) { id login }
      user(login: $login) { id login }
    }
    """
    run_query(org_query, {"login": org_login})

    # 3. Try to create a project board under user (replace with your user id)
    print("--- Create Project Board (User) ---")
    # First, get user id
    viewer_resp = run_query(viewer_query)
    user_id = viewer_resp.get('data', {}).get('viewer', {}).get('id')
    if user_id:
        create_project_query = """
        mutation($ownerId:ID!, $name:String!) {
          createProjectV2(input: {ownerId: $ownerId, title: $name}) {
            projectV2 { id title url }
          }
        }
        """
        run_query(create_project_query, {"ownerId": user_id, "name": "Test Project Board"})
    else:
        print("Could not get user id for project creation.")

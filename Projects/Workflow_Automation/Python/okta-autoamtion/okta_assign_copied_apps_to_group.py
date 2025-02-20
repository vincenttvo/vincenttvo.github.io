import requests
import json
import subprocess
import time

# Function to retrieve the API key from 1Password vault.
def okta_api_token():
    result = subprocess.run(
        ["op", "read", "op://path-to-item"],
        capture_output = True,
        text = True
    )
    # Extract and return the API key from the result
    okta_api_token = result.stdout.strip()
    return okta_api_token

# Function to retrieve the Okta company domain from 1Password vault.
def okta_company_domain():
    result = subprocess.run(
        ["op", "read", "op://path-to-item"],
        capture_output = True,
        text = True
    )
    okta_company_domain = result.stdout.strip()
    return okta_company_domain

def set_headers(okta_api_token):
    # Set up headers
    headers = {
        "Authorization": f"SSWS {okta_api_token}",
        "Content-Type": "application/json"
    }
    return headers

# Function to handle API rate limits in Okta
def handle_rate_limit(response):
    if response.status_code == 429: # Rate limit error
        retry_after = response.headers.get("X-Rate-Limit-Reset", "60")
        print(f"Rate limit exceeded. Retrying after {retry_after} seconds...")
        time.sleep(int(retry_after)) # Sleep before retrying
        return True
    return False # No retry needed

# Function to initialize or get group IDs and apps
def get_group_and_apps(source_group_id, target_group_id):
    # Assuming source_group_id and target_group_id are passed when calling this function
    return source_group_id, target_group_id, []

# Get Okta API URL
def get_app_url(okta_company_domain, app_id):
    return f"https://{okta_company_domain}/api/v1/apps/{app_id}/groups"

def get_assigned_apps(okta_api_token, okta_company_domain, source_group_id):
    url = f"https://{okta_company_domain}/api/v1/groups/{source_group_id}/apps?limit=200"
    headers = set_headers(okta_api_token)
    assigned_apps = []

    while True:
        print(f"Making request to: {url}")
        response = requests.get(url, headers=headers)

        if handle_rate_limit(response):
            continue

        if response.status_code == 200:
            apps = response.json()
            assigned_apps.extend(apps)
            print(f"Retrieved {len(apps)} applications assigned to group {source_group_id} from this page.")

            link_header = response.headers.get("Link", None)

            if link_header:
                # Find the "next" link for the next page
                next_page = None
                for link in link_header.split(","):
                    if "rel=\"next\"" in link:
                        next_page = link.split(";")[0].strip("<>").strip()
                        break
                if next_page:
                    url = next_page
                else:
                    url = None # No more pages
            else:
                print(f"No \'Link\" header found, assuming no more pages.")
        else:
            print(f"Failed to retrieve applications. Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            return []
    
        print(f"Total applications retrieved: {len(assigned_apps)}")
        return assigned_apps

# Assign multiple apps to new group
def assign_apps_to_group(okta_api_token, okta_company_domain, assigned_apps, new_group_id):
    for app in assigned_apps:
        app_id = app["id"] # Extract the app ID from the response
        app_name = app.get("label", "Unknown")
        check_url = f"https://{okta_company_domain}/api/v1/apps/{app_id}/groups"
        headers = set_headers(okta_api_token)
        response = requests.get(check_url, headers=headers)

        if handle_rate_limit(response):
            continue

        if response.status_code == 200:
            # Get list of groups that this app is assigned to
            assigned_groups = response.json()

            # Check if app is already assigned to the target group
            already_assigned = any(group["id"] == new_group_id for group in assigned_groups)

            if already_assigned:
                print(f"Application with ID {app_id} {app_name} is already assigned to target group. Skipping.")
                continue # Skip this app and move on to the next one
            else:
                # Proceed to assign the app to the new group
                url = f"https://{okta_company_domain}/api/v1/apps/{app_id}/groups/{new_group_id}"

                # Payload for assigning the app to the group (Okta expects a body with a groupId)
                payload = {
                    "id": new_group_id
                }
                response = requests.put(url, headers=headers, data=json.dumps(payload)) # Use PUT for assignment

                if handle_rate_limit(response):
                    continue

                if response.status_code in [200, 201]:
                    print(f"Application with ID {app_id} {app_name} successfully assigned to the new group.")
                else:
                    if response.status_code == 404:
                        print(f"Application with ID {app_id} {app_name} not found. Skipping this app.")
                    else:
                        print(f"Failed to assign app {app_id} {app_name} to new group. Status Code: {response.status_code}")
                        print(f"Response: {response.text}")

def main():

    api_token = okta_api_token()
    company_domain = okta_company_domain()
    source_group_id = input(f"Enter Okta Source Group ID: ").strip()
    target_group_id = input(f"Enter Okta Target Group ID: ").strip()

    source_group_id, target_group_id = get_group_and_apps(source_group_id, target_group_id)

    # Get the list of apps assigned to the source group
    assigned_apps = get_assigned_apps(api_token, company_domain, source_group_id)

    if assigned_apps:
        # Assign each app to the new group
        assign_apps_to_group(api_token, company_domain, assigned_apps, target_group_id)
    else:
        print("No applications found to assign")


# Run the script
if __name__ == "__main__":
    main()
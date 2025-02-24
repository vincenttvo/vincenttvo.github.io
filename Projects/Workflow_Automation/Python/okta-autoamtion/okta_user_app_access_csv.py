# Script to automate generating Okta user's current app access

import requests
import subprocess
import json
import os
import csv

# Function to retrieve the API key from 1Password vault. Can update to take hardcoded value instead of from 1Password vault
def okta_api_token():
    result = subprocess.run(
        ["op", "read", "op://op-path-to-vault-item"],
        capture_output = True,
        text = True
    )
    # Extract and return the API key from the result
    okta_api_token = result.stdout.strip()
    return okta_api_token

# Function to retrieve the Okta company domain from 1Password vault. Can update to take hardcoded value instead of from 1Password vault
def okta_company_domain():
    result = subprocess.run(
        ["op", "read", "op://op-path-to-vault-item"],
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

def get_user_assigned_apps(okta_api_token, okta_company_domain, user_id):
    url = f"https://{okta_company_domain}/api/v1/users/{user_id}/appLinks"
    headers = set_headers(okta_api_token)

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        apps_data = response.json()

        print(f"Downloading assigned apps for {user_id}")

        # Print the result or save it for further processing. Optional
        # print(json.dumps(apps_data, indent=4))

        # Now export this data to a CSV
        # export_to_csv(user_id)
        # print(f"Assigned apps structure for {user_id}: {json.dumps(apps_data, indent=4)}")  # Debugging print
        print(f'User {user_id} has {len(apps_data)} assigned apps.')
        return apps_data
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return []

def get_user_groups(okta_api_token, okta_company_domain, user_id):
    url = f"https://{okta_company_domain}/api/v1/users/{user_id}/groups"
    headers = set_headers(okta_api_token)

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        # Return the group name and group id
        return [(group["id"], group["profile"]["name"]) for group in response.json()]
    else:
        print(f"Error retrieving groups for user {user_id}: {response.status_code}, {response.text}")
        return []
    
def get_group_assigned_apps(okta_api_token, okta_company_domain, group_id):
    url = f"https://{okta_company_domain}/api/v1/groups/{group_id}/apps"
    headers = set_headers(okta_api_token)

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        apps = response.json()
        # print(f"Assigned apps structure for {group_id}: {json.dumps(apps, indent=4)}")  # Debugging print
        # Print the number of applications found for the group
        print(f"Group {group_id} has {len(apps)} assigned apps.")
        return apps
    else:
        print(f"Error retrieving apps for group {group_id}: {response.status_code}, {response.text}")
        return []

def export_to_csv(user_apps, user_id, group_apps):
    # Where to export the file to
    export_dir = "/Users/vincentvo/Downloads" 
    # Define the CSV file name based on the user's email
    csv_filename = f'{"_".join([part.title() for part in user_id.split("@")[0].split(".")])}_OktaAppAccess.csv'
    # Combine the directory and filename to create the full path
    full_path = os.path.join(export_dir, csv_filename)

    if not os.path.exists(export_dir):
        os.makedirs(export_dir)

    # Open the CSV file in write mode.
    with open(full_path, mode='w', newline='', encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)

        # Write the CSV header (field you want to include in the report)
        writer.writerow(["App Name", "App ID", "User Name", "User Email", "Assignment"])

        # Iterate through each app in the individual assignment apps list
        for app in user_apps:
            # Extract the relevant information from the app dictionary
            app_name = app.get('label', 'label not found')
            app_id = app.get("id", "app id not found")
            # last_updated = app.get("lastUpdated", "N/A")
            user_name = f'{" ".join([part.title() for part in user_id.split("@")[0].split(".")])}'
            user_email = f"{user_id}"
            # status = app.get("status", "N/A")
            # Write each row to the csv
            writer.writerow([app_name, app_id, user_name, user_email, 'Individual'])
        
        # Add group apps to the CSV
        print(f"Exporting group assigned apps...")  # Debugging line
        for group_id, group_data in group_apps.items():
            group_name = group_data["name"]
            groups_apps_list = group_data["apps"]

            # Iterate through each app in the group's assigned apps
            for app in groups_apps_list:
                # Check is app is active
                if app.get("status", "").upper() == "ACTIVE":
                    app_name = app["label"]
                    app_id = app.get("id", "N/A")
                    user_name = f'{" ".join([part.title() for part in user_id.split("@")[0].split(".")])}'
                    user_email = user_id
                
                    writer.writerow([app_name, app_id, user_name, user_email, group_name])

    
    print(f"CSV report for {user_id} generated successfully: {csv_filename}")


def main():
    api_token = okta_api_token()
    company_domain = okta_company_domain()
    user_id = input(f"Enter the user's email: ").strip().lower()
    user_apps = get_user_assigned_apps(api_token, company_domain, user_id)
    user_groups = get_user_groups(api_token, company_domain, user_id)

    group_apps = {}
    for group_id, group_name in user_groups:
        group_apps[group_id] = {
            "name": group_name, # Store the group name
            "apps": get_group_assigned_apps(api_token, company_domain, group_id)
        }
    
    export_to_csv(user_apps, user_id, group_apps)

if __name__ == "__main__":
    main()

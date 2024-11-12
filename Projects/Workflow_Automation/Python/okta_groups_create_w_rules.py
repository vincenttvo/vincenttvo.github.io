# Script to create okta groups using API

import requests
import subprocess
import pandas as pd
import json

# Function to retrieve the API key from 1Password vault. Can update to take hardcoded value instead of from 1Password vault
def okta_api_token():
    result = subprocess.run(
        ["op", "read", "op://Employee/Okta API Key/credential"],
        capture_output = True,
        text = True
    )
    # Extract and return the API key from the result
    okta_api_token = result.stdout.strip()
    return okta_api_token

# Function to retrieve the Okta company domain from 1Password vault. Can update to take hardcoded value instead of from 1Password vault
def okta_company_domain():
    result = subprocess.run(
        ["op", "read", "op://Employee/Okta API Key/username"],
        capture_output = True,
        text = True
    )
    okta_company_domain = result.stdout.strip()
    return okta_company_domain

# Set up headers
def set_headers(okta_api_token):
    # Set up headers
    headers = {
        "Authorization": f"SSWS {okta_api_token}",
        "Content-Type": "application/json"
    }
    return headers

# Function to auto generate group rule name
def generate_group_name(role_title):
    # Convert the title to lowercase and replace spaced with hypends
    group_name = f"role-{role_title
                         .replace(" ", "-")
                         .replace("&", "and")
                         .replace(",", "")
                         .replace("director", "dir")
                         .replace("manager", "mgr")
                         .lower()}"
    return group_name

# Function to auto generate group rule name
def generate_group_description(role_title):
    # Convert the title to lowercase and replace spaced with hypends
    group_description = f"This group assigns applications and access to the {role_title} role."
    return group_description

# Function to create a group
def create_group(okta_api_token, okta_company_domain, group_name, group_description):
    url = f"https://{okta_company_domain}/api/v1/groups"
    headers = set_headers(okta_api_token)

    search_url = f"https://{okta_company_domain}/api/v1/groups?q={group_name}"
    search_response = requests.get(search_url, headers=headers)
    #print(f"Searching for group {group_name}, Status Code: {search_response.status_code}") # Debugging print

    if search_response.status_code == 200:
        groups = search_response.json()
        for group in groups:
            if group["profile"]["name"] == group_name:
                print(f"Group {group_name} already exists.")
                return

    # Proceed to create group if it does not already exist.
    payload = {
        "profile": {
            "name": f"{group_name
                         .replace(" ", "-")
                         .replace("&", "and")
                         .replace(",", "")
                         .replace("director", "dir")
                         .replace("manager", "mgr")
                         .lower()}",
            "description": group_description
        }
    }
    #print(f"Creating group {group_name} with payload: {json.dumps(payload)}")  # Debugging print
    response = requests.post(url, headers=headers, json=payload)

    # Log the full response for debugging
    #print(f"Group creation response: {response.status_code} - {response.text}")

    if response.status_code == 200:
        print(f"Group {group_name} created successfully.")
        return response.json() # Return the created group details
    else:
        print(f"Failed to create group {group_name}: {response.status_code} - {response.text}")
        return None
    
# Function to create a dynamic group rule
def create_group_rule(okta_api_token, okta_company_domain, group_id, rule_name, condition_filter):
    url = f"https://{okta_company_domain}/api/v1/groups/rules"
    headers = set_headers(okta_api_token)

    payload = {
        "type": "group_rule",  # Make sure the type is set to "group_rule"
        "name": f"{rule_name
                    .replace(" ", "-")
                    .replace("&", "and")
                    .replace(",", "")
                    .replace("director", "dir")
                    .replace("manager", "mgr")
                    .lower()}",
        "conditions": {
            "expression": {  # Fix the expression placement
                "value": condition_filter,
                "type": "urn:okta:expression:1.0"
            }
        },
        "actions": {
            "assignUserToGroups": {  # Correct action for assigning users to groups
                "groupIds": [group_id]  # Use groupIds in an array
            }
        }
    }
    #print(f"Payload for group rule: {json.dumps(payload, indent=2)}")  # Print out the JSON payload to inspect
    #print(f"Creating group rule with filter: {condition_filter}") # Debugging print

    # Make the API request to create the rule
    response = requests.post(url, headers=headers, json=payload)

    # Log the full response for debugging
    #print(f"Group rule creation response: {response.status_code} - {response.text}")

    if response.status_code in [200, 201]:
        print(f"Group rule for {rule_name} created successfully.")
        rule = response.json()
        rule_id = rule["id"]
        print(f"Rule created with ID: {rule_id}")

        activate_url = f"https://{okta_company_domain}/api/v1/groups/rules/{rule_id}/lifecycle/activate"
        activate_response = requests.post(activate_url, headers=headers)

        if activate_response.status_code == 204:
            print(f"Successfully activated the group rule {rule_name}")
            return rule
        else:
            print(f"Failed to activate rule {rule_name}: {activate_response.status_code} - {activate_response.text}")
            return None
    else:
        print(f"Failed to create rule: {response.status_code} - {response.text}")
        return None
        
# Function to read the group data from a CSV file using pandas
def read_group_data(csv_file_path):
    df = pd.read_csv(csv_file_path)
    groups_to_create = []

    for _, row in df.iterrows():
        group = {
            "title": row["Title"],
        }
        groups_to_create.append(group) # Add the group dictionary to the list
    return groups_to_create # Return full list after all the rows are processed.

# Create all groups and associated rules
def create_multiple_groups_and_rules(okta_api_token, okta_company_domain, csv_file_path):
    groups_to_create = read_group_data(csv_file_path)

    for group in groups_to_create:
        role_title = group["title"]
        group_name = generate_group_name(role_title)
        group_description = generate_group_description(role_title)
        

        # Create group
        created_group = create_group(okta_api_token, okta_company_domain, group_name, group_description)

        if created_group:
            group_id = created_group.get("id")
            print(f"Created Group {group_name} with ID {group_id}") # Debugging print

            # Define the rule condition (e.g, filter by title)
            condition_filter = f"user.title==\"{role_title}\" OR user.title==\"{role_title} I\" OR user.title==\"{role_title} II\" OR user.title==\"{role_title} III\"" # Assuming users's title contains this title

            # Create the rule for the group
            rule_name = f"{group_name}"
            create_group_rule(okta_api_token, okta_company_domain, group_id, rule_name, condition_filter)
        else:
            print(f"Group {group_name} created, but no valid group ID found. Skipping rule creation.")

# Main function to call to create groups
def main():
    api_token = okta_api_token()
    company_domain = okta_company_domain()
    csv_file_path = ""
    create_multiple_groups_and_rules(api_token, company_domain, csv_file_path)

# Call main function
if __name__ == "__main__":
    main()
# This script is intended to reset an Okta users's MFA and remove an Okta user's groups 

import requests
import subprocess
import time

# Function to retrieve the API key from 1Password vault.
def okta_api_token():
    result = subprocess.run(
        ["op", "read", "op://op-path-to-vault-item"],
        capture_output = True,
        text = True
    )
    # Extract and return the API key from the result
    okta_api_token = result.stdout.strip()
    return okta_api_token

# Function to retrieve the Okta company domain from 1Password vault.
def okta_company_domain():
    result = subprocess.run(
        ["op", "read", "op://op-path-to-vault-item"],
        capture_output = True,
        text = True
    )
    okta_company_domain = result.stdout.strip()
    return okta_company_domain

# Function to set up headers
def set_headers(okta_api_token):

    headers = {
        "Authorization": f"SSWS {okta_api_token}",
        "Content-Type": "application/json"
    }
    return headers

# Function to handle rate limit responses from to many API requests against Okta and retry.
def handle_rate_limit(response):
    if response.status_code == 429: # Rate limit error
        retry_after = response.headers.get("X-Rate-Limit-Reset", "60")
        print(f"Rate limit exceeded. Retrying after {retry_after} seconds...")
        time.sleep(int(retry_after)) # Sleep before retrying
        return True
    return False # No retry needed

def get_user_id_by_email(okta_api_token, okta_company_domain, user_id):
    url = f"https://{okta_company_domain}/api/v1/users/{user_id}"
    headers = set_headers(okta_api_token)

    while True:
        try:
            response = requests.get(url, headers=headers)

            if handle_rate_limit(response):
                None

            if response.status_code == 200:
                user_data = response.json()
                return user_data['id'] # This is the unique id in Okta
            else:
                print(f'Error fetching user ID for {user_id}: {response.status_code}')

        except requests.exceptions.RequestException as e:
            print(f'Request failed: {e}. Retrying...')
            continue
        except Exception as e:
            print(f'Unexpected error occurred: {e}')
            break

def get_user_mfa_factors(okta_api_token, okta_company_domain, user_id):
    """
    Fetch the MFA factors for the user
    :param user_id: Okta User Email
    :return: List of MFA factors
    """
    url = f"https://{okta_company_domain}/api/v1/users/{user_id}/factors"
    headers = set_headers(okta_api_token)

    while True:
        try:
            response = requests.get(url, headers=headers)

            if handle_rate_limit(response):
                continue

            if response.status_code == 200:
                factors = response.json()
                factor_ids = [factor['id'] for factor in factors]
                return factor_ids
            else:
                print(f'Failed to get MFA factors for user {user_id}: {response.status_code}')
                return []
            
        except requests.exceptions.RequestException as e:
            print(f'Request failed: {e}. Retrying...')
            continue
        except Exception as e:
            print(f'Unexpected error occurred: {e}')
            break

def reset_user_mfa(okta_api_token, okta_company_domain, user_id, unique_user_id, factor_ids):
    """
    Reset all MFA factors for the user.
    :param factor_ids: List of the MFA factor IDs
    """
    headers = set_headers(okta_api_token)

    for factor_id in factor_ids:
        url = f"https://{okta_company_domain}/api/v1/users/{user_id}/lifecycle/reset_factors"

        while True:
            try:
                response = requests.post(url, headers=headers)

                if handle_rate_limit(response):
                    continue

                if response.status_code == 200:
                    print(f'Sucessfully reset MFA factor {factor_id} for user {user_id}.')
                    break
                else:
                    print(f'Failed to reset MFA factor {factor_id} for user {user_id}: {response.status_code}')
                    break

            except requests.exceptions.RequestException as e:
                print(f'Request failed: {e}. Retrying...')
                continue
            except Exception as e:
                print(f'Unexpected error occurred: {e}')
                break

def find_user_devices(okta_api_token, okta_company_domain, user_id, unique_user_id):
    """
    Find the Okta User's assigned devices
    :params user_id: User email or unique Okta user ID
    :return: List of devices
    """
    url = f"https://{okta_company_domain}/api/v1/users/{unique_user_id}/devices"
    headers = set_headers(okta_api_token)

    while True:
        try:
            response = requests.get(url, headers=headers)

            if handle_rate_limit(response):
                continue

            if response.status_code == 200:
                devices = response.json()
                print(f'Response data: {devices}"')

                if not devices: # Check if device list is empty
                    print(f'No devices found for the user {user_id}')
                    return []
                else:
                    # If devices are found, print and return their ids
                    device_ids = [device['device'].get('id') for device in devices]
                    print(f'Found {len(devices)} devices for the user {user_id}.')
                    return device_ids
            else:
                print(f'Failed to retrieve devices for user {user_id}: {response.status_code}')
                return []
        
        except requests.exceptions.RequestException as e:
            print(f'Request failed: {e}. Retrying...')
            continue
        except Exception as e:
            print(f'Unexpected error occurred while finding devices for user {user_id}: {e}')
            break

def deactivate_device(okta_api_token, okta_company_domain, user_id, device_ids):
    """
    Deactivate associated devices for the provided Okta User
    """
    url = f"https://{okta_company_domain}/api/v1/devices/{device_ids}/lifecycle/deactivate"
    headers = set_headers(okta_api_token)

    while True:
        try:
            response = requests.post(url, headers=headers)

            if handle_rate_limit(response):
                continue

            if response.status_code == 204:
                print(f'Successfully deactivated device {device_ids} for user {user_id}.')
                break
            else:
                print(f'Failed to deactiate device {device_ids} for user {user_id}.')
                break
        
        except requests.exceptions.RequestException as e:
            print(f'Request failed: {e}. Retrying...')
            continue
        except Exception as e:
            print(f'Unexpected error occurred while deactivating devices for user {user_id}: {e}')
            break

def delete_device(okta_api_token, okta_company_domain, user_id, device_ids):
    """
    Delete associated device
    """
    url = f"https://{okta_company_domain}/api/v1/devices/{device_ids}"
    headers = set_headers(okta_api_token)

    while True:
        try:
            response = requests.delete(url, headers=headers)

            if handle_rate_limit(response):
                continue

            if response.status_code == 204:
                print(f'Successfully delete device {device_ids} for user {user_id}.')
                break
            else:
                print(f'Failed to delete device {device_ids} for user {user_id}.')
                break
        
        except requests.exceptions.RequestException as e:
            print(f'Request failed: {e}. Retrying...')
            continue
        except Exception as e:
            print(f'Unexpected error occurred while deleting devices for user {user_id}: {e}')
            break

def remove_user_devices(okta_api_token, okta_company_domain, user_id, unique_user_id):
    """
    Delete and deactivate associated devices
    """
    try:
        # Step 1: Find the devices associated with the user
        devices = find_user_devices(okta_api_token, okta_company_domain, user_id, unique_user_id)

        # Step 2: Deactivate and delete each device
        if devices:
            for device in devices:
                # print(f'Device: {device}') # Debug check structure
                device_ids = device['device'].get('id') # safe extraction with get()
                if device_ids:
                    print(f'Deactivating and deleting device with ID: {device}')
                    deactivate_device(okta_api_token, okta_company_domain, user_id, device_ids)
                    delete_device(okta_api_token, okta_company_domain, user_id, device_ids)
                else:
                    print(f'No devices found for user {user_id}')

    except requests.exceptions.RequestException as e:
        print(f'Request failed: {e}. Retrying...')
    except Exception as e:
        print(f'Unexcepted error while trying to remove devices for user {user_id}: {e}')

def find_user_okta_groups(okta_api_token, okta_company_domain, user_id, unique_user_id):
    """
    Find the groups that belong to the Okta user
    :param user_id: The Okta user email
    :return: List of groups the user is a part of
    """
    url = f"https://{okta_company_domain}/api/v1/users/{unique_user_id}/groups"
    headers = set_headers(okta_api_token)

    while True:
        try:
            response = requests.get(url, headers=headers)

            if handle_rate_limit(response):
                continue

            if response.status_code == 200:
                groups = response.json()
                group_names = [group['profile']['name'] for group in groups]
                group_ids = [group['id'] for group in groups] # Store group ids to pass to remove function
                return group_ids, group_names
            else:
                print(f'Failed to get user groups: {response.status_code}')
                return [], []
        except requests.exceptions.RequestException as e:
            print(f'Request failed: {e}. Retrying...')
            continue
        except Exception as e:
            print(f'Unexpected error occurred: {e}')
            break

def remove_user_okta_groups(okta_api_token, okta_company_domain, user_id, unique_user_id, group_ids, group_names):
    """
    Removes the Okta groups from the listed ones from the find function
    """
    headers = set_headers(okta_api_token)

    for group_id, group_name in zip(group_ids, group_names):
        url = f"https://{okta_company_domain}/api/v1/groups/{group_id}/users/{unique_user_id}"

        if group_name == "Everyone":
            print(f'Skipping Okta default group "Everyone" for {user_id}')
            continue

        while True:
            try:
                response = requests.delete(url, headers=headers)

                if handle_rate_limit(response):
                    continue

                if response.status_code == 204:
                    print(f'Successfully removed user {user_id} from group {group_id} {group_name}.')
                    break
                elif response.status_code == 403:
                    print(f"Can't remove from user {user_id} from group {group_id} {group_name}")
                else:
                    print(f'Failed to remove user from group {group_id}: {response.status_code}')
                    break
            except requests.exceptions.RequestException as e:
                print(f'Request failed: {e}. Retrying...')
                continue
            except Exception as e:
                print(f'Unexpected error occurred: {e}')
                break

def check_user_status(okta_api_token, okta_company_domain, user_id, unique_user_id):
    """
    Check if user is active in Okta
    :param user_id: Okta user email
    :return: Boolean indicating whether the user is active
    """

    url = f"https://{okta_company_domain}/api/v1/users/{user_id}"
    headers = set_headers(okta_api_token)

    while True:
        try:
            response = requests.get(url, headers=headers)

            if handle_rate_limit(response):
                continue

            if response.status_code == 200:
                user_data = response.json()
                status = user_data.get('status', '') # Status can be "ACTIVE", "SUSPENDED", "LOCKED OUT", etc.
                if status in ['ACTIVE', 'SUSPENDED']:
                    return True
                else:
                    print(f'User {user_id} is not active (status: {status}). Skipping deactivation.')
                    return False
            else:
                print(f'Failed to get user status for {user_id}: {response.status_code}')
                return False
            
        except requests.exceptions.RequestException as e:
            print(f'Request failed: {e}. Retrying...')
            continue
        except Exception as e:
            print(f'Unexpected error occurred: {e}')
            break

def deactivate_okta_user(okta_api_token, okta_company_domain, user_id, unique_user_id):
    """
    Deactivate Okta User
    """
    url = f"https://{okta_company_domain}/api/v1/users/{user_id}/lifecycle/deactivate"
    headers = set_headers(okta_api_token)

    while True:
        try:
            response = requests.post(url, headers=headers)

            if handle_rate_limit(response):
                continue

            if response.status_code == 200:
                print(f'Successfully deactivated user {user_id}.')
                break
            else:
                print(f'Failed to deactivate user {user_id}: {response.status_code}')
                break
        
        except requests.exceptions.RequestException as e:
            print(f'Request failed: {e}. Retrying...')
            continue
        except Exception as e:
            print(f'Unexpected error occurred: {e}')
            break
    return


def main():
    # Get the Okta API key from 1Password
    api_token = okta_api_token()

    # Get Okta Company Domain from 1Password
    company_domain = okta_company_domain()

    user_id = input(f'Enter user email(s) here (separated by comma): ')

    user_ids = user_id.split(',')

    for user_id in user_ids:
        print(f'Processing user: {user_id}')
        # Find user Okta uniuqe user ID
        unique_user_id = get_user_id_by_email(api_token, company_domain, user_id)

        # Find user's mfa factor IDs
        factor_ids = get_user_mfa_factors(api_token, company_domain, unique_user_id)

        # Find the user's associated Okta devices
        user_devices = find_user_devices(api_token, company_domain, user_id, unique_user_id)

        # Find user groups
        group_ids, group_names = find_user_okta_groups(api_token, company_domain, user_id, unique_user_id)
        print(f'User {user_id} is part of the following groups: {group_names}')

        if factor_ids:
            # Only reset MFA if factors exist
            reset_user_mfa(api_token, company_domain, user_id, unique_user_id, factor_ids)
        else:
            print(f'No MFA factors found for the user {user_id}.')

        if user_devices:
            # Remove associated user devices
            remove_user_devices(api_token, company_domain, user_id, unique_user_id)
        else:
            print(f'No user devices found for user {user_id}.')

        if check_user_status(api_token, company_domain, user_id, unique_user_id): # Checking if user status returns True to "ACTIVE" or "SUSPENDED"
            deactivate_okta_user(api_token, company_domain, user_id, unique_user_id)
        else:
            print(f'User {user_id} is not active. Skipping deactivation.')

        if group_names:
            remove_user_okta_groups(api_token, company_domain, user_id, unique_user_id, group_ids, group_names)
        else:
            print(f'User {user_id} is not part of any groups.')

        print(f'Finished processing user {user_id}')

    # Call main function
if __name__ == "__main__":
    main()
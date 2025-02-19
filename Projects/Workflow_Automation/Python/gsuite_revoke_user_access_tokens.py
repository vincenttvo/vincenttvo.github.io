import requests
import os
import google.auth
import logging
import json
import subprocess
from google.oauth2 import service_account
from googleapiclient.discovery import build

def setup_logging(user_emails):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    user_emails = user_emails[0]
    log_file_name = f"{'_'.join([part.title() for part in user_emails.split('@')[0].split('.')]).lower().strip()}"
    log_file_path = f"/Users/vincentvo/Downloads/{log_file_name}_revoke_access_token_log.log"

    file_handler = logging.FileHandler(log_file_path)
    stream_handler = logging.StreamHandler()

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    return logger
    # # Configure logging
    # logging.basicConfig(
    #     level=logging.INFO,  # You can adjust the level to DEBUG, WARNING, ERROR as needed
    #     format='%(asctime)s - %(levelname)s - %(message)s',
    #     handlers=[
    #         logging.FileHandler({log_file_path}),  # Log to file
    #         logging.StreamHandler()  # Also log to console
    #     ]
    # )
    # logger = logging.getLogger()
    # return logger

# Authenticate using the Service Account
def authenticate_service_account(service_account_file, scopes, domain):
    # Use this following line if the file is uploaded to something like 1Password as a file and you need to read it
    service_account_info = json.loads(service_account_file)

    # Swap from_service_account_info to from_service_account_file and the passed in parameter to match if you are reading from a local file location found in the main function
    credentials = service_account.Credentials.from_service_account_info(
        service_account_info, scopes=scopes
    )
    # Delegate domain-wide authority (impersonate an admin user)
    credentials = credentials.with_subject(f"vincent.vo-sa@{domain}")
    directory_service = build("admin", "directory_v1", credentials=credentials)
    groupsettings_service = build("groupssettings", "v1", credentials=credentials)
    return directory_service, groupsettings_service

def read_service_account_file():
    result = subprocess.run(
        ["op", "read", "op://IT-PRIVILEGED-SECRETS/Google Suite API Key Service Account/quick-geography-441516-f2-c6b6a8fa8b17.json"],
        capture_output = True,
        text = True
        )
    service_account_file = result.stdout.strip()
    return service_account_file


def revoke_token(access_token, token_name, logger):
    url = "https://oauth2.googleapis.com/revoke"
    params = {"token": access_token}

    try:
        response = requests.post(url, params=params)

        if response.status_code == 200:
            logger.info(f"Token successfully revoked: {token_name}")
            print(f"Token successfully revoked {token_name}")
        else:
            logger.error(f"Failed to revoke token {token_name}: {response.status_code}, {response.text}")
            print(f" Failed to revoke token {token_name}: {response.status_code}, {response.text}")
    except Exception as e:
        logger.error(f"Error revoking token {token_name}: {e}")
        print(f"Error revoking token {token_name}: {e}")

def revoke_user_tokens(directory_service, user_emails, logger):
    try:
        # Get the list of OAuth 2 tokens for the user
        results = directory_service.users().tokens().list(userKey=user_emails).execute()
        tokens = results.get("items", [])

        if not tokens:
            logger.info(f"No tokens found for user {user_emails}")
            print(f"No tokens found for user {user_emails}")
            return
        
        # Loop through each token and revoke it
        for token in tokens:
            token_id = token["id"]
            client_id = token.get("clientId", "Unknown")
            token_name = token.get("name", "Unknown")
            logger.info(f"Revoking token with Client ID: {token_id}, Name: {token_name} for user {user_emails}")
            print(f"Revoking token with Client ID: {token_id} {token_name} for user {user_emails}")
            revoke_token(token["access_token"], token_name)
    except Exception as e:
        logger.error(f"An error occurred while revoking tokens for {user_emails}: {e}")
        print(f"An error occurred {e}")

def main():
    service_account_file = read_service_account_file()
    scopes = ["https://www.googleapis.com/auth/admin.directory.user"]
    domain = "measurabl.com"

    user_emails = input(f"Enter user email(s) here (separated by comma): ")
    # user_emails = ["genesa.alcantara@measurabl.com"]
    user_emails = [name.strip() for name in user_emails.split(',')]
    logger = setup_logging(user_emails)

    try:

        directory_service = authenticate_service_account(service_account_file, scopes, domain)
        
        for user in user_emails:
            revoke_user_tokens(directory_service, user, logger)
    except Exception as e:
        logger.error(f"Failed to complete the token revocation process: {e}")
        print(f"Failed to complete the token revocation process: {e}")

if __name__ == "__main__":
    main()


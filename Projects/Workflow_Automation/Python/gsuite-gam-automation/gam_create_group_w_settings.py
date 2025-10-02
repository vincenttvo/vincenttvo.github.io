# This GAM script is intended to create a Google group No reply inbox for forwaring former employee emails to and hide the groups from global directory

import subprocess
import time
from pydantic import EmailStr, field_validator, BaseModel, ValidationError


class EmailInput(BaseModel):
    email: EmailStr

    # Custom validator to check if the email ends with a specific domain
    @field_validator('email')
    def check_email_domain(cls, value):
        # Define the allowed domain e.g. @example.com
        allowed_domain = '@domain.com'

        # Check if the email ends with the allowed domain
        if not value.endswith(f'@domain.com'):
            raise ValueError(f'Email must end with @{allowed_domain}')
        return value

def gam_create_group(gam_path, env, group_name, group_email, group_description):
    gam_command = [
        f'{gam_path}/gam',
        'create',
        'group',
        group_email,
        'name',
        group_name,
        'description',
        group_description
    ]


    try:
        result = subprocess.run(
            gam_command,
            capture_output = True,
            text = True,
            env = env
            # shell = True # this is only needed when command is a single line string
        )
        # print("stdout:", result.stdout)
        # print("stderr:", result.stderr)

        if result.stderr:
            return f"Error: {result.stderr.strip()}"
        
        return result.stdout.strip()
    
    except FileNotFoundError as e:
        return f'Error: Command not found - {e}'
    
    except subprocess.CalledProcessError as e:
        return f'Error: A subprocess error occurred - {e}'
    
    except Exception as e:
        return f'An unexpected error occurred: {e}'

def gam_apply_settings(gam_path, env, group_email, settings=None):
    # Default setings if no custom settings are passed
    if settings is None:
        settings = {
            "whoCanDiscoverGroup": "ALL_MEMBERS_CAN_DISCOVER",
            "whoCanViewGroup": "ALL_MEMBERS_CAN_VIEW",
            "whoCanViewMembership": "ALL_MEMBERS_CAN_VIEW", # ALL_IN_DOMAIN_CAN_VIEW
            "whoCanContactOwner": "ALL_MEMBERS_CAN_CONTACT",
            "whoCanJoin": "INVITED_CAN_JOIN",
            "archiveOnly": "false",
            "whoCanPostMessage": "ANYONE_CAN_POST", # NONE_CAN_POST and archiveOnly needs to be True to do this, ALL_IN_DOMAIN_CAN_POST
            "allowWebPosting": "false",
            "showInGroupDirectory": "false",
            "includeInGlobalAddressList": "false",
            "allowExternalMembers": "false"
        }

    gam_command = [
        f'{gam_path}/gam',
        'update',
        'group',
        group_email
    ]


    # Add the value mapping settings dynamically to the command
    for setting, value in settings.items():
        gam_command.append(f'{setting}')
        gam_command.append(f'{value}')
        
    try:
        #print("Executing command:", " ".join(gam_command)) # Debugging print
        result = subprocess.run(
            gam_command,
            capture_output = True,
            text = True,
            env = env
        )

        # Print stdout and stderr for debugging
        # print("stdout:", result.stdout)
        # print("stderr:", result.stderr)

        if result.stderr:
            return f"Error: {result.stderr.strip()}"
        
        return result.stdout.strip()
    
    except FileNotFoundError as e:
        return f'Error: Command not found - {e}'
    
    except subprocess.CalledProcessError as e:
        return f'Error: A subprocess error occurred - {e}'
    
    except Exception as e:
        return f'An unexpected error occurred: {e}'

def main():
    gam_path = "/Users/vincentvo/bin/gamadv-xtd3"
    env = {'PATH': f'{gam_path}:{subprocess.getoutput("echo $PATH")}'}
    group_name = input(f"Enter name of group here (email of user(s)): ").strip()

    # Split the input by comma and turn into a list
    group_name = [name.strip() for name in group_name.split(',')]

    # Loop through each email in the list
    for group_name in group_name:
        try:
            group_name_input = EmailInput(email=group_name)
            group_name = group_name_input.email

            group_email = f"no-reply-{group_name.split('@')[0].replace('.', '-')}@{group_name.split('@')[1]}"
            group_description = f"no-reply inbox for {group_name}"

        except ValidationError as e:
            print(f'Invalid email {group_name} error {e}')
            continue

    print(f'Creating group: {group_email}')
    gam_create_group(gam_path, env, group_name, group_email, group_description)
    print(f'Successfully created group: {group_email}')

    time.sleep(10)

    custom_settings = {
        "whoCanDiscoverGroup": "ALL_MEMBERS_CAN_DISCOVER",
        "whoCanViewGroup": "ALL_MEMBERS_CAN_VIEW",
        "whoCanViewMembership": "ALL_MEMBERS_CAN_VIEW", # ALL_IN_DOMAIN_CAN_VIEW
        "whoCanContactOwner": "ALL_MEMBERS_CAN_CONTACT",
        "whoCanJoin": "INVITED_CAN_JOIN",
        "archiveOnly": "false",
        "whoCanPostMessage": "ANYONE_CAN_POST", # NONE_CAN_POST and archiveOnly needs to be True to do this, ALL_IN_DOMAIN_CAN_POST
        "allowWebPosting": "false",
        "showInGroupDirectory": "false",
        "includeInGlobalAddressList": "false",
        "allowExternalMembers": "false"
    }

    print(f'Applying custom settings...')
    gam_apply_settings(gam_path, env, group_email, custom_settings)
    print(f'Successfully applied settings.')

if __name__ == "__main__":
    main()

# *Okta Automation*

## Overview
Created Okta Scripts using Okta API to automate administrative tasks in Okta.

## Implementation Details
**Tools Used:** 
- Okta

**Scope:** 
- Automate manual actions using Okta API

## Challenges and Solutions
**Challenge:** 
- Automate manual reptitive tasks that IT needed to support such as creating new Okta groups for roles to provision access.

**Solution:** 
- Automated creating new role groups to support RBAC.
- Created a provisioned CSV for whena user leaves for evidence for audit.

**Conclusion**
- Implementing the use of Okta API into scripts, created automated repetitive tasks and reduced human error and time it took to create those Okta resources. Creating added efficiency from a minimal IT team.

## Link to Scripts

### Create Okta Groups
- This automated the creation of role groups that were used to support RBAC for the business while also creating the Okta Group rule that would assign users this group by their title.

[==**Create Okta Role Groups**==](https://github.com/vincenttvo/vincenttvo.github.io/blob/main/Projects/Workflow_Automation/Python/okta-autoamtion/okta_groups_create_w_rules.py)

### Copy Okta App Assignment
- This allowed for quick assignment of apps to roles in the Senior or Advanced levels of an existing role. To avoid lack of access for an application that role needed. Permissions not applied just app assignment.

[==**Copy Okta Apps**==](https://github.com/vincenttvo/vincenttvo.github.io/blob/main/Projects/Workflow_Automation/Python/okta-autoamtion/okta_assign_copied_apps_to_group.py)

### Create App Assignment CSV Report
- This script was intended to pull an active Okta user's current app assignments prior to deactivation as audit evidence showing their access.

[==**Generate Report for Okta App Assignment**==](https://github.com/vincenttvo/vincenttvo.github.io/blob/main/Projects/Workflow_Automation/Python/okta-autoamtion/okta_user_app_access_csv.py)


## Outcomes
- Reduced manual actions by 50%.
- Enabled efficient user access management.
- Created scalable solutions to be used again for future projects.
- Generated evidence for audits.
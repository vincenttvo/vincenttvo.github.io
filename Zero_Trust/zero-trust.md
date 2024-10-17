# RBAC Implementation with Okta

## Objective
Design and Implement Zero Trust models for the organization.

## Implementation Details
- **Tools Used** 
- Okta, Kandji
- **Scope** 
- Reduce unauthorized access, or set adaptaive MFA for access based on risk factors such as behavior, location, and device.

## Challenges and Solutions
- **Challenge** 
- Users were using unmonitored, managed, and non company devices to access company tools and data with no restrictions.

- **Solution** 
- Worked with stakeholders such as HR to get a list of acceptable work locations to create regional network policies to prevent users from logging in from unacceptable work locations. 
- Deployed Adaptive MFA for those that were approved to work temporarily. 
- Deployed Okta and Kandji Device trust onto devices to insist users to use their work machines. 
- Disabled the ability to use windows machine to log onto company systems.


## Screenshots
![Kandji and Okta Device Trust](Images_zero_trust/kandji-okta-device-trust.png)


## Outcomes
- Reduced unauthorized access by 50%
- Reduced login fatigue by 25%
- Installed more security within the business without reducing work productivity.

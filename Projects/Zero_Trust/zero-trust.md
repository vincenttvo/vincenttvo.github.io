# Zero Trust Policies and Models

## Objective
Design and Implement Zero Trust models for the organization.

## Implementation Details
**Tools Used:** 
- Okta, Kandji

**Scope:** 
- Reduce unauthorized access, or set adaptaive MFA for access based on risk factors such as behavior, location, and device.

## Challenges and Solutions
**Challenge:** 
- Users were using unmonitored, managed, and non company devices to access company tools and data with no restrictions.

**Solution:** 
- Worked with stakeholders such as HR to get a list of acceptable work locations to create regional network policies to prevent users from logging in from unacceptable work locations. 
- Deployed Adaptive MFA for those that were approved to work temporarily. 
- Deployed Okta and Kandji Device trust onto devices to insist users to use their work machines. 
- Disabled the ability to use windows machine to log onto company systems.

## Screenshots

### Zero Trust Configurations:

**Network Zones**
- Created network zones to allow access from trusted areas.

![Okta Network Zones](Images_Zero_Trust/okta-network-zones.png)

**Adaptive MFA Okta Policies**
- Created adaptive MFA policies based on user location, device, and role (ie. Employee, third-party, contractor)

![Okta Adaptive MFA Policies](Images_Zero_Trust/okta-adaptive-mfa-auth-policies.png)

**Configured Okta and Kandji to deploy certificate to endpoints to be managed devices using Okta Verify**
- This allowed devices to authenticate and verify they are in possession of the machine.

![Kandji and Okta Device Trust](Images_Zero_Trust/kandji-okta-device-trust.png)

![Kandji and Okta Device Trust Cont.](Images_Zero_Trust/kandji-okta-device-trust-2.png)

![Kandji and Okta Device Trust Cont.](Images_Zero_Trust/kandji-okta-device-trust-3.png)

## Outcomes
- Reduced unauthorized access by 50%
- Reduced login fatigue by 25%
- Installed more security within the business without reducing work productivity.

# Miscellaneous Notes
## Where to Edit User Profile
Click the avatar in the upper right corner, select `profile`. You can then `Edit Profile`, such as changing email or password.

## The Pods Page
This page is admin-only. It allows the administrator to get a WebShell with `root` privilege into any running pod, to avoid the hassles of SSH.

## The OAuth Page
In this page, you can add OAuth apps. `client_id` and `client_secret` will be generated automatically. The only fields you need to enter are app name and redirect uri. Only one redirect uri is supported on frontend, though the background supports multiple redirect uris. Moreover, all apps created using frontend is `shared` apps that can be used by all administrators. To create private apps, you need to use the Cloud Scheduler API server directly.
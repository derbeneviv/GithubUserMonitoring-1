GithubUserMonitoring
====================

This SW is to monitor public repos of your organization members for newly create or modified so that you can check those repos for company sensitive data.

Needed python 2.7, PyYAML lib (installed via pip), any SMTP server

usage:

    python repos.py -t <token> -m email1@mail.mail,email2@mail2.mail2,...

or

    python repos.py -t <token> -f /path/to/file

in file there should be a list of emails 1 per line


keys:
```
-h, --help: print this help
-t <token>, --token <token>: specify token
-d <dbname>, --database <dbname>: specify db name
-u <username>, --user <username>: specify db user
-p <password>, --password <password>: specify db pass
-H <hostname>, --hostname <hostname>: specify db host
-o <org1_name>,<org2_name>,... --org <org1_name>,<org2_name>,... : organization names
-m <email1,email2,...>, --mail <email1,email2,...>: specify emails to send notifications.
-c <filename>, --config <filename>: specify config .yml file
```
config file:  
```
token:  
db_name:  
db_username:  
db_password:  
db_host:  
org_names:  
    - org1
    - org2
emails:
    - email1
    - email2
```

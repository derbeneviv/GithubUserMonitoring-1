GithubUserMonitoring
====================

This SW is to monitor public repos of your organization members for newly create or modified so that you can check those repos for company sensitive data.

Needed python 2.7

usage:

    python repos.py -t <token> -m email1@mail.mail,email2@mail2.mail2,...

or  

    python repos.py -t <token> -f /path/to/file  

in file there should be a list of emails 1 per line


keys:

    -h, --help: print this help  
    -t <token>, --token <token>: specify token  
    -d <dbname>, --database <dbname>: specify db name  
    -u <username>, --user <username>: specify db user  
    -p <password>, --password <password>: specify db pass  
    -H <hostname>, --hostname <hostname>: specify db host  
    -o <org_name>, --org: organization name  
    -m <email1,email2,...>, --mail <email1,email2,...>: specify emails to send notifications. Conflicts with -f  
    -f <file>, --file <file>: specify file with emails. 1 address per line. Conflicts with -m"""


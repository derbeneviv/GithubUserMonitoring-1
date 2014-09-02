GithubUserMonitoring
====================

This SW is to monitor public repos of your organization members for newly create or modified so that you can check those repos for company sensitive data.

Needed python 2.7

usage:
python repos.py -t <token>

keys:

-h, --help: print this help
-t <token>, --token <token>: specify token
-d <dbname>, --database <dbname>: specify db name
-u <username>, --user <username>: specify db user
-p <password>, --password <password>: specify db pass
-H <hostname>, --hostname <hostname>: specify db host
-o <org_name>, --org: organization name
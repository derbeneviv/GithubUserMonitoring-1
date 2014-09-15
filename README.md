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
-d <dbname>, --database <dbname>: specify db name
-u <username>, --user <username>: specify db user
-p <password>, --password <password>: specify db pass
-H <hostname>, --hostname <hostname>: specify db host
-o <org1_name:token:email1,email2>;<org2_name:token:email3,email4>;... --org <org1_name:token:email1,email2>;<org2_name:email3,email4> : organization names and emails per organization
-M <hostname>, --mailhost <hostname>: specify SMTP hostname
-s <email>, --sender <email>: specify sender email
```
config file:  
```
db_name: public_repos.db
db_username: root
db_password: password
db_host: localhost
org:
  VerySwagOrg_Inc:
    token: tokentokentokentokentokentokentokentoken
    emails:
        - vasiliy_pupkin@veryswagorg.com
  AnotherGreatORG:
    token: t2okent2okent2okento2kento2kentok2ento2kentoken
    emails:
      - vasiliy_pupkin@anothergorg.com
sender: repo-bot@tech-corps.com
mailhost: localhost
```

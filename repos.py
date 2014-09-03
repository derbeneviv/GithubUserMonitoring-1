#! /usr/bin/python
#api
import json
import urllib2

#sqlite
import sqlite3

#options
import sys,getopt

#mail
import smtplib
from email.mime.text import MIMEText

#configfile
import yaml

def mail(message,recipient,subject,smtp_host,sender='repository_bot@tech-corps.com'):
	msg = MIMEText(message)
	msg['Subject'] = subject
	msg['From'] =sender
	msg['To'] = recipient
	try:
		s = smtplib.SMTP(smtp_host)
		s.sendmail(sender,recipient,msg.as_string())
		s.quit()
		log('e-mail notification sent to '+recipient)
	except smtplib.socket.error:
		print 'No connection to SMTP server'
		sys.exit(2)

def mailall(message,recipients,subject,smtp_host,sender='repository_bot@tech-corps.com'):
	for rec in recipients:
		mail(message,rec,subject,smtp_host,sender='repository_bot@tech-corps.com')

def log(log_string):
	print log_string

def log_and_send(logstring,msg):
	log(msg)
	logstring=logstring+'\n'+msg
	mailall(msg,recipients,subject,smtp_host,sender='repository_bot@tech-corps.com')

def init_db(host,user,password,db):
	
	try:
		con = sqlite3.connect(db)
		cursor = con.cursor()
	except sqlite3.Error, e:
		log("%s:" % e.args[0])
	log('creating tables...')
	try:
		sql = '''CREATE TABLE members(
			member_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
			login VARCHAR(100) UNIQUE NOT NULL)'''
		cursor.execute(sql)
		log ('table \'members\' created')
	except sqlite3.Error, e:
		log("%s:" % e.args[0])

	try:
		sql = '''CREATE TABLE repos(
			repo_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
			repo_name VARCHAR(100),
			owner_id INT,
			last_updated DATETIME)'''
		cursor.execute(sql)
		log('table \'repos\' created')
	except sqlite3.Error, e:
		log("%s:" % e.args[0])
	return con


def api_request(req_url, token, api_url='https://api.github.com'):
	url = api_url+req_url
	headers = {'Authorization':'token '+ token}
	req = urllib2.Request(url=url, headers=headers)
	try:
		response = urllib2.urlopen(req)
		return json.load(response)
	except urllib2.HTTPError as e:
		print e
		sys.exit(2)
	
def get_user_repos(username, token):
	full_res=api_request('/users/'+username+'/repos',token=token)
	res = {}
	for iterator in full_res:
		res.update({iterator['full_name']:[iterator['pushed_at'],iterator['html_url']]})
	return res

def get_org_users(org_name,token):
	full_res = api_request('/orgs/'+org_name+'/members',token=token)
	res=[]
	for iterator in full_res:
		res.append(iterator['login'])
	return res

def is_user_in_db(user, connect):
	sql = 'SELECT * FROM members where login = \''+user+'\''
	cursor=connect.cursor()
	cursor.execute(sql) 
	res = cursor.fetchall()
	if not res:
		return False
	return res[0][0]

def is_repo_in_db(userid,repo,connect):
	sql = 'SELECT * FROM repos where owner_id = \''+str(userid)+'\' AND repo_name = \''+repo+'\''
	cursor=connect.cursor()
        cursor.execute(sql)
	res = cursor.fetchall()
        if not res:
                return False
	return res[0][3]

def add_user_to_db(user, connect):
	try:
		log('Adding user '+user+' to DB...')
		cursor=connect.cursor()
		sql = '''INSERT INTO members (login) VALUES ('''+'\''+user+'\')'
		cursor.execute(sql)
		connect.commit()
		return is_user_in_db(user, connect)
	except:
		return False

def add_repo_to_db(userid,repo,last_updated,connect):
	log('Adding repo '+repo+' to DB...')
	cursor=connect.cursor()
	sql = """INSERT INTO repos (repo_name, owner_id, last_updated) VALUES (?,?,?);"""#, (repo,str(userid),last_updated)#+repo+','+str(userid)+','+last_updated+')'
	cursor.execute(sql, (repo,str(userid),last_updated))
 	connect.commit()

def update_date(userid,repo,date,connect):
	log('updating time...')
	cursor = connect.cursor()
	sql = "UPDATE repos SET last_updated = ? where owner_id = ? AND repo_name = ?"
	cursor.execute(sql, (date,str(userid),repo))
	connect.commit()
	

def main():
	host = 'localhost'
	user = 'root'
	password = 'password'
	db = 'public_repos.db'
	orgs = ['Tech-Corps']
	emails = []
	logstring = ''
	token = None
#	print sys.argv
	try: 
		opts, args = getopt.getopt(sys.argv[1:],"ht:d:u:p:H:o:m:f:c:",["help","token","database","user", "password","host","org","mail","file","config"])
	except getopt.GetoptError:
		print 'wrong options. Try -h for the whole list'
		sys.exit(2)
	#first, load config if exists
	for opt, arg in opts:
		if opt in ("-c","--config"):
			config_file = open(arg).read()
			data = yaml.load(config_file)
			if data['token']:
				token = data['token']
			if data['db_name']:
				db = data['db_name']
			if data['db_username']:
				user = data['db_username']
			if data['db_password']:
				password = data['db_password']
			if data['db_host']:
				db_host = data['db_host']
			if data['org_names']:
				orgs = data['org_names']
			if data['emails']:
				emails = data['emails']

	for opt, arg in opts:
		if opt in ("-h", "--help"):
			print """-h, --help: print this help
			-t <token>, --token <token>: specify token
			-d <dbname>, --database <dbname>: specify db name
			-u <username>, --user <username>: specify db user
			-p <password>, --password <password>: specify db pass
			-H <hostname>, --hostname <hostname>: specify db host
			-o <org1_name>,<org2_name>, --org <org1_name>,<org2_name> : organization names
			-m <email1,email2,...>, --mail <email1,email2,...>: specify emails to send notifications"""
			sys.exit()

		elif opt in ("-t", "--token"):
			token = arg
		elif opt in ("-d", "--database"):
			db = arg
		elif opt in ("-u", "--user"):
			user = arg
		elif opt in ("-p", "--password"):
			password = arg
		elif opt in ("-H", "--host"):
			host = arg
		elif opt in ("-o", "--org"):
			orgs.extend(arg.split(","))
		elif opt in ("-m","--mail"):
			emails.extend(arg.split(","))
			for email in emails:
				email = email.strip()

	if not token:
		print "token required! pass it with -t option"
		sys.exit(2)
	if not emails:
		print "emails required! pass it with -m option!"
		sys.exit(2)

	connect=init_db(host, user, password,db)
	for org in orgs:
		members = get_org_users(org,token)
		for user in members:
			userid =is_user_in_db(user, connect) 
			if not userid:
				log ('New User: '+user)
				userid = add_user_to_db(user,connect)
			repos = get_user_repos(user,token)
			for reponame, repo_items in repos.iteritems():
				repo_current_date = repo_items[0]
				repo_html = repo_items[1]
				repo_db_date = is_repo_in_db(userid,reponame,connect)
				if not repo_db_date:
					sending_msg = '['+repo_current_date+'] NEW REPOSITOIRY'+'\nowner: '+user+'\norg: '+org+'\nrepo name:'+ reponame+'\nrepo url: '+repo_html
					log(sending_msg)
					logstring = logstring + '\n'+ sending_msg
					add_repo_to_db(userid, reponame, repo_current_date, connect)

				elif repo_db_date != repo_current_date:
					sending_msg = '['+repo_current_date+']'+' REPOSITORY UPDATED:'+'\n'+'owner:'+ user+'\norg: '+org+'\nrepo name:'+ reponame+'\nrepo url: '+repo_html
					log(sending_msg)
					logstring = logstring + '\n'+ sending_msg
					update_date(userid,reponame,repo_current_date,connect)
	if logstring:
		mailall(logstring,emails,'repositories updated','localhost')
	connect.close()


if __name__ == '__main__':
#	mail('test msg','ivan.derbenev@tech-corps.com','test@test.te','subj','localhost')
	main()

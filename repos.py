#! /usr/bin/python
import json
import urllib2
import sqlite3
import sys,getopt

def log(log_string):
	print log_string

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
	#except MySQLdb.OperationalError:
	#	print 'table \'members\' already created'

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
	#except MySQLdb.OperationalError:
	#	print 'table \'repos\' already created'
	return con


def api_request(req_url, token, api_url='https://api.github.com'):
	url = api_url+req_url
	headers = {'Authorization':'token '+ token}
	req = urllib2.Request(url=url, headers=headers)
	response = urllib2.urlopen(req)
	return json.load(response)
	
def get_user_repos(username, token):
	full_res=api_request('/users/'+username+'/repos',token=token)
	res = {}
	for iterator in full_res:
		res.update({iterator['full_name']:iterator['pushed_at']})
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
	org = 'Tech-Corps'
	token = None
	print sys.argv
	try: 
		opts, args = getopt.getopt(sys.argv[1:],"ht:d:u:p:H:o:",["help","token","database","user", "password","host","org"])
	except getopt.GetoptError:
		print 'wrong options. Try -h for the whole list'
		sys.exit(2)
	for opt, arg in opts:
		if opt in ("-h", "--help"):
			print """-h, --help: print this help
			-t <token>, --token <token>: specify token
			-d <dbname>, --database <dbname>: specify db name
			-u <username>, --user <username>: specify db user
			-p <password>, --password <password>: specify db pass
			-H <hostname>, --hostname <hostname>: specify db host
			-o <org_name>, --org: organization name"""
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
			org = arg
	if not token:
		print "token required! pass it with -t option"
		sys.exit(2)
	connect=init_db(host, user, password,db)
	members = get_org_users(org,token)
	for user in members:
		userid =is_user_in_db(user, connect) 
		if not userid:
			log ('New User: '+user)
			userid = add_user_to_db(user,connect)
		repos = get_user_repos(user,token)
		for reponame, repo_current_date in repos.iteritems():
			repo_db_date = is_repo_in_db(userid,reponame,connect)
			if not repo_db_date:
				log('['+repo_current_date+'] NEW REPOSITOIRY')
				log ('owner:' +  user)
				log ('repo name:'+ reponame)
				add_repo_to_db(userid, reponame, repo_current_date, connect)
			elif repo_db_date != repo_current_date:
				log ('['+repo_current_date+']'+' REPOSITORY UPDATED:')
				log ('owner:'+ user)
				log ('repo name:'+ reponame)

				update_date(userid,reponame,repo_current_date,connect)
					
	connect.close()


if __name__ == '__main__':
	  main()
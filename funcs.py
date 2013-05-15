import glob
import os
import sys
import sqlite3
from smtplib import SMTP
from email.mime.text import MIMEText

from settings import *


def db_init(db_cache):
	if not os.path.exists(LOGMON_DB_PATH):
		con = sqlite3.connect(LOGMON_DB_PATH)
		con.execute('''create table log_stats (log_title text, position int, last_hash char(35))''')
	else:
		con = sqlite3.connect(LOGMON_DB_PATH)
	cur = con.cursor()
	cur.execute('select * from log_stats')
	for row in cur.fetchall():
		log_title = row[0]
		db_cache[log_title] = {}
		db_cache[log_title]['position'] = row[1]
		db_cache[log_title]['last_hash'] = row[2]
		db_cache[log_title]['new'] = False
	cur.close()
	con.close()


def db_update(db_cache):
	con = sqlite3.connect(LOGMON_DB_PATH)
	for key in db_cache:
		if db_cache[key]['new']:
			sql_query = 'insert into log_stats (log_title, position, last_hash) values ("%s",%d,"%s")' % (key
			, int(db_cache[key]['position']), db_cache[key]['last_hash'])
		else:
			sql_query = 'update log_stats set position=%d, last_hash="%s" where log_title="%s"' % (
			int(db_cache[key]['position']), db_cache[key]['last_hash'], key)
		con.execute(sql_query)

	con.commit()
	con.close()


def get_log_plugins():
	plug_list = []
	for fname in glob.glob(os.path.dirname(__file__) + "/configs/*.py"):
		if not fname.endswith('__init__.py'):
			plug_list.append(fname)
	return plug_list


def notify_user(log_title, parsed_log):
	if not parsed_log:
		return

	# typical values for text_subtype are plain, html, xml
	text_subtype = 'plain'

	content = """\
	Log %s
	%s
	""" % (log_title, parsed_log)

	try:
		msg = MIMEText(content, text_subtype)
		msg['Subject'] = "LogMon alert. Log %s " % log_title
		msg['From'] = SENDER_EMAIL

		conn = SMTP(SMTP_SERVER, SMTP_PORT)
		conn.starttls()
		conn.set_debuglevel(False)
		conn.login(SMTP_USERNAME, STMP_PASSWORD)
		try:
			conn.sendmail(SENDER_EMAIL, DESTINATION_EMAILS, msg.as_string())
		finally:
			conn.close()

	except Exception, e:
			sys.exit("Failed sending email. Error %s" % str(e))

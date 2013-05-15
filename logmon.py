#! /usr/local/bin/python
import os
import imp
import hashlib
from funcs import db_init, db_update, get_log_plugins, notify_user


db_cache = {}
db_init(db_cache)

for plugin in get_log_plugins():
	plugin_mod = imp.load_source(plugin[:-3], plugin)

	log_title = plugin_mod.Title
	log_fname = plugin_mod.LogFname
	log_max_seek = plugin_mod.MaxSeekToDiff
	try:
		fsize = os.path.getsize(plugin_mod.LogFname)
		old_data = ""

		with open(log_fname, 'rb') as fp:
			if log_title in db_cache:
				last_position = db_cache[log_title]['position']
				if last_position == fsize:
					continue  # file was not changed, switch to next one
				elif last_position > fsize:
					last_position = 0   # file became smaller than expected, rewind

				if fsize >= log_max_seek:   # file is too large, don't calculate old hash
					fp.seek(last_position)
				else:
					old_data = fp.read(last_position)
					if hashlib.md5(old_data).hexdigest() != db_cache[log_title]['last_hash']:
						fp.seek(0)  # file changed, rewind
			else:
				db_cache[log_title] = {}
				db_cache[log_title]['new'] = True
			new_log_data = fp.read()
			data_hash = hashlib.md5(old_data + new_log_data).hexdigest()

			db_cache[log_title]['position'] = fp.tell()
			db_cache[log_title]['last_hash'] = data_hash

		parsed_log = plugin_mod.log_parse(new_log_data)

	except os.error, e:
		parsed_log = 'Failed opening file %s for plugin %s' % (log_fname, log_title)

	notify_user(log_title, parsed_log)

db_update(db_cache)

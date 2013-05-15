Title = 'Log Title'
LogFname = '/log/path.log'
MaxSeekToDiff = 1024*1024 # set to 0 to parse th file from beginning everytime


def log_parse(log):
	import re

	log_data = re.findall("Traceback:([ \w]+)", log)
	if not len(log_data):
		return None

	return ';'.join(log_data)


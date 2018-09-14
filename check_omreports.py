#!/usr/bin/python

from os import walk
from smtplib import SMTP

def make_dict(data):
	d = {}
	for element in data:
		pair = element.split(' :')
		d.update({pair[0].strip() : pair[1].strip('\n').strip()})
	return d

def make_dict_rev(data):
	d = {}
	for element in data:
		pair = element.split(' :')
		d.update({pair[1].strip('\n').strip() : pair[0].strip()})
	return d

REPORT_DIR = '/data/monitoring/omsa_reports'

msg = ""

admin_emails = ['jrtaylor95@gmail.com']

critical_nodes = []
node_name = ''
msg_part = ''

for (dirpath, dirname, filename) in walk(REPORT_DIR):
	if filename:
		for (file) in filename:
			with open(dirpath + "/" + file, "r", 0) as fo:
				lines = fo.readlines()
				for i, line in enumerate(lines):
					if 'Critical' in line:
						if 'pdisk' in file:
							d = make_dict(lines[i-1:i+38])
							node_name = file[:-11]
							msg_part = '%s\n' % node_name
							for key in ['Name', 'Status', 'Failure Predicted']:
								msg_part += '\t%-20s\t%-20s\n' % (key, d[key])
						elif 'vdisk' in file:
							d = make_dict(lines[i-1:i+17])
							node_name = file[:-11]
							msg_part = '%s\n' % node_name
							for key in ['Name', 'Status' 'Device Name']:
								msg_part += '\t%-20s\t%-20s\n' % (key, d[key])
						else:
							d = make_dict_rev(lines[5:-3])
							node_name = file[:-4]
							msg_part = '%s\n' % node_name
							for k, v in d.items():
								if 'Critical' in v:
									msg_part += '\t%-20s\t%-20s\n' % (k, v)
						critical_nodes.append(node_name)
						msg += '%s\n' % msg_part 

if msg:
	critical_nodes = list(set(critical_nodes))

	from_addr = 'root@hepcms-hn.umd.edu'
	to_addr = ",".join(admin_emails)
	subject = "WARNING: Node(s) %s are critical" % " ".join(critical_nodes)
	
	header = "From: %s\nTo: %s\nSubject: %s\n" % (from_addr, to_addr, subject)
	email = header + msg
	print email
	#server = SMTP('localhost')
	#server.sendmail(from_addr, to_addr, email)
	#server.quit()


#!/usr/bin/env python

'''
This script checks the usage of /mnt/hadoop notifies admins when it is 80% full or more. NOTE: This script must be run as sudo. 
'''

#Import necessary modules
import subprocess
import smtplib

admins = ['jabeen@umd.edu', 'kakw@umd.edu', 'youngho.shin@cern.ch']

#Runs "df -h" and makes a list of the output
o1 = subprocess.Popen("df -h", stdout=subprocess.PIPE, shell=True)
o1_text = str(o1.communicate())
usage_list = o1_text.split(r"\n")
del usage_list[0]
del usage_list[-1]
for a in range(0, len(usage_list)):
  usage_list[a] = " ".join(usage_list[a].split())

#Cleans up output list by combining elements that should be on a single line and deleting duplicated elements
to_del = []
for b in range(0, len(usage_list)):
  if len(usage_list[b].split()) == 1 and len(usage_list[b+1].split()) == 5:
    usage_list[b+1] = usage_list[b] + " " + usage_list[b+1]
    to_del.append(b)
for c in range(0, len(to_del)):
  del usage_list[to_del[c]-c]
 
#Creates array out of output list 
usage_array = [["Filesystem", "Size", "Used", "Avail", "Use%", "Mounted on"]]
for d in range(0, len(usage_list)):
  usage_array.append(usage_list[d].split(" "))

#Creates list corresponding to data usage of /mnt/hadoop
hadoop_list = []
for e in range(0, len(usage_list)+1):
  if usage_array[e][5] == "/mnt/hadoop":
    hadoop_list = usage_array[e]

#print to_del
#print hadoop_list
#print usage_array


#Sends email to admins if /mnt/hadoop usage exceeds 80%
if hadoop_list != [] and int(hadoop_list[4].strip("%")) > 80:
  ohost = subprocess.Popen("hostname", stdout=subprocess.PIPE, shell=True)
  host = str(ohost.communicate())[2:-10]
  msg = "On " + host + ": \n" + "/mnt/hadoop is " + str(hadoop_list[4].strip("%")) + "% full. Please consider deleting or removing files."
  from_addr = 'root@hepcms-hn.umd.edu'
  to_addr = ", ".join(admins)
  subject = "WARNING: /mnt/hadoop usage is high"
  header = "From: %s\nTo: %s\nSubject: %s\n" % (from_addr, to_addr, subject)
  email = header + msg
  server = smtplib.SMTP('localhost')
  for addr in admins:
      server.sendmail(from_addr, addr, email)
  server.quit()


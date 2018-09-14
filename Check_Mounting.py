#!/usr/bin/env python

'''
This script checks if /home, /hadoop, /data, and /cvmfs are proplerly mounted on a node. If cvmfs is not mounted, 'ls \cvmfs' and 
'/data/osg/scripts/fixCVMFS.sh' are run to try to mount it. If any of these directories are not mounted, an email is sent to the admins. 
NOTE: This script must be run as sudo. 
'''

#Import necessary modules
import subprocess
import smtplib
import time

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

#Creates list corresponding to data usage
directory_list = ["/home", "/hadoop", "/data", "/cvmfs"]
directory_mounted = [0, 0, 0, 0]
for e in range(0, len(directory_list)):
  for f in range(0, len(usage_list)+1):
    if directory_list[e] in usage_array[f][5]:
      directory_mounted[e] = 1


#If cvmfs is not mounted, ls is run in an attempt to mount cvmfs, and df -h is used again to check if cvmfs has been mounted
if directory_mounted[3] == 0:
  o2 = subprocess.Popen("ls \cvmfs", stdout=subprocess.PIPE, shell=True)
  o3 = subprocess.Popen("df -h", stdout=subprocess.PIPE, shell=True)
  o3_text = str(o3.communicate())
  usage_list = o3_text.split(r"\n")
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
  #Checks if cvmfs has been mounted
  for h in range(0, len(usage_list)+1):
    if directory_list[3] in usage_array[h][5]:
      directory_mounted[3] = 1


#If cvmfs is still not mounted, /data/osg/scripts/fixCVMFS.sh is run in an attempt to mount cvmfs, and df -h is used again to check if cvmfs has been mounted
if directory_mounted[3] == 0:
  subprocess.call(['/data/osg/scripts/fixCVMFS.sh']) 
  #o2 = subprocess.Popen("/data/osg/scripts/fixCVMFS.sh", stdout=subprocess.PIPE, shell=True)
  time.sleep(30)
  o3 = subprocess.Popen("df -h", stdout=subprocess.PIPE, shell=True)
  o3_text = str(o3.communicate())
  usage_list = o3_text.split(r"\n")
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
  #Checks if cvmfs has been mounted
  for h in range(0, len(usage_list)+1):
    if directory_list[3] in usage_array[h][5]:
      directory_mounted[3] = 1


#Message compiled corresponding to unmounted storage devices
msg = ""
for i in range(0, len(directory_mounted)):
  if directory_mounted[i] == 0:
    msg = msg + directory_list[i] + " is not mounted properly. \n"



#Sends email to admins if any storage devices are not mounted properly
if msg != "" :
  ohost = subprocess.Popen("hostname", stdout=subprocess.PIPE, shell=True)
  host = str(ohost.communicate())[2:-10]
  msg = "On " + host + ": \n" + msg
  from_addr = 'root@hepcms-hn.umd.edu'
  to_addr = ", ".join(admins)
  subject = "WARNING: data directories are not properly mounted"
  header = "From: %s\nTo: %s\nSubject: %s\n" % (from_addr, to_addr, subject)
  email = header + msg
  server = smtplib.SMTP('localhost')
  for addr in admins:
      server.sendmail(from_addr, addr, email)
  server.quit()



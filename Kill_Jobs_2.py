#!/usr/bin/env python

'''
This script checks the CPU usage of jobs running on the cluster and kills those that have exceeded 70% CPU usage for 1 hour or more. It also warns the user by email about their intensive job for those exceeding 70% CPU usage for 20 minutes or more. NOTE: This script must be run as sudo. 
'''

#Import necessary modules
import subprocess
import time
import os 
import signal
import smtplib
from pwd import getpwuid


to_kill = []
notify = []
time_running = []
CPU_usage = []
admins = ['jabeen@umd.edu', 'kakw@umd.edu', 'youngho.shin@cern.ch']
send_to = []
user_email =  ""
o2_text = ""

#Runs commands multiple times to ensure no intensive processes are missed

for i in range(0, 6):

  #Runs ps and makes an array of the output
  
  o1_text = ""
  ps_list = []
  ps_array = []
  o1 = subprocess.Popen("ps -G users u --sort=-pcpu", stdout=subprocess.PIPE, shell=True)
  o1_text = str(o1.communicate())
  ps_list = o1_text.split(r"\n")
  del ps_list[0]
  del ps_list[-1]
  for c in range(0, len(ps_list)):
    ps_list[c] = " ".join(ps_list[c].split())
  ps_array = [["USER", "PID", "%CPU", "MEM", "VSZ", "RSS", "TTY", "STAT", "START", "TIME", "COMMAND"]]
  for d in range(0, len(ps_list)):
    ps_array.append(ps_list[d].split(" "))


  #Adds PID's to to_kill corresponding to jobs that are using > 70% CPU usage and have been running for 20 minutes or more.
  #The if statement below also checks that the job is not already in to_kill from a previous iteration.
  
  for f in range(1, len(ps_list)+1):
    if float(ps_array[f][2]) >= 70 and int(ps_array[f][9][:-3]) >= 20 and ps_array[f][1] not in to_kill:
      to_kill.append(ps_array[f][1])
      if ps_array[f][0].isdigit():
        notify.append(getpwuid(int(ps_array[f][0])).pw_name)
      else:
        notify.append(ps_array[f][0])
      CPU_usage.append(ps_array[f][2])
      time_running.append(ps_array[f][9])


  #Waits a few seconds in between each iteration
  if i < 5:
    time.sleep(2)


#Quits program if to_kill is empty (no intensive jobs being run); otherwise, it kills the jobs in to_kill running for times greater than 1 hour and emails admins and the users in the notify array.
if to_kill  == []:
  quit()
else:
  for g in range(0, len(to_kill)):
    #Used to obtain user's email if it is in hepcms_Users.csv
    o2 = subprocess.Popen("python /home/hon-martyn/scripts/cronscripts/parseUsers.py -m %s /home/hon-martyn/scripts/cronscripts/hepcms_Users.csv" % notify[g], stdout=subprocess.PIPE, shell=True) 
    o2_text = str(o2.communicate()) 
    #If the user's email is not in hepcms_Users.csv, the job is killed without notifying the user; otherwise, the user is notified.
    if "Unknown user" in o2_text:
      if int(time_running[g][:-3]) >= 60:
        o3 = subprocess.Popen("kill %s" % to_kill[g], stdout=subprocess.PIPE, shell=True)
    else:
      user_email = o2_text.split(r"\n")[-3]
      #If the job has been running for more than 1 hour, it is killed. Otherwise, the user is only emailed a warning.
      if int(time_running[g][:-3]) >= 60:
        o4 = subprocess.Popen("kill %s" % to_kill[g], stdout=subprocess.PIPE, shell=True)
        ohost1 = subprocess.Popen("hostname", stdout=subprocess.PIPE, shell=True)
        host = str(ohost1.communicate())[2:-10]
        msg = "Dear %s, \n \n You were running an intensive job on %s for an extended period of time. Due to cluster policies, this job has been terminated. Please consider using HTCondor to run this job, or contact Tier 3 for more information. Thank you. \n \n Statistics summary (user, job number, percent CPU usage, time running): \n " % (notify[g], host)
        msg += notify[g] + ", " + to_kill[g] + ", " + CPU_usage[g] + ", " + time_running[g] + "\n"
        admins = ['jabeen@umd.edu', 'kakw@umd.edu', 'youngho.shin@cern.ch']
        from_addr = 'root@hepcms-hn.umd.edu'
        to_addr1 = ", ".join(admins)
        to_addr1 = to_addr1 + ", " + user_email 
        send_to = admins
        send_to.append(user_email)
        subject = "Note about Intensive Job Being Run on Cluster"
        header = "From: %s\nTo: %s\nSubject: %s\n" % (from_addr, to_addr1, subject)
        email = header + msg
        server = smtplib.SMTP('localhost')
        for addr in send_to:
          server.sendmail(from_addr, addr, email)
        server.quit()
      else:
        ohost2 = subprocess.Popen("hostname", stdout=subprocess.PIPE, shell=True)
        host = str(ohost2.communicate())[2:-10]
        msg = "Dear %s, \n \n You are currently running an intensive job on %s. Due to cluster policies, this job will be terminated if it continues to run for more than 1 hour. You will receive two warning emails before termination. Please consider using HTCondor to run this job, or contact Tier 3 for more information. Thank you. \n \n Statistics summary (user, job number, percent CPU usage, time running): \n " % (notify[g], host)
        msg += notify[g] + ", " + to_kill[g] + ", " + CPU_usage[g] + ", " + time_running[g] + "\n"
        admins = ['jabeen@umd.edu', 'kakw@umd.edu', 'youngho.shin@cern.ch']
        from_addr = 'root@hepcms-hn.umd.edu'
        to_addr2 = ", ".join(admins)
        to_addr2 = to_addr2 + ", " + user_email 
        send_to = admins
        send_to.append(user_email)
        subject = "Note about Intensive Job Being Run on Cluster"
        header = "From: %s\nTo: %s\nSubject: %s\n" % (from_addr, to_addr2, subject)
        email = header + msg
        server = smtplib.SMTP('localhost')
        for addr in send_to:
          server.sendmail(from_addr, addr, email)
        server.quit()


#Separately emails admins about all intensive jobs
admins = ['jabeen@umd.edu', 'kakw@umd.edu', 'youngho.shin@cern.ch']
ohost3 = subprocess.Popen("hostname", stdout=subprocess.PIPE, shell=True)
host = str(ohost3.communicate())[2:-10]
msg = "Intensive jobs being run on " + host + " (user, job number, % CPU usage, time running): \n "
for g in range(0, len(to_kill)):
  msg += notify[g] + ", " + to_kill[g] + ", " + CPU_usage[g] + ", " + time_running[g] + "\n"
from_addr = 'root@hepcms-hn.umd.edu'
to_addr3 = ", ".join(admins)
subject = "WARNING: Intensive Jobs Being Run on Cluster"
header = "From: %s\nTo: %s\nSubject: %s\n" % (from_addr, to_addr3, subject)
email = header + msg
server = smtplib.SMTP('localhost')
for addr in admins:
  server.sendmail(from_addr, addr, email)
server.quit()

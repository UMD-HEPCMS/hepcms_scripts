#!/usr/bin/python
''' 
This script checks if Hadoop is running properly and emails admins if it is not. 
NOTE: This script must be run on a node where hadoop is set up (i.e. r510) and run by someone who has root access (i.e. sudo) for it to function properly. 
'''

#Import necessary modules
import smtplib
import subprocess
import os

#Set admins
admins = ['jabeen@umd.edu', 'kakw@umd.edu', 'youngho.shin@cern.ch']

#Runs command to check if hadoop is running properly; be sure to use full path to command in order for command to run properly in cron
o1 = subprocess.Popen("/sbin/service hadoop-hdfs-datanode status", stdout=subprocess.PIPE, shell=True)
o1_text = str(o1.communicate())

#Emails admins if hadoop is not running properly
if 'Hadoop datanode is running' not in o1_text:
  ohost = subprocess.Popen("hostname", stdout=subprocess.PIPE, shell=True)
  host = str(ohost.communicate())[2:-10]
  msg = "On " + host + ": \n Hadoop is not running properly. \' service hadoop-hdfs-datanode status \' did not return its expected output."
  from_addr = 'root@hepcms-hn.umd.edu'
  to_addr = ", ".join(admins)
  subject = "WARNING: Hadoop is not running properly."
  header = "From: %s\nTo: %s\nSubject: %s\n" % (from_addr, to_addr, subject)
  email = header + msg
  server = smtplib.SMTP('localhost')
  for addr in admins:
      server.sendmail(from_addr, addr, email)
  server.quit()



#!/usr/bin/env python

'''
parseUsers.py
v1.0
by Jeff Temple
April 6, 2012

Purpose:  Read a list of users from a csv file (from Marguerite"s initial Excel file), and identify them by name, user id, and email.
'''


import os,sys,string
import time
from optparse import OptionParser

class EmailInfo:
    ''' Stores name, email address, username, etc. for an individual user.'''

    def __init__(self,inputstring,debug=False):
        ''' Reads inputstring to get user info.'''
        self.inputstring=inputstring
        temp=string.split(inputstring,"\t")  # Break up string by commas (assumes comma-separated .csv input file)
        self.isValid=False # Assume string is not valid until all info read properly
        self.isAdmin=False # Assume not an admin until shown otherwise

        self.debug=debug
        # Default name, email variables
        self.email=None
        self.name=None
        self.dontbugEmail=None
        self.accountAge=-1  # account age in days
        self.inactiveAccount=False
        # Now try to read line
        okay=False
        freakyUser="daffyduck"  # replace "freakyUser" with name of particular user to check why a particular user in hepcms_Users.csv doesn't appear valid (for instance, mburr is invalid because he has a dontbugEmail, so we don't want him on our usual email lists).
        if freakyUser<>None and temp[0].find(freakyUser)>-1:
            okay=True
        try:
            self.username=string.replace(temp[0],'"','')
            self.group=string.replace(temp[1],'"','')
            self.name=string.replace(temp[2],'"','')
            self.email=string.replace(temp[3],'"','')
            self.dontbugEmail=string.replace(temp[4],'"','')  # should parse to use as email, but this email is explicitly set as "don't bug", so we don't want an auto script to use it
            self.extraInfo=temp[5]
            
            try:
                self.dateJoined=time.strptime(temp[6],"%m/%d/%y")
            except:
                self.dateJoined=time.strptime("01/01/99","%m/%d/%y")
            self.accountAge=time.mktime(time.localtime())-time.mktime(self.dateJoined)
            self.accountAge=self.accountAge/(3600*24)
            if (okay):print "uname:%s\tgroup:%s\tname:%s\temail:%s\tdbemail:%s\tStatus:%s\tDateJoined=%s\n"%(self.username, self.group, self.name, self.email, self.dontbugEmail, self.extraInfo,self.dateJoined)
            
            self.isAdminString=temp[7]
            self.isActiveString=string.strip(temp[8])
            if string.find(string.upper(temp[7]),"YES")>-1:
                self.isAdmin=True
            if string.find(string.upper(temp[8]),"YES")==-1:  # Must be specified as valid account in spreadsheet
                self.inactiveAccount=True
                if okay:print "USER INACTIVE! ",self.name, self.email, "TEMP = '%s'"%temp[8]
            self.isValid=True
            
            if len(self.email)==0 or len(self.dontbugEmail)>0:  # must have an email address to be a valid user!
                self.isValid=False
                if okay:print "No EMAIL",self.username
            if self.inactiveAccount==True:
                self.isValid=False
                if okay:print "INACTIVE",self.username
        except:
            self.isValid=False
            if self.debug:
                print "<EmailInfo::__init__> Error!  Could not parse line '%s'"%inputstring
        if self.email==None and self.dontbugEmail==None:
            # no contact info; assume invalid
            self.isValid=False
        return

    def Print(self):
        ''' Prints info about user.'''
        
        if self.isValid==False:
            if self.debug:
                print "<EmailInfo::Print>  Error!  Could not parse entry"
            return
        print "** User = %15s  **\nGroup = %10s \nName = %30s \ne-mail:%40s \nDate Joined: %9s \nInfo=%s \nAccount age (days) = %.2f"%(self.username,
                                                                                                                                       self.group,
                                                                                                                                       self.name,
                                                                                                                                       self.email,
                                                                                                                                       time.strftime("%m/%d/%y",self.dateJoined),
                                                                                                                                       self.extraInfo,
                                                                                                                                       self.accountAge)
        if (self.isAdmin):
            print "USER IS AN ADMIN!"
        print "%s"%("-"*50)
        return

    def PrintToFile(self):
        ''' prints user info as a string suitable for csv.'''
        mygroup=self.group

        if len(mygroup)<>0:
            mygroup='"%s"'%mygroup
        
        mystring="\"%s\"\t%s\t\"%s\"\t\"%s\"\t%s\t%s\t%s\t%s\t%s\n"%(self.username,
                                                                     mygroup,
                                                                     self.name,
                                                                     self.email,
                                                                     self.dontbugEmail,
                                                                     self.extraInfo,
                                                                     time.strftime("%m/%d/%y",self.dateJoined),
                                                                     self.isAdminString,
                                                                     self.isActiveString
                                                                     )
        return mystring


def ParseUsers(inputfile,debug=False):
    ''' Main program to take input file, and try to get user info from each line.'''
    userDict={}  # Dictionary of user information

    if not os.path.isfile(inputfile):
        if (debug):
            print "<ParseUsers>  Error!  Input file '%s' does not exist!"%inputfile
            return userDict
    lines=open(inputfile,'r').readlines()
    for l in lines:  # Go through all lines in file
        User=EmailInfo(l,debug=debug)
        if User.isValid:  # Add to dictionary if valid user
            userDict[User.username]=User
    return userDict

def PrintAll(userDict,debug=False):
    keys=userDict.keys()
    keys.sort()
    for k in keys:
        userDict[k].Print()
    print "\n Total identified users = %i\n"%len(keys)
    return

def PrintEmails(userDict,debug=False):
    keys=userDict.keys()
    keys.sort()
    for k in keys:
        if k==keys[-1]:
            print "%s"%userDict[k].email
        else:
            print "%s,"%userDict[k].email,
    return

def GetAdmins(userDict,verbose=False):
    keys=userDict.keys()
    keys.sort()
    admins=[]
    if verbose:
        print "Searching for T3 admins..."
    for k in keys:
        if userDict[k].isAdmin:
            admins.append(k)
            if verbose:
                userDict[k].Print()
    return admins

        
#######################################################

if __name__=="__main__":
    parser=OptionParser()
    parser.add_option("-d","--debug",
                      action="store_true",
                      dest="debug",
                      default=False,
                      help="If specified, print debug info.")
    parser.add_option("-e","--email",
                      action="store_true",
                      dest="email",
                      default=False,
                      help="If specified, print email of all users.")
    parser.add_option("-p","--print",
                      action="store_true",
                      default=False,
                      dest="Print",
                      help="If specified, print info about each user")
    parser.add_option("-a","--admins",
                      action="store_true",
                      default=False,
                      dest="admins",
                      help="If specified, print admins")
    parser.add_option("-u","--printuser",
                      action="append",
                      default=[],
                      dest="printUser",
                      help="If specified, only print info about particular username")

    parser.add_option("-m","--indivmail",
                      dest="indivmail",
                      default=[],
                      action="append",
                      help="Prints out email for individual users specified via -m <username>")
                      
    
    (opts,args)=parser.parse_args()

    fullUserDict={}
    if len(args)==0:
        if os.path.isfile("hepcms_Users.csv"):
            print "No input file supplied; using hepcms_Users.csv as default\n"
            args.append("hepcms_Users.csv")
        else:
            print "No input .csv file supplied!\n\n"
    for i in args:  # args should be input files; shouldn't need more than one, but allow for multiple files, just in case
        thisDict=ParseUsers(i,debug=opts.debug)
        for d in thisDict.keys():
            if d not in fullUserDict:
                fullUserDict[d]=thisDict[d]

    # Print individual users
    if len(opts.printUser)>0:
        userdict={}
        for i in opts.printUser:
            if i not in fullUserDict.keys():
                print "Error!  Have no info about username '%s'"%i
            else:
                userdict[i]=fullUserDict[i]
        PrintAll(userdict,opts.debug)
    # Print all users
    if opts.Print==True:
        PrintAll(fullUserDict,opts.debug)
    # Print email addresses only (for mass emailings)
    if opts.email==True:
        PrintEmails(fullUserDict,opts.debug)
    if len(opts.indivmail)>0:
        maillist=[]
        print "%15s\t%30s"%("UserName","Email")
        for i in opts.indivmail:
            if i in fullUserDict.keys():
                print "%15s\t%30s"%(i, fullUserDict[i].email)
                maillist.append(fullUserDict[i].email)
            else:
                print "Unknown user '%s'"%i
        if len(maillist)>0:
            print
            for i in maillist:
                if i<>maillist[-1]:
                    print "%s, "%i,
                else:
                    print "%s"%i
            print
    # Print only admins
    if opts.admins==True:
        admins=GetAdmins(fullUserDict,True)

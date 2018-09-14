#!/usr/bin/env python

#cleans cvmfs cache and temp scratch if they are almost full
import subprocess
import re
output = subprocess.Popen(['df', '-h'], stdout=subprocess.PIPE)
for line in iter(output.stdout.readline, ''):
	if "cvmfs" in line:
		percent = line.split()[4]
		percent = int(percent.strip("%"))
		if percent > 75:
			subprocess.call(["cvmfs_config", "wipecache"])
			break

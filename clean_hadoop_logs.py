#!/usr/bin/env python

#cleans cvmfs cache and temp scratch if they are almost full
import subprocess, socket, sys, getopt

def parse_args( argv ):
	try:
		opts, args = getopt.getopt(argv, 't:h', ['threshold=', 'help'])
	except getopt.GetoptError:
		print 'clean_hadoop_logs.py [options <argument>]\ntry clean_hadoop_logs.py -h | --help for more information'
		sys.exit(2)
	output = None
	for opt, arg in opts:
		if opt in ('-h', '--help'):
			print 'Usage: clean_hadoop_logs.py [options <argument>]\n\t-t, --threshold\tSet threshold for log deletion \n\t-h, --help\tDisplay help dialog'
			sys.exit(2)
		elif opt in ('-t', '--threshold'):
			output = arg
	return output

def main( argv ):
	arg = parse_args(argv)
	hostname = socket.gethostname()
	output = subprocess.Popen(['df', '-h'], stdout=subprocess.PIPE)

	if arg:
		threshold = arg
	else:
		threshold = 95
	for line in iter(output.stdout.readline, ''):
		if "scratch" in line:
			percent = line.split()[4]
			percent = int(percent.strip("%"))
			if percent > threshold:
				subprocess.call(['python', '/data/osg/scripts/pyCleanupHadoopLogs.py', '-k', '15', '-s', '$(' + hostname + ').log', '--dir', '/scratch/hadoop/hadoop-hdfs/'])
				break

if __name__ == "__main__":
	main(sys.argv[1:])

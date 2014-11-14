import os
import shutil
import sys
import re

image_pattern = re.compile("(.*)\.(jpg|png)$", re.I)
image_name_pattern = re.compile("([_A-Z0-9-]+\.jpg|png)", re.I)

if __name__ == '__main__':

	def logger(logfile, msg):
		"""
		"""
		if not logfile:
			logfile = log_file
		with open(logfile, 'a') as lg:
			lg.write(msg)

			
	threshold = 27
	if not os.path.isdir(sys.argv[-1]):
		print "python filter_traces.py /path/to/traces"
		sys.exit(1)
	
	data_dir = os.path.expanduser(sys.argv[-1])
	
	traces = [t for t in os.listdir(data_dir) if t.endswith("traced.txt")]
	images = [i for i in os.listdir(data_dir) if re.search(image_pattern, i)]
	
	if not traces:
		print "specified directory does not contain any traced.txt files"
		print "exiting..."
		sys.exit(1)	

	empty = []
	#make dir for problem traces...
	empty_dir = os.path.join(data_dir, "EMPTY")
	if not os.path.exists(empty_dir):
		os.mkdir(empty_dir)
	
	log_file = os.path.join(empty_dir, "missing_log")
	#initialize log file
	if not os.path.exists(log_file):
		open(log_file, 'w').close()

	for t in traces:
		t_path = os.path.join(data_dir, t)
		values = [l.strip().split('\t') for l in open(t_path,'r').readlines()]
		num_missing = len([l[0] for l in values if int(l[0]) == -1])
		if num_missing >= threshold:
			missing_msg = "num missing for {0}: {1}".format(t, num_missing)
			print missing_msg
			logger(log_file, missing_msg)
			empty.append(t)

	empty += [i for i in images if any(re.search(image_name_pattern, t).group(1) in i for t in empty)]

	for e in empty:
		src = os.path.join(data_dir, e)
		dst = os.path.join(empty_dir, e)
		shutil.move(src, dst)

	print "moved {0} problem files to {1}".format(len(empty), empty_dir)
import os
import shutil
import sys
import re

image_pattern = re.compile("(.*\.jpg|png)", re.I)


if __name__ == '__main__':
	try:
		bad_traces_dir = os.path.expanduser(sys.argv[1])
		corrected_traces_dir = os.path.expanduser(sys.argv[-1])
	except:
		print "\tpython move_traces.py <path/to/bad/traces> <path/to/corrected/traces>"
		sys.exit(1)
	if not os.path.exists(bad_traces_dir) or not os.path.exists(corrected_traces_dir):
		print "Problem with specified paths. Exiting..."
		sys.exit(1)
	print "bad traces dir: {0}".format(bad_traces_dir)
	print "corrected traces dir: {0}".format(corrected_traces_dir)
	bad_traces = [f for f in os.listdir(bad_traces_dir) if f.endswith("traced.txt") and any([re.search(image_pattern, corrected).group(1) in f for corrected in [trace for trace in os.listdir(corrected_traces_dir) if trace.endswith("traced.txt")]])]
	corrected_traces = [f for f in os.listdir(corrected_traces_dir) if f.endswith("traced.txt") and any([re.search(image_pattern, f).group(1) in b for b in bad_traces])]

	print "number of problem traces: {0}".format(len(bad_traces))
	print "number of corrected traces: {0}".format(len(corrected_traces))
		
	for b in bad_traces:
		os.remove(os.path.join(bad_traces_dir, b))
	print
	for corrected in corrected_traces:
		src = os.path.join(corrected_traces_dir, corrected)
		dst = os.path.join(bad_traces_dir, corrected)
		shutil.copy(src, dst)

	print "finished updating traces!"
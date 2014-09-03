import os
import shutil
import sys
import re

image_pattern = re.compile("(.*)\.(jpg|png)$", re.I)


if __name__ == '__main__':
	try:
		traces_dir = os.path.expanduser(sys.argv[1])
		images_dir = os.path.expanduser(sys.argv[-1])
	except:
		print "\tpython move_images.py <path/to/traces> <path/to/images>"
		sys.exit(1)
	if not os.path.isdir(traces_dir) or not os.path.isdir(images_dir):
		print "Problem with specified paths. Exiting..."
		sys.exit(1)
	print "traces_dir: {0}".format(traces_dir)
	print "images_dir: {0}".format(images_dir)
	traces = [f for f in os.listdir(traces_dir) if f.endswith("traced.txt")]
	images = [f for f in os.listdir(images_dir) if re.search(image_pattern, f)]
	to_move = []

	print "number of problem traces: {0}".format(len(traces))
	
	to_move += [im for im in images if any([re.search(image_pattern, im).group(1) in t for t in traces])]
	
	print "images to move: {0}".format(len(to_move))
	for im in to_move:
		src = os.path.join(images_dir, im)
		dst = os.path.join(traces_dir, im)
		if not os.path.exists(dst):
			shutil.copy(src, dst)
	print "images copied!"

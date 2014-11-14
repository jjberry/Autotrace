from PIL import Image
import os
import sys

dst = os.path.join(sys.argv[-1], "converted")
if not os.path.exists(dst):
	print "making output directory at {0}".format(dst)
	os.mkdir(dst)
for f in os.listdir(sys.argv[-1]):
	if f.endswith('jpg') or f.endswith('JPG'):
		source_name = os.path.join(sys.argv[-1], f)
		im = Image.open(source_name).convert("RGB")
		im.save(os.path.join(dst,f))
print "Mode conversion completed!"

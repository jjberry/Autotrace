"""
Author: Gus Hahn-Powell
converts png images to the jpg format used by autotrace
"""

import os
import Image
import sys
import shutil

if __name__ == '__main__':
	if not os.path.isdir(sys.argv[-1]):
		print "python png_to_jpg.py </path/to/png/images>"
		sys.exit(1)

	destination = os.path.expanduser(sys.argv[-1])
	png_files = [f for f in os.listdir(destination) if f.endswith("png")]
	to_rename = [f for f in os.listdir(destination) if "png" in f]
	
	if png_files:
		print "found {0} png files".format(len(png_files))
		print "converting png files to jpg..."

		for im in png_files:
			im_name = os.path.splitext(im)[0]
			img = Image.open(os.path.join(destination,im))
			img.save(os.path.join(destination, "{0}.jpg".format(im_name)), "JPEG")
			os.remove(os.path.join(destination, im))

		print "conversion completed!"

	if to_rename:
		print "renaming traces..."
		for f in to_rename:
			src = os.path.join(destination, f)
			dst = os.path.join(destination, f.replace('png', 'jpg'))
			shutil.move(src, dst)
		print "renaming complete!"
	else:
		print "nothing to rename..."
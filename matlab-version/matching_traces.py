import os
from random import sample
import shutil

def get_matching_traces(images, traces):
	return [t for t in t if any(i in t for i in images)]

def get_sample(images, n):
	return sample(images, n)

def move_files(files, dest):
	for f in files:
		s = os.path.join(os.getcwd(), f)
		d = os.path.join(os.getcwd(), dest, f)
		shutil.move(f)




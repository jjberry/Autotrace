import subprocess as sp
import re
import shlex
import urllib
import os
import sys

downloads_folder = os.path.join(os.path.expanduser("~"),"Downloads")
macports_src = None
macports_dst = os.path.join(downloads_folder, "macports_installer.pkg")

version_pattern = re.compile("([0-9.]+)")

#find Mac OSX version
version = sp.Popen("sw_vers", stdout=sp.PIPE, stderr=sp.PIPE)
out, _ = version.communicate()
version = out.split('\n')
version = re.search(version_pattern, version[1]).group(1)

def install_macports():
	"""
	Download appropriate version
	and open installer
	"""
	if version == "10.9":
		print "You're using Mavericks"
		macports_src = "https://distfiles.macports.org/MacPorts/MacPorts-2.2.1-10.9-Mavericks.pkg"

	elif version == "10.8":
		print "You're using Mountain Lion"
		macports_src = "https://distfiles.macports.org/MacPorts/MacPorts-2.2.1-10.8-MountainLion.pkg"

	elif version == "10.7":
		print "You're using Lion"
		macports_src = "https://distfiles.macports.org/MacPorts/MacPorts-2.2.1-10.7-Lion.pkg"

	elif version == "10.6":
		print "You're using Snow Leopard"
		macports_src = "https://distfiles.macports.org/MacPorts/MacPorts-2.2.1-10.6-SnowLeopard.pkg"

	else:
		print "Mac OSX version not recognized.\nAborting..."
		sys.exit()

	#urllib.request.urlretrieve(macports_src, macports_dst)
	f = urllib.urlopen(macports_src)
	with open(macports_dst, "wb") as pkgFile:
	    pkgFile.write(f.read())	

	#open macports installer...
	macports_installer = sp.Popen(shlex.split("open {pkg}".format(pkg=macports_dst)))
	macports_installer.wait()


def check_macports():
	"""
	Check to see if macport installed
	"""
	port_found, _ = sp.Popen(shlex.split("which port"), stdout=sp.PIPE, stderr=sp.PIPE).communicate()
	if not port_found:
		print "We need to install Macports...Let's see what system you're using..."
		install_macports()
	else:
		print "Macports already installed!"


#see if xcode tools installed
gcc_configured = sp.Popen(shlex.split("gcc --version"), stdout=sp.PIPE, stderr=sp.PIPE)
o, e = gcc_configured.communicate()
if "--prefix=/Applications/Xcode.app/Contents/Developer/usr" in e:
	print "XCode command line tools appear to be installed."

else:
	tools_install = sp.Popen(shlex.split("xcode-select --install"))
	tools_install.wait()

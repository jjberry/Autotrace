'''
Mac Autotrace Installer

This python2.7 script will automatically install all of the dependences to run
the AutoTrace software from the APIL (Arizona Phonological Imaging Lab) on
a macintosh computer.

Installs MacPorts and uses it to prepare the following dependencies:
python27
python-select
GTK
numpy
OpenCV
MatPlotLib
qt4

Also checks for matlab installation, but matlab is not required for installation
(though it is required to make AutoTrace run properly, ATM.)

Changes to be made:
qt stuff? (refer to the Autotrace readme)


possibly:
tk gui interface after install?


Needs Sudo!

By Gustave Powell and Trevor Sullivan

'''




import subprocess as sp
import re
import shlex
import urllib
import os
import sys
import time
import webbrowser
import Tkinter



class Installer(object):

	def __init__(self):
		self.user_home = os.path.expanduser("~/")
		self.user_name = self.user_home.split("/")[-2]
		self.profile_path = os.path.join(self.user_home,".bash_profile")
		self.github_path = os.path.join(self.user_home,"github/")

		self.downloads_folder = os.path.join(self.user_home, "Downloads/")
		self.macports_dst = os.path.join(self.downloads_folder, "macports_installer.pkg")

		self.version = self.check_OSX_version()

	def exit_on_error(self):
		print "Exiting..."
		sys.exit(1)

	def progress(self, process):
		while process.poll() is None:
			print ".",
			time.sleep(3)


	def prepare_installation(self):
		self.find_matlab()
		self.check_root()
		self.check_xcode()
		self.check_macports()

	def install(self):
		print "Updating macports database..."
		p = sp.Popen(shlex.split("sudo port selfupdate"), stdout=sp.PIPE, stderr=sp.PIPE)
		p = self.progress(p)

		print "Upgrading outdated ports..."
		o, e = sp.Popen(shlex.split("sudo port upgrade outdated"), stdout=sp.PIPE, stderr=sp.PIPE).communicate()
		self.check_python()
		self.check_qt4()
		self.check_gtk()
		self.check_numpy()
		self.check_cv()
		self.check_matplot()
		self.check_git()
		self.check_clone()
		self.set_crontab()
		print "Success!" #point user to ReadMe file or give URL to place on github (possibly even hyperlink?)
		#tk window that says something like "install complete, click here for more info"
		self.check_clone()
		self.set_crontab()
		self.after_install_gui()


	'''
	Check for matlab install and ask permission to continue
	'''
	def find_matlab(self):

		Applications_folder, _ = sp.Popen(["ls", "Applications"], stdout=sp.PIPE, stderr=sp.PIPE, ).communicate()
		matlab_installed = Applications_folder.find("MATLAB")
		if matlab_installed > 0:
			pass
		else:
			print "You don't seem to have MATLAB installed. Autotrace may not run properly without it."
			answer = raw_input("Would you like to continue with the installation anyway? (y/n) ").lower()
			if answer == "n":
				self.exit_on_error()
			elif answer == "y":
				return
			else:
				print "Try again"
				self.find_matlab()

	'''
	Checks for matlab version
	'''
	def check_matlab_version(self):
		out, err = sp.Popen(shlex.split("matlab -nosplash -nodesktop -r 'exit'"), stdout=sp.PIPE, stderr=sp.PIPE, ).communicate()
		if out:
			print "You've got MATLAB already with the proper license"
		if err:
			print "You do not have the proper MATLAB license.  Please check your install."

	def check_root(self):
		"""
		check if user has root priviliges
		"""
		o, e = sp.Popen(["groups"], stderr = sp.PIPE, stdout = sp.PIPE, shell = True).communicate()
		oa, e = sp.Popen(["whoami"], stderr = sp.PIPE, stdout = sp.PIPE, shell = True).communicate()

		if "admin" not in o:
			print "ERROR: You need administrative rights to complete the installation"
			self.exit_on_error()

	def check_OSX_version(self):
		#find Mac OSX version
		version_pattern = re.compile("([0-9.]+)")

		version = sp.Popen("sw_vers", stdout=sp.PIPE, stderr=sp.PIPE)
		out, _ = version.communicate()
		version = out.split('\n')
		version = re.search(version_pattern, version[1]).group(1)
		return version


	def install_macports(self):
		"""
		Download appropriate version
		and open installer
		"""

		#print "creating file: {0}".format(os.path.expanduser("~/.bash_profile"))

		if not os.path.exists(self.profile_path):
			print "bash_profile doesn't exist, creating it now"
			open(self.profile_path, "w").close()
			#sp.Popen(["sudo", "chown", "$USER", "~/.bash_profile"])
			o, e =sp.Popen(["sudo", "chmod", "777", self.profile_path], stderr=sp.PIPE, stdout=sp.PIPE).communicate()
			print "chmod out {0}".format(o)
			print "chmod err {0}".format(e)

		else:
			o, e = sp.Popen(["$PATH"], stderr=sp.PIPE, stdout=sp.PIPE, shell=True).communicate()
			sys_path = os.environ['PATH']

			if "/opt/local/bin" in sys_path and '/opt/local/sbin' in sys_path:
				print "PATH is correct"

			elif "/opt/local/bin" not in sys_path:
				newfile = open(self.profile_path, "a")
				newfile.write("\nexport PATH=/opt/local/bin:$PATH\n")
				newfile.close()

				os.environ['PATH'] = ":".join([sys_path, '/opt/local/bin'])
				sys_path = os.environ['PATH']

			elif "/opt/local/sbin" not in sys_path:
				newfile = open(self.profile_path, "a")
				newfile.write("\nexport PATH=/opt/local/sbin:$PATH\n")
				newfile.close()

				os.environ['PATH'] = ":".join([sys_path, '/opt/local/sbin'])
				sys_path = os.environ['PATH']

			else:
				print "adding to PATH"
				newfile = open(self.profile_path, "a")
				# gotta look up the code for this part
				newfile.write("\nexport PATH=/opt/local/bin:/opt/local/sbin:$PATH\n")
				newfile.close()

		o, e = sp.Popen(["sudo", "chmod", "777", self.profile_path], stderr=sp.PIPE, stdout=sp.PIPE).communicate()
		o, e = sp.Popen(["sudo", "chown", self.user_name, self.profile_path], stderr=sp.PIPE, stdout=sp.PIPE).communicate()

		if self.version.startswith("10.9"):
			print "You're using Mavericks\n"
			macports_src = "https://distfiles.macports.org/MacPorts/MacPorts-2.2.1-10.9-Mavericks.pkg"

		elif self.version.startswith("10.8"):
			print "You're using Mountain Lion\n"
			macports_src = "https://distfiles.macports.org/MacPorts/MacPorts-2.2.1-10.8-MountainLion.pkg"

		elif self.version.startswith("10.7"):
			print "You're using Lion\n"
			macports_src = "https://distfiles.macports.org/MacPorts/MacPorts-2.2.1-10.7-Lion.pkg"

		elif self.version.startswith("10.6"):
			print "You're using Snow Leopard\n"
			macports_src = "https://distfiles.macports.org/MacPorts/MacPorts-2.2.1-10.6-SnowLeopard.pkg"

		else:
			print "Mac OSX version not recognized."
			self.exit_on_error()

		#urllib.request.urlretrieve(macports_src, macports_dst)
		f = urllib.urlopen(macports_src)
		with open(self.macports_dst, "wb") as pkgFile:
		    pkgFile.write(f.read())

		#open macports installer...
		macports_installer = sp.Popen(shlex.split("open {pkg}".format(pkg=self.macports_dst)), stdout=sp.PIPE, stderr=sp.PIPE)
		print "follow the instructions in the installer"
		o, e = macports_installer.communicate()
		raw_input("Press Enter after finishing MacPorts install")
		#macports_installer.wait()
		self.install()


	def check_macports(self):
		"""
		Check to see if macport installed
		"""
		port_found, _ = sp.Popen(shlex.split("which port"), stdout=sp.PIPE, stderr=sp.PIPE).communicate()
		print port_found
		if not port_found:
			print "We need to install Macports...Let's see what system you're using..."
			self.install_macports()
		else:
			print "Macports already installed!"
			self.install()


	#see if xcode tools installed
	def check_xcode(self):
		p = sp.Popen(["pkgutil", "--pkg-info=com.apple.pkg.CLTools_Executables"], stdout=sp.PIPE, stderr=sp.PIPE)
		o, e = p.communicate()

		if "No receipt" in e:
			print "Xcode not installed"
			if self.version.startswith("10.9"):
				try:
					print "Installing XCode command line tools"
					o, e = sp.Popen(shlex.split("xcode-select --install"), stdout=sp.PIPE, stderr=sp.PIPE).communicate()
					raw_input("Press Enter after finishing Command Line Tools install")
				except:
					print "You need to install XCode tools! \n You'll find it in the app store."
					sys.exit()
			else:
				print "Please install XCode tools.  "
				print "1. Install 'XCode' from the app store"
				print "2. run Xcode"
				print "3. go to menu > preferences > downloads"
				print "4. select 'command line tools'"
				self.exit_on_error()

		else:
			print "Xcode installed"
		'''
		try:
			gcc_configured = sp.Popen(shlex.split("gcc --version"), stdout=sp.PIPE, stderr=sp.PIPE)
			o, e = gcc_configured.communicate()
			if "--prefix=/Applications/Xcode.app/Contents/Developer/usr" in e:
				print "XCode command line tools appear to be installed."
		except:
		'''

	def get_installed_list(self):
		port_installed, _ = sp.Popen(shlex.split("port installed"), stdout=sp.PIPE, stderr=sp.PIPE).communicate()
		return port_installed


	def check_python(self):
		'''
		Checks for python27 installation
		'''
		installed = self.get_installed_list()

		if re.search(".*python27 [@0-9._]+? \(active\)", installed):
			print "You have the correct version of Python installed (2.7)"
		else:
			print "You do not have the correct version of python installed.  Installing Python 2.7 using MacPorts"
			self.install_python()

	def install_python(self):
		p = sp.Popen(shlex.split("sudo port install python27"), stdout=sp.PIPE, stderr=sp.PIPE)
		self.progress(p)
		out, err = p.communicate()
		if not err:
			print out
			return
		else:
			print err
			print "Python 2.7 install failed. (port install python27)"
			self.exit_on_error()

		print "Setting python27 as system default..."
		o, e = sp.Popen("sudo port select --set python python27").communicate()

	def check_qt4(self):
		installed = self.get_installed_list()
		pos = installed.find('qt4-mac')

		if pos > 0:
			print "You have QT4 installed"
		else:
			print "You do not have qt4 installed.  Installing qt4 using MacPorts (this may take a while, be patient)"
			self.install_qt4()

	def install_qt4(self):
		p = sp.Popen(shlex.split("sudo port install qt4-mac"), stdout=sp.PIPE, stderr=sp.PIPE)
		while p.poll() is None:
			print ".",
			time.sleep(3)
		out, err = p.communicate()
		if not err:
			print out
			return
		else:
			print err
			print "qt4 install failed. (port install qt4-mac)"
			self.exit_on_error()

		print "Setting qt4 as system default..."
		o, e = sp.Popen("sudo port select --set qt4 qt4-mac").communicate()



	def check_gtk(self):
		'''
		checks for gtk installation, if not found, installs using methods below
		'''
		installed = self.get_installed_list()
		gtk_pos = installed.find('py27-pygtk ')
		gtk_doc_pos = installed.find('gtk-doc ')
		gtk2_pos = installed.find('gtk2 ')
		gtk3_pos = installed.find('gtk3 ')

		if gtk_pos > 0:
			print "pyGTK already installed!"
		else:
			print "Installing pyGTK using MacPorts"
			self.install_gtk()
		'''
		if gtk_doc_pos > 0:
			print "gtk-doc already installed!"
		else:
			print "Installing gtk-doc using MacPorts"
			self.install_gtkdoc()
		'''
		if gtk2_pos > 0:
			print "gtk2 already installed!"
		else:
			print "Installing gtk2 using MacPorts"
			self.install_gtk2()

		if gtk3_pos > 0:
			print "gtk3 already installed!"
		else:
			print "Installing gtk3 using MacPorts"
			self.install_gtk3()


	def install_gtk(self):
		p = sp.Popen(shlex.split("sudo port install py27-pygtk"), stdout=sp.PIPE, stderr=sp.PIPE)
		self.progress(p)
		output, err = p.communicate()

		if not err:
			return
		else:
			print "pygtk install failed. (port install py27-pygtk)"
			print err
			self.exit_on_error()

	def install_gtkdoc(self):
		p = sp.Popen(shlex.split("sudo port install gtk-doc"), stdout=sp.PIPE, stderr=sp.PIPE)
		self.progress(p)
		output, err = p.communicate()
		if not err:
			return
		else:
			print "gtk-doc install failed. (port install gtk-doc)"
			print err
			self.exit_on_error()

	def install_gtk2(self):
		p = sp.Popen(shlex.split("sudo port install gtk2"), stdout=sp.PIPE, stderr=sp.PIPE)
		self.progress(p)
		output, err = p.communicate()
		if not err:
			return
		else:
			print "gtk2 install failed. (port install gtk2)"
			print err
			self.exit_on_error()


	def install_gtk3(self):
		p = sp.Popen(shlex.split("sudo port install gtk3"), stdout=sp.PIPE, stderr=sp.PIPE)
		self.progress(p)
		output, err = p.communicate()
		if not err:
			return
		else:
			print "gtk3 install failed. (port install gtk3)"
			print err
			self.exit_on_error()


	def check_numpy(self):
		'''
		checks for numpy installation.  If not found, installs with methods below
		'''
		installed = self.get_installed_list()
		numpy_pos = installed.find("py27-numpy ")

		if numpy_pos > 0:
			print "Looks like we've got numpy already"
		else:
			print "Oh Noes! We need numpy.  Installing with MacPorts"
			self.install_numpy()


	def install_numpy(self):
		p = sp.Popen(shlex.split("sudo port install py27-numpy"), stdout=sp.PIPE, stderr=sp.PIPE)
		self.progress(p)
		output, err = p.communicate()
		if not err:
			return
		else:
			print "numpy install failed. (port install py27-numpy)"
			print err
			self.exit_on_error()

	def check_cv(self):
		'''
		take a guess
		'''
		installed = self.get_installed_list()
		opencv_pos = installed.find("opencv ")

		if opencv_pos > 0:
			print "OpenCV is here"
		else:
			print "OpenCV is missing, time for MacPorts"
			self.install_cv()

	def install_cv(self):
		p = sp.Popen(shlex.split("sudo port install opencv +qt4 +python27"), stdout=sp.PIPE, stderr=sp.PIPE)
		self.progress(p)
		output, err = p.communicate()
		if not err:
			return
		else:
			print "OpenCV install failed. (port install opencv)"
			print err
			self.exit_on_error()

	def check_matplot(self):
		'''
		yep
		'''
		installed = self.get_installed_list()
		matplot_pos = installed.find("matplotlib")

		if matplot_pos > 0:
			print "Looks like we've got matplotlib over here"
		else:
			print "matplotlib is missing, installing with MacPorts"
			self.install_matplot()

	def install_matplot(self):
		p = sp.Popen(shlex.split("sudo port install py27-matplotlib +gtk3 +gtk2 +qt4"), stdout=sp.PIPE, stderr=sp.PIPE)
		self.progress(p)
		output, err = p.communicate()
		if not err:
			return
		else:
			print "Matplotlib install failed. (port install py27-matplotlib)"
			print err
			self.exit_on_error()

	def check_git(self):
		installed = self.get_installed_list()
		matplot_pos = installed.find("git-core")

		if matplot_pos > 0:
			print "Looks like git is installed"
		else:
			print "git is missing, installing with MacPorts"
			self.install_git()

	def install_git(self):
		p = sp.Popen(shlex.split("sudo port install git-core"), stdout=sp.PIPE, stderr=sp.PIPE)
		self.progress(p)
		output, err = p.communicate()
		if not err:
			return
		else:
			print "Git install failed. (port install git-core)"
			print err
			self.exit_on_error()


#github stuff

	def check_clone(self):
		if not os.path.exists(self.github_path):
			print "github directory doesn't exist, creating it now"
			print self.github_path
			os.makedirs(self.github_path)
			o, e = sp.Popen(["sudo", "chmod", "777", self.github_path], stderr=sp.PIPE, stdout=sp.PIPE).communicate()
			o, e = sp.Popen(["sudo", "chown", self.user_name, self.github_path], stderr=sp.PIPE, stdout=sp.PIPE).communicate()

		if not os.path.exists(os.path.join(self.github_path, "old/")):
			print "Downloading Autotrace to ~/github/"
			self.clone_autotrace_repo()

		else:
			print "Looks like you have autotrace installed already"


	def clone_autotrace_repo(self):
		p = sp.Popen(["sudo git clone https://github.com/jjberry/Autotrace.git {0}".format(self.github_path)], stdout=sp.PIPE, stderr=sp.PIPE, shell=True)
		self.progress(p)
		o, e = p.communicate()
		print "git clone output"
		print o
		print "git clone error"
		print e

		# may be unnecessary.
		#if [failure because of non-empty repo]
		#	p = sp.Popen([shlex.split("rm -rf"), self.github_path], stderr=sp.PIPE, stdout=sp.PIPE)
		#	self.check_clone()

#updates

	def set_crontab(self):
		print "Creating UpdateAutotrace file in /usr/local"


		f = open("/usr/local/UpdateAutotrace", 'w')
		f.write('#!/bin/bash\
			\
			cd /Users/$USER/github\
			\
			sudo git pull') #This will overwrite whatever's already there, but it shouldn't matter because the file
							#won't change. If we want we can add an if statement so that this doesn't happen if the file
							#exists and has what we want in it.
		f.close()
		o, e = sp.Popen(["sudo", "chmod", "777", "/usr/local/UpdateAutotrace"], stderr=sp.PIPE, stdout=sp.PIPE).communicate()
		o, e = sp.Popen(["sudo", "chown", self.user_name, "/usr/local/UpdateAutotrace"], stderr=sp.PIPE, stdout=sp.PIPE).communicate()


		print "Creating crontab job to run the /usr/local/UpdateAutotrace script every Sunday and Thursday at noon"
		if not os.path.exists("/etc/crontab"):
			open("/etc/crontab", "w").close()

		with open('/etc/crontab', 'r+') as f:
			contents = f.read()
			if contents.find("automatically updates autotrace") > 0:
				print "crontab job already set"
			else:
				f.write("\n 0 12 * * 0,4 /usr/local/UpdateAutotrace #This script automatically updates autotrace \n\t\
					#on sundays and thursdays at noon\n")
			#f.write("\n * * * * * echo 'test' >> /Users/apiladmin/Downloads/test.txt") <- uncomment to test cron

		sp.Popen(["crontab", "/etc/crontab"]) #this refreshes crontab so that it starts counting


		'''
		This would work if we install the CronTab module, which would require some downloading, unpacking, and installing.
		I figure it's best to just change the file we want directly.

		try:
			from crontab import CronTab
		except:
			https://pypi.python.org/packages/source/p/python-crontab/python-crontab-1.7.2.tar.gz
			#unpack and cd into this archive
			sp.Popen(["sudo python setup.py install"], stderr=sp.PIPE, stdout=sp.PIPE)

			from crontab import CronTab
		cron = new CronTab()

		if cron.find_comment("automatically updates autotrace"):
			return
		else:
			job = cron.new(command=/usr/local/UpdateAutotrace, comment="This script automatically updates autotrace on sundays \
				and thursdays at noon")
			job.setall('0 12 * * 0,4')
		'''



	def after_install_gui(self):


		top = Tkinter.Tk()
		top.geometry('300x150')
		top.title("AutoTrace")

		label = Tkinter.Label(top, text = "Welcome to Autotrace!",
			font = 'Helvetica -18 bold')
		label.pack(fill=Tkinter.Y, expand=1)

		folder = Tkinter.Button(top, text='Click here to view Autotrace files',
			command = lambda: (os.system("open "+self.github_path)))
		folder.pack()

		readme = Tkinter.Button(top, text='ReadMe',
			command = lambda: (os.system("open "+os.path.join(self.github_path, "README.md"))), activeforeground ='blue',
			activebackground = 'green')
		readme.pack()

		apilsite = Tkinter.Button(top, text='Look here for more info on the project',
			command = lambda: (webbrowser.open("http://apil.arizona.edu")), activeforeground = 'purple',
			activebackground = 'orange')
		apilsite.pack()

		quit = Tkinter.Button(top, text='Quit',
			command=top.quit, activeforeground='red',
			activebackground='black')
		quit.pack()

		Tkinter.mainloop()


	def test_git(self):
		self.after_install_gui()
















if __name__ == '__main__':

	installer = Installer()

	installer.prepare_installation()

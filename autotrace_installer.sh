#! /usr/bin/bash

POOP=$(sw_vers | grep ProductVersion | awk '{print $2}')
MACPORTSMSG="\n\tLet's find the right version of Macports for your system..."
#echo $POOP;
#xcode-select --install
if type port >/dev/null 2>&1
	then
		echo "Macports already installed!"
	else
		if [ $POOP = "10.9" ]
			then
				echo -e "You're using Mavericks$MACPORTSMSG"
				curl -o ~/Downloads/macports_installer.pkg https://distfiles.macports.org/MacPorts/MacPorts-2.2.1-10.9-Mavericks.pkg
		elif [ $POOP = "10.8" ]
			thenex
				echo -e "You're using Mountain Lion$MACPORTSMSG"
				curl -o ~/Downloads/macports_installer.pkg https://distfiles.macports.org/MacPorts/MacPorts-2.2.1-10.8-MountainLion.pkg
		elif [ $POOP = "10.7" ]
			then
				echo -e "You're using Lion$MACPORTSMSG"
				curl -o ~/Downloads/macports_installer.pkg https://distfiles.macports.org/MacPorts/MacPorts-2.2.1-10.7-Lion.pkg
		elif [ $POOP = "10.6" ]
			then
				echo -e "You're using Snow Leopard$MACPORTSMSG"
				curl -o ~/Downloads/macports_installer.pkg https://distfiles.macports.org/MacPorts/MacPorts-2.2.1-10.6-SnowLeopard.pkg
		fi
		open ~/Downloads/macports_installer.pkg
fi

#update and upgrade macports
# sudo port -v selfupdate
# sudo port upgrade outdated

# packages=("R +accelerate+cairo+gfortran48+recommended+tcltk+tests+x11" "ImageMagick +x11" "tk +quartz" "python27 +universal" "py27-pil" "opencv +python27" "python_select" "py27-numpy +atlas" "py27-scipy" "py27-pygtk +x11" "py27-gnome" "glade3 +python27" "py27-gobject" "py27-matplotlib +gtk2 +latex +pyside +qt4 +tkinter")
# for package in "${packages[@]}"
# 	do
# 		echo "sudo port install ${package}"
# 		#sudo port install ${package}
# 	done

#use macport python
#sudo port select --set python python27

#find praat here: http://www.fon.hum.uva.nl/praat/download_mac.html


# 	if 
# 		then
# 			curl -o Downloads/Praat.dmg http://www.fon.hum.uva.nl/praat/praat5362_mac64.dmg
# 	fi
# 	if
# 		then
# 			curl -o Downloads/Praat.dmg http://www.fon.hum.uva.nl/praat/praat5361_mac32.dmg
# 	fi

# hdiutil attach -mountpoint ~/Downloads/Praat Praat.dmg
# hdiutil detach ~/Downloads/Praat
# mv Praat ~/Applications/Praat
#automating xcode install
#xcode-select --install &
#sleep 5
#xdotool key Tab Tab Return
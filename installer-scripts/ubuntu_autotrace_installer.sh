#! /usr/bin/env bash

##############
#
###############

# for everyone
sudo apt-get -y install git libopencv-dev python-opencv opencv-doc ipython python-gnome2-dev python-matplotlib python-scipy

# install Oracle JRE 8
# https://www.digitalocean.com/community/tutorials/how-to-install-java-on-ubuntu-with-apt-get
sudo apt-get -y install python-software-properties
# auto add the repo
sudo add-apt-repository -y ppa:webupd8team/java
sudo apt-get update
sudo apt-get -y install oracle-java8-installer

# clone AutoTrace TK into ~/github
mkdir ~/github
cd ~/github
git clone https://github.com/jjberry/Autotrace.git

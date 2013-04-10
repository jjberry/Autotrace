#!/usr/bin/env python

'''
watchdog.py
Written by Jeff Berry on Jan 11 2011

purpose:
    This script runs in the savefiles directory, waiting for 
    a new network.mat and meancdist.mat file to appear, and 
    renames them with a unique time, so they do not get overwritten
    by other instances of TrainNetwork.py
    
usage:
    python watchdog.py
'''

import os, subprocess, time

def watchdog():
    while True:
        if os.path.isfile('network.mat'):
            time.sleep(5)
            cmd = ['mv', 'network.mat', 'network'+str(time.time())+'.mat']
            p = subprocess.Popen(cmd)
            p.wait()
            
        elif os.path.isfile('meancdist.mat'):
            cmd = ['mv', 'meancdist.mat', 'meancdist'+str(time.time())+'.mat']
            p = subprocess.Popen(cmd)
            p.wait()
        
        else:
            time.sleep(5)

if __name__ == "__main__":
    watchdog()
        

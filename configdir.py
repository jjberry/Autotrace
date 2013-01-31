#!/usr/bin/env python

'''
configdir.py
Written by Jeff Berry on Jan 11 2011

purpose:
    This script arranges training data into the directory
    structure that TrainNetwork.py expects.

usage:
    python configdir.py
    
    This file should be placed in the directory with the .jpg
    and corresponding .traced.txt files, as well as ROI_config.txt.
    Running this script produces the directories Subject1/, traces/
    and Subject1/JPG/, as well as TongueContours.csv. ROI_config.txt
    is moved into Subject1/.
    
--------------------------------------------------
Modified by Jeff Berry on Feb 19 2011
reason:
    Added support for ROI_config.txt
'''

import os, subprocess

def formatAutoTrace():
    filename = 'Subject1/TongueContours.csv'
    o = open(filename, 'w')
    o.write("Filename\tRaw.R1.X\tRaw.R1.Y\tRaw.R2.X\tRaw.R2.Y\tRaw.R3.X\tRaw.R3.Y\tRaw.R4.X\tRaw.R4.Y\tRaw.R5.X\tRaw.R5.Y\tRaw.R6.X\tRaw.R6.Y\tRaw.R7.X\tRaw.R7.Y\tRaw.R8.X\tRaw.R8.Y\tRaw.R9.X\tRaw.R9.Y\tRaw.R10.X\tRaw.R10.Y\tRaw.R11.X\tRaw.R11.Y\tRaw.R12.X\tRaw.R12.Y\tRaw.R13.X\tRaw.R13.Y\tRaw.R14.X\tRaw.R14.Y\tRaw.R15.X\tRaw.R15.Y\tRaw.R16.X\tRaw.R16.Y\tRaw.R17.X\tRaw.R17.Y\tRaw.R18.X\tRaw.R18.Y\tRaw.R19.X\tRaw.R19.Y\tRaw.R20.X\tRaw.R20.Y\tRaw.R21.X\tRaw.R21.Y\tRaw.R22.X\tRaw.R22.Y\tRaw.R23.X\tRaw.R23.Y\tRaw.R24.X\tRaw.R24.Y\tRaw.R25.X\tRaw.R25.Y\tRaw.R26.X\tRaw.R26.Y\tRaw.R27.X\tRaw.R27.Y\tRaw.R28.X\tRaw.R28.Y\tRaw.R29.X\tRaw.R29.Y\tRaw.R30.X\tRaw.R30.Y\tRaw.R31.X\tRaw.R31.Y\tRaw.R32.X\tRaw.R32.Y\tUL.x\tUL.y\tUR.x\tUR.y\tLL.x\tLL.y\tLR.x\tLR.y\tAux1.x\tAux1.y\tAux2.x\tAux2.y\tAux3.x\tAux3.y\tAux4.x\tAux4.y\tAux5.x\tAux5.y\tAux6.x\tAux6.y\tAux7.x\tAux7.y\tAux8.x\tAux8.y\tAux9.x\tAux9.y\tAux10.x\tAux10.y\n")
    
    fnamesl = sorted(os.listdir('.'))
    fnames = []
    for i in fnamesl:
        if '.traced.txt' in i:
            fnames.append(i)
    warnings = 0    
    for i in fnames:
        f = open(i, 'r').readlines()
        if (len(f) != 32):
            print '\033[91m' + 'Warning: ' + i + ' does not have 32 lines\n\tThis will cause an error during training' + '\033[0m'
            warnings += 1
        nums = []
        for j in range(len(f)):
            x = f[j][:-1].split('\t')
            nums.append(int(round(float(x[1]))))
            nums.append(int(round(float(x[2]))))

        for k in range(8):
            nums.append(-1)

        for l in range(20):
            nums.append(-1)
        name = '.'.join(i.split('.')[0:2])
        #o.write('%s' % i[:-11])
        o.write('%s' % name)
        for k in nums:
        	o.write('\t%s' % k)
        o.write('\n')
    	    
    o.close()	
    
    if warnings > 0:
        print "There were %d warnings" % warnings
    
def configdir():
    if not os.path.isdir('Subject1'):
        os.makedirs('Subject1/JPG/')
        os.mkdir('traces')
	
    formatAutoTrace()

    tracecount = 0
    jpgcount = 0
    files = sorted(os.listdir('.'))
    for i in files:
        if '.traced.txt' in i:
            cmd = ['mv', i, 'traces']
            p = subprocess.Popen(cmd)
            p.wait()
            tracecount += 1
        elif '.jpg' in i:
            cmd = ['mv', i, 'Subject1/JPG']
            p = subprocess.Popen(cmd)
            p.wait()
            jpgcount += 1
	if os.path.isfile('ROI_config.txt'):
	    subprocess.Popen(['cp', 'ROI_config.txt', 'Subject1/'])
	if os.path.isfile('../ROI_config.txt'):
	    subprocess.Popen(['cp', '../ROI_config.txt', 'Subject1/'])
	    
    print "moved %d images and %d traces" % (jpgcount, tracecount)
    if jpgcount != tracecount:
        print '\033[91m' + 'Warning: There is a mismatch in number of images and number of traces' + '\033[0m'
	
if __name__ == "__main__":
    configdir()

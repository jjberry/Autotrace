#!/usr/bin/env python

'''
addheadcorr.py
written by Jeff Berry on Feb 17 2011

purpose:
    This script is designed to take the Palatoglossatron_Output.txt file resulting
    from the Export function in AutoTrace.py and add dot positions contained in 
    the file <headcorrfilename>, which is the output of Adam Baker's old Palatoglossatron.
    The resulting file will be called PG_addHC.txt, and is ready for peterotron.

usage:
    python addheadcorr.py <inputfile_from_old_school_palatoglossatron>
'''

import sys

def addheadcorr(headcorrfilename):
    hc = open(headcorrfilename, 'r').readlines()
    pg = open('Palatoglossatron_Output.txt','r').readlines()
    o = open('PG_addHC.txt', 'w')
    o.write(pg[0]) #header
    
    for i in range(1, len(hc)):
        h = hc[i].split('\t')
        t = pg[i].split('\t')
        o.write("%s\t%s\t%s" %(h[0], '\t'.join(t[1:65]), '\t'.join(h[65:]) ) )
    
    o.close()
    
if __name__ == "__main__":
    addheadcorr(sys.argv[1])

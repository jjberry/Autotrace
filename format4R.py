import re, os, sys
import pygtk
import gtk
import subprocess

def format4R(inputfile,outfile):
    f = open(inputfile,'r').readlines()
    output = open(outfile,'w')
	
    dic ={}
    for line in range(len(f)):
        x = f[line][:-1].split('\t')
        # find whether we have a full path attached
        if '/' in x[0]:
            y = x[0].split('/')
            z = y[-1]
        else:
            z = x[0]
        # find word and token number
        #m = re.match(r'(\D*)(\d*)_(.*)',z)
        #word = m.group(1)
        word = z.split('_')[0]
        if dic.has_key(word):
            dic[word] += 1
        else:
            dic[word] = 1
        tokenN = dic[word]
	
        # print the lines
        for i in range(1,64,2):
            output.write('%s\t%d\t%s\t%s\n' % (word,tokenN,x[i],x[i+1]))
		    
    output.close()
	
def cleanMissing(inputfile):
    f = open(inputfile,'r').readlines()
    output = open(inputfile,'w')

    warning = False
    #divide the thing into frames
    for i in range(0,len(f),32):

        # figure out the first frame that is not missing data
        index = []
        for j in range(32):
            x = f[i+j][:-1].split('\t')
            if eval(x[2]) > 0:
                index.append(j)
        try:
            st = index[0]

            # fix the missing points
            for k in range(32):
                y = f[i+k][:-1].split('\t')
                if k in index:
                    output.write(f[i+k])
                elif k < st:
                    output.write(f[i+st])
                else:
                    z = k
                    while z not in index:
                        z -= 1
                    output.write(f[i+z])
        except IndexError:
            warning = True         
            print "missing data in %s_%02d.jpg" % (inputfile[:-4], int(x[1]))

    if warning == True:
        md = gtk.MessageDialog(None, gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_WARNING,
            gtk.BUTTONS_CLOSE, "Warning: Some files are missing data\nThe sound file and linguagram will not be time aligned!\nSee the terminal window for affected images")
        md.run()
        md.destroy()
                
    output.close()
    return inputfile

def separate(inputfile):
    '''run this function to do the whole thing, taking the output from Peterotron as the input'''
    f = open(inputfile,'r').readlines()
    dic = {}
    for line in range(1,len(f)):
        x = f[line].split('_')
        if dic.has_key(x[0]):
            dic[x[0]] += 1
        else:
            dic[x[0]] = 1
    fnames = []
    for i in dic.keys():
        #os.system('grep %s %s > %s.txt' % (i,inputfile,i))
        cmd = ['grep', i, inputfile, ]
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        o = open(i+'.txt', 'w')
        o.write(p.communicate()[0])
        o.close()
        format4R(i+'.txt',i+'.csv')
        #os.system('rm %s.txt' % (i))
        subprocess.Popen(['rm', i+'.txt'])
        fname = cleanMissing(i+'.csv')
        fnames.append(fname)
    return fnames
	
if __name__ == "__main__":
    separate(sys.argv[1])
    
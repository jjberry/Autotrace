import pygtk
pygtk.require("2.0")
import gtk
import gtk.glade
import os, sys, subprocess
import gnomecanvas
import neutralContourSimple as ncs
#import numpy as np
#from matplotlib.figure import Figure
#from matplotlib.backends.backend_gtkagg import FigureCanvasGTKAgg as FigureCanvas


class AnalysisWindow:
    def __init__(self, csvlist):
        self.gladefile = "LinguaViewer.glade"
        self.wTree = gtk.glade.XML(self.gladefile, "analyze")
        self.window = self.wTree.get_widget("analyze")
        self.window.connect('destroy', self.onDestroy)
        self.window.set_title("Analysis")
        self.window.set_size_request(480, -1)
                
        self.comparisonVB = self.wTree.get_widget("vbox11")
        self.comparisonCB = gtk.combo_box_new_text()
        self.comparisonVB.add(self.comparisonCB)
        self.comparisonCB.connect('changed', self.onChangeComparison)

        # add new options here - append_text adds a new numerical option in the order the append takes place
        # see self.onChangeComparison
        # http://bytebaker.com/2008/11/03/switch-case-statement-in-python/
        self.options = {0: self.byLabel,
                        1: self.byWord,
                        2: self.WholeWord}
        self.comparisonCB.append_text("by label") #will use the labels to graph the data, i.e. l-tip vs. l-back
        self.comparisonCB.append_text("by filename") #will use the word names to graph the data, i.e. coli-tip vs. coli-back
        self.comparisonCB.append_text("by whole word")

        self.leftVbox = self.wTree.get_widget("vbox12")
        self.rightVbox = self.wTree.get_widget("vbox13")
        self.leftCbox = gtk.combo_box_new_text()
        self.leftVbox.add(self.leftCbox)
        self.rightCbox = gtk.combo_box_new_text()
        self.rightVbox.add(self.rightCbox)
        self.leftIND = 0 # this is to keep track of how many words we have listed in the left combobox
        self.rightIND = 0
        
        self.graphbutton = self.wTree.get_widget("button1")
        dic = { "on_button1_clicked" : self.onGraph,
                "on_tbSave2_clicked" : self.onSave}
        self.wTree.signal_autoconnect(dic)
        
        self.imageBox = self.wTree.get_widget("hbox8")
        self.image = gtk.Image()
        self.imageBox.add(self.image)

        self.parseCSV(csvlist)
        self.csvlist = csvlist
        self.comparisonCB.set_active(0) # sets tip vs. dorsum as default and triggers callback

        self.window.show_all()

    def getTvB(self, contours, backNum, tipNum, neutral):
    	'''backNum is the point on the contour from which to extract back peak value
    	   similarly, tipNum tells where to extract tip peak value
    	'''
    	t = ncs.NeutralTongue()
    	cx, cy = t.getNeutral(neutral)
    	cmags = t.makePolar(cx, cy)
    	X, Y = t.loadContours(contours)
    	M = t.batchConvert2Polar(X, Y)
    	D = t.batchGetMinD(M, cmags)
    	back = []
    	tip = []
    	for i in range(len(D)):
    		back.append(D[i][backNum-1])
    		tip.append(D[i][tipNum-1])

    	return back, tip

    def parseCSV(self, csvlist):
        '''This function takes the .csv.label.txt files and creates a results file called AW_ResultsFile.txt.
        This function calculates the LAG based on the label files. neutral.csv must be present in the same directory
        as the csv.label.txt and corresponding .csv files created by the Export function in AutoTrace.py for this to work.
        The results file can by used in R to do stats on the LAG measurement, and will be located in the same directory as 
        LinguaView.py.
        '''
        nolabel = 0
        noneutral = 0
        o = open('AW_ResultsFile.txt','w')
        o.write("token\tlag\tbackrow\ttiprow\tintstart\tintend\tbackpeak\ttippeak\tintlabel\n")
        for i in csvlist:
            if not os.path.isfile(i+'.label.txt'):
                nolabel += 1
                print "no label file found for %s" % i
            else:
                thispath = '/'.join(i.split('/')[:-1]) + '/'
                                
                if os.path.isfile(thispath + 'neutral.csv'):  
                    #parse the label file       
                    f = open(i+'.label.txt','r').readlines()
                    numFrames = int(f[1][:-1].split('\t')[1])  
                    dorsumline = int(f[2][:-1].split('\t')[1])
                    tipline = int(f[3][:-1].split('\t')[1])
                    intervals=[]
                    for j in range(5,len(f)):
                        line = f[j][:-1].split('\t')
                        if line[2] != '':
                            #find nearest frames for interval values
                            step = 465.0 / (numFrames - 1)
                            lowerframe = 0
                            int1 = float(line[0])
                            lowerbound = 75.0
                            while lowerbound <= int1:
                                lowerbound = 75.0 + step*lowerframe
                                lowerframe += 1
                            #subtract 1 for the last iteration and 1 to get the frame to the left    
                            lowerframe = lowerframe - 2 
                            
                            upperframe = 0
                            int2 = float(line[1])
                            upperbound = 75.0
                            while upperbound <= int2:
                                upperbound = 75.0 +step*upperframe
                                upperframe += 1
                            upperframe = upperframe - 1 # subtract 1 for the last iteration
                                
                            intervals.append([lowerframe, upperframe, line[2]]) 

                    back, tip = self.getTvB(i, dorsumline, tipline, thispath+'neutral.csv')
                    for k in range(len(intervals)):
                        lt = tip[intervals[k][0]:intervals[k][1]+1]
                        maxt = -1000
                        indt = -1
                        for l in range(len(lt)):
                            if lt[l] > maxt:
                                maxt = lt[l]
                                indt = l

                        lb = back[intervals[k][0]:intervals[k][1]+1]
                        maxb = -1000
                        indb = -1
                        for m in range(len(lb)):
                            if lb[m] > maxb:
                                maxb = lb[m]
                                indb = m

                        indt = intervals[k][0] + indt
                        indb = intervals[k][0] + indb
                        lag = indt - indb
                        o.write("%s\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%s\n" % (i, lag, dorsumline, tipline, intervals[k][0], intervals[k][1], indb, indt, intervals[k][2]))
                
                else:
                    noneutral += 1
                    print "neutral.csv not found for %s" % i
        o.close()        
        if nolabel > 0:
            md = gtk.MessageDialog(None, gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_WARNING,
                gtk.BUTTONS_CLOSE, "Warning: 1 or more words have not been labeled")
            md.run()
            md.destroy()
            
        if noneutral > 0:
            md = gtk.MessageDialog(None, gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_ERROR,
                gtk.BUTTONS_CLOSE, "Error: neutral.csv not found\nResults file not created")
            md.run()
            md.destroy()

    def onChangeComparison(self, event):
        '''Callback triggered when comparison combobox is changed'''
        self.clearBoxes()
        opt =  self.comparisonCB.get_active()        
        self.options[opt]()
        
    def byLabel(self):
        f = open('AW_ResultsFile.txt', 'r').readlines()
        o = open('AW_SSA_byLabel.txt', 'w')
        o.write('word\ttoken\tX\tY\n')
        
        tokenNums = {}
        tlist = []
        for i in range(1, len(f)):
            x = f[i][:-1].split('\t')
            backNum = int(x[2])
            tipNum = int(x[3])
            intstart = int(x[4])
            intend = int(x[5])
            thispath = '/'.join(x[0].split('/')[:-1]) + '/'
            back, tip = self.getTvB(x[0], backNum, tipNum, thispath+'neutral.csv')
            lt = tip[intstart:intend+1]
            lb = back[intstart:intend+1]
            if tokenNums.has_key(x[8]):
                tokenNums[x[8]] += 1
            else:
                tokenNums[x[8]] = 1
            for j in range(len(lt)):
                o.write('%stip\t%s\t%d\t%d\n' % (x[8], tokenNums[x[8]], j, -lt[j]))
                tokenname = x[8] + 'tip'
                if tokenname not in tlist:
                    tlist.append(tokenname)

            for j in range(len(lb)):
                o.write('%sback\t%s\t%d\t%d\n' % (x[8], tokenNums[x[8]], j, -lb[j]))
                tokenname = x[8] + 'back'
                if tokenname not in tlist:
                    tlist.append(tokenname)
    	o.close()
    	self.populateBox(tlist)
        
    def byWord(self):
        f = open('AW_ResultsFile.txt', 'r').readlines()
        o = open('AW_SSA_byWord.txt', 'w')
        o.write('word\ttoken\tX\tY\n')
        
        tlist = []
        for i in range(1, len(f)):
            x = f[i][:-1].split('\t')
            backNum = int(x[2])
            tipNum = int(x[3])
            intstart = int(x[4])
            intend = int(x[5])
            thispath = '/'.join(x[0].split('/')[:-1]) + '/'
            back, tip = self.getTvB(x[0], backNum, tipNum, thispath+'neutral.csv')
            lt = tip[intstart:intend+1]
            lb = back[intstart:intend+1]
            token = x[0].split('/')[-1][:-4] # cut off the path and use only the filename            
            for j in range(len(lt)):
                o.write('%stip\t%s\t%d\t%d\n' % (token[:-1], token[-1], j, -lt[j]))
                tokenname = token[:-1] + 'tip'
                if tokenname not in tlist:
                    tlist.append(tokenname)
                
            for j in range(len(lb)):
                o.write('%sback\t%s\t%d\t%d\n' % (token[:-1], token[-1], j, -lb[j]))
                tokenname = token[:-1] + 'back'
                if tokenname not in tlist:
                    tlist.append(tokenname)

    	o.close()
    	self.populateBox(tlist)
    	
    def WholeWord(self):
        o = open('AW_SSA_WholeWord.txt', 'w')
        o.write('word\ttoken\tX\tY\n')

        tlist = []
        for i in self.csvlist:
            thispath = '/'.join(i.split('/')[:-1]) + '/'
            if os.path.isfile(thispath + 'neutral.csv'):
                f = open(i+'.label.txt','r').readlines()
                fname = f[0][:-1].split('\t')[1]
                token = fname.split('/')[-1][:-4]
                numFrames = int(f[1][:-1].split('\t')[1])  
                dorsumline = int(f[2][:-1].split('\t')[1])
                tipline = int(f[3][:-1].split('\t')[1])
                intervals=[]
                for j in range(6, len(f)):
                    intervals.append( (((float(f[j].split('\t')[0])) - 75.0) / 465.0) * numFrames )
            
                back, tip = self.getTvB(i, dorsumline, tipline, thispath+'neutral.csv')
                for j in range(len(tip)):
                    o.write('%stip\t%s\t%d\t%d\n' % (token[:-1], token[-1], j, -tip[j]))
                    tokenname = token[:-1] + 'tip'
                    if tokenname not in tlist:
                        tlist.append(tokenname)

                for j in range(len(back)):
                    o.write('%sback\t%s\t%d\t%d\n' % (token[:-1], token[-1], j, -back[j]))
                    tokenname = token[:-1] + 'back'
                    if tokenname not in tlist:
                        tlist.append(tokenname)

        
        o.close()
    	self.populateBox(tlist)
        
    def populateBox(self, names):
        for i in names:
            self.leftCbox.append_text(i)
            self.leftIND += 1
            self.rightCbox.append_text(i)
            self.rightIND += 1
        
    def clearBoxes(self):
        if self.leftIND > 0:
            for i in range(self.leftIND):
                self.leftCbox.remove_text(i)
            self.leftCbox.append_text('')
            self.leftCbox.set_active(0)
            self.leftCbox.remove_text(0)
        if self.rightIND > 0:
            for i in range(self.rightIND):
                self.rightCbox.remove_text(i)
            self.rightCbox.append_text('')
            self.rightCbox.set_active(0)
            self.rightCbox.remove_text(0)
            
    def onGraph(self, event):
        ltext = self.leftCbox.get_active_text()
        rtext = self.rightCbox.get_active_text()
        if (ltext != None) and (rtext != None):
            graphdata = {0 : 'AW_SSA_byLabel.txt',
                        1 : 'AW_SSA_byWord.txt',
                        2 : 'AW_SSA_WholeWord.txt'}
            opt =  self.comparisonCB.get_active()
            if opt != 2:
                cmd = ['Rscript', '--vanilla', 'ssanova.R', ltext, rtext, graphdata[opt]]
                proc = subprocess.Popen(cmd)
                proc.wait()
                self.image.set_from_file('Current_Graph.png')
            else: 
                #let's plot with matplotlib so that we can put in the labels easily
                self.mplGraph(graphdata[opt], ltext, rtext)
     
    def mplGraph(self, datafile, plot1, plot2):
        '''This simply plots the data in datafile, and adds label data for plot1'''
        #get the label file
        p = open('AW_ResultsFile.txt', 'r').readlines()
        noMatch = True
        i = 1
        while (noMatch == True):
            x = p[i].split('\t')
            if 'tip' in plot1:
                stem = plot1[:-3]
            else:
                stem = plot1[:-4]
            if stem in x[0]:
                labelfilename = x[0]+'.label.txt'
                noMatch = False
            else:
                i += 1
        lf = open(labelfilename, 'r').readlines()
        nFrames = int(lf[1][:-1].split('\t')[1])
        cmd = ['Rscript', '--vanilla', 'ssanova.R', plot1, plot2, datafile]
        for i in range(6, len(lf)):
            val = float(lf[i].split('\t')[0])
            cmd.append(str(((val-75)/465.)*17))
        proc = subprocess.Popen(cmd)
        proc.wait()
        self.image.set_from_file('Current_Graph.png')
            
        
    def onSave(self, event):
        if os.path.isfile('Current_Graph.png'):
            fc = gtk.FileChooserDialog(title='Save Image File', parent=None, 
                action=gtk.FILE_CHOOSER_ACTION_SAVE, 
                buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, 
                gtk.STOCK_SAVE, gtk.RESPONSE_OK))
            g_directory = fc.get_current_folder() if fc.get_current_folder() else os.path.expanduser("~")
            fc.set_current_folder(g_directory)
            fc.set_default_response(gtk.RESPONSE_OK)
            fc.set_select_multiple(False)
            response = fc.run()
            if response == gtk.RESPONSE_OK:
                savename = fc.get_filename()
                g_directory = fc.get_current_folder()
                cmd = ['cp', 'Current_Graph.png', savename]
                proc = subprocess.Popen(cmd)
            fc.destroy()
        else:
            md = gtk.MessageDialog(None, gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_ERROR,
                gtk.BUTTONS_CLOSE, "Error: No Graph selected")
            md.run()
            md.destroy()

    def onDestroy(self, event):
        #gtk.main_quit()
        self.window.destroy()
 
if __name__ == "__main__":
    AnalysisWindow('junk')
    gtk.main()    
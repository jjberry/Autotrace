'''
 neutralContour.py
 Copyright (C) 2010 Jeff Berry

 This program is free software; you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation; either version 2 of the License, or
 (at your option) any later version.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with this program; if not, write to the Free Software
 Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
'''

import sys, os, math, subprocess
import LabelWindow
#import matplotlib.pylab as p
from numpy import *
from mpl_toolkits.mplot3d.axes3d import Axes3D
from matplotlib import cm
from matplotlib.figure import Figure
from matplotlib.backends.backend_gtkagg import FigureCanvasGTKAgg as FigureCanvas
from scipy.io.wavfile import read as wavread
import pygtk
pygtk.require("2.0")
import gtk
import gtk.glade
import gobject

class NeutralTongue:
	
    def __init__(self, contours, neutral, SHOW_LINGUAGRAM, SHOW_NEUTRAL, SHOW_WAVEFORM, SHOW_SPECTROGRAM):
        '''center points determined by transforming the point (426, 393) several times
           with peterotron, and taking the average.
        '''
        self.static_dir = os.getcwd() + '/'
        #self.centerX = 710
        #self.centerY = 638

        # these come from hand tuning to find the smallest range of y values of polar mags
        self.centerX = 665
        self.centerY = 525	

        self.gladefile = self.static_dir + "LinguaViewer.glade"
        self.wTree = gtk.glade.XML(self.gladefile, "window1")
        self.win = self.wTree.get_widget("window1")
        self.win.set_title(contours)
        self.title = contours

        self.mainVBox = self.wTree.get_widget("vbox1")

        dic = { "on_window1_destroy": self.onDestroy,
                "on_tbPlay_clicked" : self.playSound,
                "on_tbSave_clicked" : self.onSave,
                "on_tbLabel_clicked": self.onLabel}
        
        self.wTree.signal_autoconnect(dic)
        
        self.X, self.Y = self.loadContours(contours)
        self.wavname = contours[:-4] + ".wav"
        
        #Linguagram
        if (SHOW_LINGUAGRAM == True):
            x1 = array(self.X)
            y1 = array(self.Y)
            Z = []
            for i in range(len(self.X)):
                zs = []
                for j in range(32):
                    zs.append(i+1)
                Z.append(zs)
            z1 = array(Z)
            self.fig = Figure()
            canvas = FigureCanvas(self.fig)
            #ax = Axes3D(self.fig, rect=[-.23,-.2,1.447,1.4])        
            ax = self.fig.add_subplot(1, 1, 1, projection='3d')
            self.fig.subplots_adjust(left=-0.23, bottom=0, right=1.215, top=1)
            ax.mouse_init()
            surf = ax.plot_surface(z1, -x1, -y1, rstride=1, cstride=1, cmap=cm.jet)
            ax.view_init(90,-90)

            canvas.show()
            canvas.set_size_request(600, 200)
            self.mainVBox.pack_start(canvas, True, True)

        #Neutral
        if (SHOW_NEUTRAL == True):
            cx, cy = self.getNeutral(neutral)
            cmags = self.makePolar(cx, cy)
            M = self.batchConvert2Polar(self.X, self.Y)
            #D = self.batchGetMinD(M, cmags)    	
            fakeX = []
            for i in range(len(M)):
                xs = []
                for j in range(1,33):
                    xs.append(j)
                fakeX.append(xs)
			
            x1 = array(fakeX)
            y1 = array(M)
            Z = []
            for i in range(len(M)):
                zs = []
                for j in range(32):
                    zs.append(i)
                Z.append(zs)
            z1 = array(Z)

            self.fig3 = Figure()
            canvas3 = FigureCanvas(self.fig3)
            ax = self.fig3.add_subplot(1, 1, 1, projection='3d')
            self.fig3.subplots_adjust(left=-0.23, bottom=0, right=1.215, top=1)
            ax.mouse_init()
            ax.plot_surface(z1, -x1, y1, rstride=1, cstride=1, cmap=cm.jet)
            ax.view_init(90,-90)
                    
            canvas3.show()
            canvas3.set_size_request(600, 200)
            self.mainVBox.pack_start(canvas3, True, True)
		
        #Waveform
        windowsize = 0
        self.fig2 = Figure()
        canvas2 = FigureCanvas(self.fig2)
        if (SHOW_WAVEFORM == True):
            fs, snd = wavread(self.wavname)
            chan = snd[:,0]
            t=array(range(len(chan)))/float(fs);
            if SHOW_SPECTROGRAM == True:
        	    wavax = self.fig2.add_subplot(2, 1, 1)
            else:
        	    wavax = self.fig2.add_subplot(1, 1, 1)
            wavax.plot(t,chan,'black');
            wavax.set_xlim(0,max(t))
            windowsize += 200
        
        #Spectrogram
        if (SHOW_SPECTROGRAM == True):
            '''This calls Praat to get the spectrogram and adds it to the viewer'''
            specname = contours[:-4] + '.Spectrogram'
            cleanname = contours[:-4] + '.clean'
            cmd = ['/Applications/Praat.app/Contents/MacOS/Praat', self.static_dir + 'makeSpec.praat', self.wavname, specname]
            proc = subprocess.Popen(cmd)
            status = proc.wait()
            cmd2 = ['bash', self.static_dir + 'cleanspec.sh', specname, cleanname]
            proc2 = subprocess.Popen(cmd2)
            status2 = proc2.wait()
       
            f = open(cleanname, 'r').readlines()
            last = len(f)-1
            x = f[last].split('\t')
            rows = int(x[0])
            cols = int(x[1])

            img = zeros((rows, cols))
            
            for i in range(len(f)):
                x = f[i][:-1].split('\t')
                img[int(x[0])-1,int(x[1])-1] = float(x[2])

            img = log(img)
            if SHOW_WAVEFORM == True:
                specax = self.fig2.add_subplot(2, 1, 2)
            else:
                specax = self.fig2.add_subplot(1, 1, 1)
            specax.imshow(img, cmap=cm.gray_r, origin='lower', aspect='auto')
            windowsize += 200

        # show it
        if (SHOW_WAVEFORM == True) or (SHOW_SPECTROGRAM == True):
            canvas2.show()
            canvas2.set_size_request(600, windowsize)
            self.mainVBox.pack_start(canvas2, True, True)
            
        self.SHOW_LINGUAGRAM = SHOW_LINGUAGRAM
        self.SHOW_NEUTRAL = SHOW_NEUTRAL
        self.SHOW_WAVEFORM = SHOW_WAVEFORM
        self.SHOW_SPECTROGRAM = SHOW_SPECTROGRAM
        self.windowsize = windowsize
                        
    def playSound(self, event):
        cmd = ['/Applications/Praat.app/Contents/MacOS/Praat', self.static_dir + 'playSound.praat', self.wavname]
        proc = subprocess.Popen(cmd)
        status = proc.wait()
    	        
    def onSave(self, event):        
        fc = gtk.FileChooserDialog(title='Save Image File', parent=None, 
            action=gtk.FILE_CHOOSER_ACTION_SAVE, 
            buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, 
            gtk.STOCK_SAVE, gtk.RESPONSE_OK))
        g_directory = fc.get_current_folder()
        fc.set_current_folder(g_directory)
        fc.set_default_response(gtk.RESPONSE_OK)
        fc.set_select_multiple(False)
        response = fc.run()
        if response == gtk.RESPONSE_OK:
            savename = fc.get_filename()
            g_directory = fc.get_current_folder()
            self.saveNcrop(savename)
            
        fc.destroy()
        
    def saveNcrop(self, savename):
        if os.path.exists("tmp1.png"):
            p = subprocess.Popen(['rm', 'tmp1.png'])
            p.wait()
        if os.path.exists("tmp2.png"):
            p = subprocess.Popen(['rm', 'tmp2.png'])
            p.wait()
        if os.path.exists("tmp3.png"):
            p = subprocess.Popen(['rm', 'tmp3.png'])
            p.wait()
        if (self.SHOW_LINGUAGRAM == True):
            self.fig.savefig("tmp1.png", format="png", pad_inches=0)
            resize = ['convert', 'tmp1.png', '-resize', '800x250!', 'tmp1.png']
            p = subprocess.Popen(resize)
            p.wait()
            chop = ['convert', 'tmp1.png', '-gravity', 'South', '-chop', '0x40', 'tmp1.png']
            p = subprocess.Popen(chop)
            s = p.wait()
        if (self.SHOW_NEUTRAL == True):
            self.fig3.savefig("tmp2.png", format="png", pad_inches=0) 
            resize = ['convert', 'tmp2.png', '-resize', '800x250!', 'tmp2.png']
            p = subprocess.Popen(resize)
            p.wait()
            chop = ['convert', 'tmp2.png', '-gravity', 'South', '-chop', '0x40', 'tmp2.png']
            p = subprocess.Popen(chop)
            s = p.wait()   
            if (self.SHOW_LINGUAGRAM == True):
                chop = ['convert', 'tmp2.png', '-chop', '0x40', 'tmp2.png']
                p = subprocess.Popen(chop)
                s = p.wait()                                 
        if (self.SHOW_WAVEFORM == True) or (self.SHOW_SPECTROGRAM == True):
            self.fig2.savefig("tmp3.png", format="png", pad_inches=0)
            chop = ['convert', 'tmp3.png', '-chop', '0x40', 'tmp3.png']
            p = subprocess.Popen(chop)                                 
            s = p.wait()
        
        cmd = ['montage', 'tmp*.png', '-mode', 'Concatenate', '-tile', '1x', savename]
        proc = subprocess.Popen(cmd)
        status = proc.wait()
        
        cmd = ['convert', savename, '-resize', '600x', savename]
        proc = subprocess.Popen(cmd)
        status = proc.wait()
 
    def onLabel(self, event):
        self.saveNcrop('labelwindowbackground.png')
        self.win.destroy()
        #LabelWindow.LabelWindow('labelwindowbackground.png', self.title, len(self.X))
        LabelWindow.LabelWindow([self.title], self.SHOW_LINGUAGRAM, self.SHOW_NEUTRAL, self.SHOW_WAVEFORM, self.SHOW_SPECTROGRAM)
              
    def onDestroy(self, event):
        self.win.destroy()
    	
    def getNeutral(self, infile):
        '''Finds the neutral tongue by averaging the values of the neutral tongue
           traces. 
        '''
        f = open(infile, 'r').readlines()

        xaves = []
        yaves = []
        for i in range(1,33):
            for j in range(i,len(f),32):
                xs = []
                ys = []
                l = f[j][:-1].split('\t')
                xs.append(eval(l[2]))
                ys.append(eval(l[3]))
            xaves.append(sum(xs)/len(xs))
            yaves.append(sum(ys)/len(ys))
		
        return xaves, yaves
	
    def makePolar(self, ContourX, ContourY):
        mags = []
        for i in range(len(ContourX)):
            dist = math.sqrt((ContourX[i]-self.centerX)**2 + (ContourY[i]-self.centerY)**2)
            mags.append(dist)
        return mags
		
    def testPolar(self, x, y, cx, cy):
        '''Use this to find better center coords for polar transform.
        '''
        mags = []
        for i in range(len(x)):
            dist = math.sqrt((x[i]-cx)**2 + (y[i]-cy)**2)
            mags.append(dist)
        #p.plot(range(32), mags)
		
    def loadContours(self, infile):
        '''Opens a .csv file and returns contents as matrices of x and y vectors --
           1 column of the x matrix corresponds to 1 column of y matrix, to make a single
           frame.
        '''
        f = open(infile, 'r').readlines()
        X = []
        Y = []
        for i in range(0,len(f),32):
            xs = []
            ys = []
            for j in range(32):
                l = f[i+j][:-1].split('\t')
                xs.append(eval(l[2]))
                ys.append(eval(l[3]))
            X.append(xs)
            Y.append(ys)
        return X, Y

    def vertDist(self, Y1, Y2):
        ds = []
        for i in range(len(Y1)):
            ds.append(Y1[i]-Y2[i])
        return ds
		
    def subtractMinD(self, Contour):
        ds = []
        minD = 1000
        for i in range(len(Contour)):	
            if abs(Contour[i]) < minD:
                minD = abs(Contour[i])
        for j in range(len(Contour)):
            if Contour[j] < 0:
                ds.append(Contour[j]+minD)
            else:
                ds.append(Contour[j]-minD)
        return ds
		
    #def plotC(self, Contour):
    #    p.plot(range(len(Contour)), Contour)
		
    def batchConvert2Polar(self, X, Y):
        M = []
        for i in range(len(X)):
            M.append(self.makePolar(X[i],Y[i]))
        return M

    def batchGetMinD(self, M, center):
        D = []
        for i in range(len(M)):
            D.append(self.subtractMinD(self.vertDist(M[i], center)))
        return D
		
	def getFrame(self, filenames, token):
		f = open(filenames, 'r').readlines()
		frames = []
		for i in f:
			x = i.split('/')
			if x[0] == token:
				y = i[:-5].split('_')
				frames.append(int(y[1]))
		return min(frames)	
	
if __name__ == "__main__":
	#demo(sys.argv[1], 'neutral.csv')
    NeutralTongue(sys.argv[1], 'neutral.csv', True, True, True, True)
    gtk.main()
    

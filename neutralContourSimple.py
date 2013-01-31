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

import sys, math
import pylab as p
from numpy import *
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm


class NeutralTongue():
	
	def __init__(self):
		'''center points determined by transforming the point (426, 393) several times
		   with peterotron, and taking the average.
		'''
		#self.centerX = 710
		#self.centerY = 638
		
		# these come from hand tuning to find the smallest range of y values of polar mags
		self.centerX = 665
		self.centerY = 525
	
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
		p.plot(range(32), mags)
	
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
	
	def plotC(self, Contour):
		p.plot(range(len(Contour)), Contour)
	
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
	
	def linguagram(self,X,Y):
		x1 = array(X)
		y1 = array(Y)
		Z = []
		for i in range(len(X)):
			zs = []
			for j in range(32):
				zs.append(i+1)
			Z.append(zs)
		z1 = array(Z)
		
		fig = p.figure()
		ax = Axes3D(fig)
		ax.plot_surface(z1, -x1, -y1, rstride=1, cstride=1, cmap=cm.jet)
		ax.view_init(90,-90)
		p.show()
	
	def NeutralLinguagram(self, M, savename, start=1):
		fakeX = []
		for i in range(len(M)):
			xs = []
			for j in range(1,33):
				xs.append(j)
			fakeX.append(xs)
		
		x1 = array(fakeX)
		y1 = array(M)
		Z = []
		for i in range(start, (len(M)+start)):
			zs = []
			for j in range(32):
				zs.append(i)
			Z.append(zs)
		z1 = array(Z)
		
		fig = p.figure()
		ax = Axes3D(fig)
		ax.plot_surface(z1, -x1, y1, rstride=1, cstride=1, cmap=cm.jet)
		ax.view_init(90,-90)
		p.suptitle(savename[:-4])
		#p.show()
		
		p.savefig(savename, format = 'png')
	
	def getFrame(self, filenames, token):
		f = open(filenames, 'r').readlines()
		frames = []
		for i in f:
			#x = i.split('/')
			#if x[0] == token:
			#	y = i[:-5].split('_')
			#	frames.append(int(y[1]))
			x = i.split('_')
			if x[0] == token:
			    frames.append(int(x[1][:-5]))
		return min(frames)

def demo(contours, neutral):
	t = NeutralTongue()
	cx, cy = t.getNeutral(neutral)
	cmags = t.makePolar(cx, cy)
	X, Y = t.loadContours(contours)
	M = t.batchConvert2Polar(X, Y)
	D = t.batchGetMinD(M, cmags)
	#start = t.getFrame('filenames.txt', contours[:-4])
	#t.linguagram(X, Y)
	savename = contours[:-4] + '.png'
	#t.NeutralLinguagram(D, savename, start)
	t.NeutralLinguagram(D, savename)

#def batch(filename):
	
	

def plotTvB(contours, backNum, tipNum, neutral='neutral.csv'):
	'''backNum is the point on the contour from which to extract back peak value
	   similarly, tipNum tells where to extract tip peak value
	'''
	t = NeutralTongue()
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
	
	start = t.getFrame('filenames.txt', contours[:-4])
	p.plot(range(start, start+len(D) ), back)
	p.plot(range(start, start+len(D) ), tip)
	p.show()
	
	return back, tip

def analyze(files, results):
	f = open(files, 'r').readlines()
	o = open(results, 'w')
	o.write("token\tlag\tbackrow\ttiprow\tlstart\tlend\tbackpeak\ttippeak\n")
	
	t = NeutralTongue()
	cx, cy = t.getNeutral('neutral.csv')
	cmags = t.makePolar(cx, cy)
	
	for i in range(len(f)):
		contours = f[i][:-1]
		X, Y = t.loadContours(contours)
		M = t.batchConvert2Polar(X, Y)
		D = t.batchGetMinD(M, cmags)
		start = t.getFrame('filenames.txt', contours[:-4])
		
		#show the neutral linguagram to get backNum and tipNum
		savename = contours[:-4] + '.png'
		print savename
		t.NeutralLinguagram(D, savename, start)
		#backNum = int(raw_input("Back Row -> "))
		#tipNum = int(raw_input("Tip Row -> "))
		backNum = 7
		tipNum = 23
		
		#show the TvB plot to determine l boundaries
		back, tip = plotTvB(contours, backNum, tipNum)
		lstart = int(raw_input("L start -> "))
		lend = int(raw_input("L end -> "))
		
		#find the lag
		lt = tip[lstart-start:lend-start+1]
		maxt = -1000
		indt = -1
		for j in range(len(lt)):
			if lt[j] > maxt:
				maxt = lt[j]
				indt = j
		
		lb = back[lstart-start:lend-start+1]
		maxb = -1000
		indb = -1
		for k in range(len(lb)):
			if lb[k] > maxb:
				maxb = lb[k]
				indb = k
		
		indt = lstart + indt
		indb = lstart + indb
		lag = indt - indb
		o.write("%s\t%d\t%d\t%d\t%d\t%d\t%d\t%d\n" % (contours[:-4], lag, backNum, tipNum, lstart, lend, indb, indt))
	
	o.close()

def analyzefromfile(templatefile, results):
	f = open(templatefile, 'r').readlines()
	o = open(results, 'w')
	o.write(f[0])
	
	t = NeutralTongue()
	cx, cy = t.getNeutral('neutral.csv')
	cmags = t.makePolar(cx, cy)
	
	for i in range(1, len(f)):
		x = f[i][:-1].split('\t')
		contours = x[0] + '.csv'
		X, Y = t.loadContours(contours)
		M = t.batchConvert2Polar(X, Y)
		D = t.batchGetMinD(M, cmags)
		start = t.getFrame('filenames.txt', contours[:-4])
		
		#show the neutral linguagram to get backNum and tipNum
		savename = contours[:-4] + '.png'
		t.NeutralLinguagram(D, savename, start)
		backNum = int(x[2])
		tipNum = int(x[3])
		
		#show the TvB plot to determine l boundaries
		back, tip = plotTvB(contours, backNum, tipNum)
		lstart = int(x[4])
		lend = int(x[5])
		
		#find the lag
		lt = tip[lstart-start:lend-start+1]
		maxt = -1000
		indt = -1
		for j in range(len(lt)):
			if lt[j] > maxt:
				maxt = lt[j]
				indt = j
		
		lb = back[lstart-start:lend-start+1]
		maxb = -1000
		indb = -1
		for k in range(len(lb)):
			if lb[k] > maxb:
				maxb = lb[k]
				indb = k
		
		indt = lstart + indt
		indb = lstart + indb
		lag = indt - indb
		o.write("%s\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%s\n" % (contours[:-4], lag, backNum, tipNum, lstart, lend, indb, indt, '\t'.join(x[8:len(x)]) ))
	
	o.close()

def GickFigures(infile, outfile):
	f = open(infile, 'r').readlines()
	o = open(outfile, 'w')
	
	t = NeutralTongue()
	cx, cy = t.getNeutral('neutral.csv')
	cmags = t.makePolar(cx, cy)
	
	for i in range(1, len(f)):
		x = f[i][:-1].split('\t')
		contours = x[0] + '.csv'
		X, Y = t.loadContours(contours)
		M = t.batchConvert2Polar(X, Y)
		D = t.batchGetMinD(M, cmags)
		start = t.getFrame('filenames.txt', contours[:-4])
		backNum = int(x[2])
		tipNum = int(x[3])
		lstart = int(x[4])
		lend = int(x[5])
		back, tip = plotTvB(contours, backNum, tipNum)
		lt = tip[lstart-start:lend-start+1]
		lb = back[lstart-start:lend-start+1]
		for j in range(len(lt)):
			o.write('%stip\t%s\t%d\t%d\n' % (x[0][:-1], x[0][-1], j, -lt[j]))
		
		for j in range(len(lb)):
			o.write('%sback\t%s\t%d\t%d\n' % (x[0][:-1], x[0][-1], j, -lb[j]))
	
	o.close()
	

if __name__ == "__main__":
	demo(sys.argv[1], 'neutral.csv')

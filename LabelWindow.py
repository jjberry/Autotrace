import neutralContour as nc
import pygtk
pygtk.require("2.0")
import gtk
import gtk.glade
import os, sys, subprocess
import gnomecanvas

class LabelWindow:
    def __init__(self, csvs, SHOW_LING, SHOW_NEUT, SHOW_WAVE, SHOW_SPEC):
        filename = 'labelwindowbackground.png'
        title = csvs[0]        
        thisdir = '/'.join(title.split('/')[:-1]) + '/'
        t = nc.NeutralTongue(title, thisdir+'neutral.csv', SHOW_LING, SHOW_NEUT, SHOW_WAVE, SHOW_SPEC)
        t.saveNcrop('labelwindowbackground.png')
        numFrames = len(t.X)
        t.win.destroy()
                
        self.gladefile = "LinguaViewer.glade"
        self.wTree = gtk.glade.XML(self.gladefile, "LabelWindow")
        self.window = self.wTree.get_widget("LabelWindow")
        self.window.connect('destroy', self.onDestroy)
        self.window.set_title(title)
        self.numFrames = numFrames
        self.title = title
        self.static_dir = os.getcwd() + '/'
        self.wavname = title[:-4] + ".wav"
        
        dic = { "on_tbSave1_clicked" : self.onSave,
                "on_tbPlay1_clicked" : self.playSound,
                "on_entry1_activate" : self.updateText}
        self.wTree.signal_autoconnect(dic)
        
        self.textentry = self.wTree.get_widget("entry1")
        self.dorsumentry = self.wTree.get_widget("entry2")
        self.tipentry = self.wTree.get_widget("entry3")
        self.statusbar = self.wTree.get_widget("statusbar3")
        self.vbox = self.wTree.get_widget("hbox4")
        
        self.canvas = gnomecanvas.Canvas(aa=True)
        
        self.vbox.add(self.canvas)
        self.window.set_resizable(False)
        self.window.show_all()
        
        self.canvas.connect("event", self.canvas_event)
        
        #add a bit of whitespace to the image to put the text labels
        cmd = ['convert', '-size', '600x75', 'xc:white', 'white.png']
        proc = subprocess.Popen(cmd)
        status = proc.wait()
        cmd = ['montage', 'white.png', filename, '-mode', 'Concatenate', '-tile', '1x', 'canvas.png']
        proc = subprocess.Popen(cmd)
        status = proc.wait()
        
        pixbuf = gtk.gdk.pixbuf_new_from_file('canvas.png')
        itemType = gnomecanvas.CanvasPixbuf
        self.background = self.canvas.root().add(itemType, x=0, y=0, pixbuf=pixbuf)
        self.width = pixbuf.get_width()
        self.height = pixbuf.get_height()

        #self.textview.set_size_request(self.width, 100)
        self.canvas.set_size_request(self.width, self.height)
        self.canvas.set_scroll_region(0, 0, self.width, self.height)
        
        #set the border lines
        self.leftedge = 75.0
        self.rightedge = 540.0
        self.canvas.root().add(gnomecanvas.CanvasLine, points=[self.leftedge, self.height, self.leftedge, 0], \
                fill_color_rgba=0x000000FF, width_units=1.0)
        self.canvas.root().add(gnomecanvas.CanvasLine, points=[self.rightedge, self.height, self.rightedge, 0], \
                fill_color_rgba=0x000000FF, width_units=1.0)
                
        #add a divider between the label portion and the image
        self.canvas.root().add(gnomecanvas.CanvasLine, points=[self.leftedge, 76.0, self.rightedge, 76.0], \
                fill_color_rgba=0x00000099, width_units=1.0)
        
        self.canvas.root().add(gnomecanvas.CanvasText, x=35, y=35, text="Label", fill_color_rgba=0x000000FF, \
                justification=gtk.JUSTIFY_CENTER)

        self.dragging = False
        self.previous_value = False
        self.boundaries = []
        self.boundary_values = []

        self.label_limit = 99
        self.label_text = []
        self.label_centers = []
        self.labels = []
        for i in range(self.label_limit):
            self.label_text.append('')
            self.label_centers.append(i+75)
            self.labels.append(self.canvas.root().add(gnomecanvas.CanvasText, x=self.label_centers[i], y=35, \
                text=self.label_text[i], fill_color_rgba=0x000000FF, justification=gtk.JUSTIFY_CENTER))
            
        self.intervals = [[self.leftedge, self.rightedge]]
        self.selected_interval = 0
        self.sorted_boundaries = [self.leftedge, self.rightedge]
        
        self.selected_mask = None
        self.loadLabel()
        

    def playSound(self, event):
        cmd = ['/Applications/Praat.app/Contents/MacOS/Praat', self.static_dir + 'playSound.praat', self.wavname]
        proc = subprocess.Popen(cmd)
        status = proc.wait()
    
    def canvas_event(self, widget, event):
        if event.type == gtk.gdk.MOTION_NOTIFY:
            if (event.x >= self.leftedge) and (event.x <= self.rightedge) and (event.y > 75): 
                context_id = self.statusbar.get_context_id("mouse motion")
                text = "(" + str(event.x) + ", " + str(event.y) + ")"
                self.statusbar.push(context_id, text)  
        self.set_boundary(widget, event)

    def set_boundary(self, widget, event):
        if (event.type == gtk.gdk.BUTTON_PRESS):
            if (event.button == 1):
                self.dragging = True
            elif (event.button == 3):
                self.delete_points = True

        if (event.type == gtk.gdk.MOTION_NOTIFY):
            # see if we are close to a boundary
            if (self.dragging == True) and (self.previous_value != True):
                result, self.currentline, self.currentind = self.check_proximity(event)
                if (result == True) and (event.y > 75):
                    self.currentline.set(points=[event.x, self.height, event.x, 0])
                    self.boundary_values[self.currentind] = event.x
                    self.previous_value = True
            elif (self.dragging == True) and (self.previous_value == True):
                self.currentline.set(points=[event.x, self.height, event.x, 0])
                self.boundary_values[self.currentind] = event.x

        # Sends selection data to the relevant method
        if (event.type == gtk.gdk.BUTTON_RELEASE) and (self.dragging):
            if (event.button == 1):
                if not self.previous_value:
                    if (event.x >= self.leftedge) and (event.x <= self.rightedge) and (event.y > 75): 
                        self.add_boundary(event)
                    elif (event.x >= self.leftedge) and (event.x <= self.rightedge) and (event.y < 75):
                        self.select_textbox(event)                
                else:
                    self.previous_value = False
                self.update_boundaries()   
                self.dragging = False
        elif (event.type == gtk.gdk.BUTTON_RELEASE) and (self.delete_points):
            if (event.button == 3):
                result, line, ind = self.check_proximity(event)
                if result:
                    line.destroy()
                    self.boundaries.remove(self.boundaries[ind])
                    self.boundary_values.remove(self.boundary_values[ind])
                self.update_boundaries()
                self.delete_points = False

    def check_proximity(self, event):
        if len(self.boundaries) > 0:
            for i in range(len(self.boundaries)):
                if (event.x >= self.boundary_values[i]-2) and (event.x <= self.boundary_values[i]+2):
                    ind = i
        try:
            return True, self.boundaries[ind], ind
        except:
            return False, None, None
            

    def add_boundary(self, event):
        self.boundary_values.append(event.x)
        self.boundaries.append(self.canvas.root().add(gnomecanvas.CanvasLine, points=[event.x, self.height, event.x, 0], \
                fill_color_rgba=0xFF0000FF, width_units=2.0))
        self.update_boundaries()

    def update_boundaries(self):
        self.sorted_boundaries = [self.leftedge]
        self.sorted_boundaries.extend(sorted(self.boundary_values))
        self.sorted_boundaries.append(self.rightedge)
        self.update_intervals()
        
    def update_intervals(self):
        self.intervals = []

        for i in range(len(self.sorted_boundaries) - 1):
            self.intervals.append([self.sorted_boundaries[i], self.sorted_boundaries[i+1]])
        
        for j in range(len(self.intervals)):
            self.label_centers[j] = round((self.intervals[j][0] + self.intervals[j][1])/2.0)
            self.labels[j].set(x=self.label_centers[j])
                                    
    def updateText(self, event):
        if self.selected_mask != None:
            labeltext = self.textentry.get_text()        
            self.label_text[self.selected_interval] = labeltext
            self.labels[self.selected_interval].set(text=labeltext)
            #print self.intervals

    def select_textbox(self, event):
        try:
            self.selected_mask.destroy()
        except AttributeError:
            pass
        for i in range(len(self.intervals)):
            if (event.x >= self.intervals[i][0]) and (event.x < self.intervals[i][1]):
                right = self.intervals[i][1]
                left = self.intervals[i][0]
                self.selected_interval = i
                
        self.textentry.set_text(self.label_text[self.selected_interval])
        #print "interval = ", self.selected_interval

        self.selected_mask = self.canvas.root().add(gnomecanvas.CanvasRect, x1=left, y1=0, x2=right, y2=75,	\
            fill_color_rgba=0xFFCC3355, outline_color_rgba=0xFFEECC99, width_units=1.0)
        
                
    def loadLabel(self):
        labelfile = self.title+'.label.txt'
        if os.path.isfile(labelfile):
            f = open(labelfile, 'r').readlines()
            dorsumline = f[2][:-1].split('\t')[1]
            tipline = f[3][:-1].split('\t')[1]
            self.dorsumentry.set_text(dorsumline)
            self.tipentry.set_text(tipline)
            for i in range(6,len(f)):
                bound = float(f[i][:-1].split('\t')[0])
                b = LabelTrick(bound)
                self.add_boundary(b)
            selected_interval = 0
            for i in range(5, len(f)):
                labeltext = f[i][:-1].split('\t')[2]
                self.label_text[selected_interval] = labeltext
                self.labels[selected_interval].set(text=labeltext)
                selected_interval += 1
        
    def onSave(self, event):
        dorsum = int(self.dorsumentry.get_text())
        tip = int(self.tipentry.get_text())  
        labelfilename = self.title + '.label.txt'
        o = open(labelfilename, 'w')
        o.write('Filename\t%s\n' % self.title)
        o.write('Num_Frames\t%d\n' % self.numFrames)
        o.write('Dorsum_Line\t%d\n' % dorsum)
        o.write('Tip_Line\t%d\n' % tip)
        o.write('Intervals\n')
        for i in range(len(self.intervals)):
            o.write('%.2f\t%.2f\t%s\n' %(self.intervals[i][0], self.intervals[i][1], self.label_text[i]))
        o.close()
        fin = gtk.MessageDialog(None, gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_INFO,
            gtk.BUTTONS_CLOSE, "Save successful")
        fin.run()
        fin.destroy()
                
    def onDestroy(self, event):
        dorsum = int(self.dorsumentry.get_text())
        tip = int(self.tipentry.get_text())  
        labelfilename = self.title + '.label.txt'
        o = open(labelfilename, 'w')
        o.write('Filename\t%s\n' % self.title)
        o.write('Num_Frames\t%d\n' % self.numFrames)
        o.write('Dorsum_Line\t%d\n' % dorsum)
        o.write('Tip_Line\t%d\n' % tip)
        o.write('Intervals\n')
        for i in range(len(self.intervals)):
            o.write('%.2f\t%.2f\t%s\n' %(self.intervals[i][0], self.intervals[i][1], self.label_text[i]))
        o.close()
        
        #gtk.main_quit()
        self.window.destroy()
        
class LabelTrick:
    def __init__(self, value):
        self.x = value
        
if __name__ == "__main__":
    LabelWindow(sys.argv[1])
    gtk.main()
    

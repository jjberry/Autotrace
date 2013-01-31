import os, sys, subprocess
import Image
import pygtk
pygtk.require('2.0')
import gtk, gobject
import gtk.glade

class ImageFixer:
    def __init__(self, filenames):
        self.gladefile = "LinguaViewer.glade"
        self.wTree = gtk.glade.XML(self.gladefile, "resize")
        self.window = self.wTree.get_widget("resize")
        self.window.set_size_request(400, 100)

        self.window.connect("destroy", self.destroy_progress)
                        
        self.pbar = self.wTree.get_widget("progressbar1")
        self.pbar.show()
        self.val = 0.0
        self.frac = 1.0/len(filenames)
        self.pbar.set_fraction(self.val)
        result = self.check(filenames)
        
        if result == gtk.RESPONSE_OK:
            task = self.fix(filenames)
            gobject.idle_add(task.next)      
            
        else:
            self.window.destroy()    
        
    def check(self, filenames):
        #check whether we need to do correction
        badcount = 0
        for i in filenames:
            im = Image.open(i)
            if (im.size[0] != 720): #or (im.size[1] != 480):
                badcount += 1
                break
        if badcount > 0:
            dlg = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_WARNING,
                gtk.BUTTONS_OK_CANCEL, 
                "It appears that 1 or more images need to be resized.\nResizing the images will overwrite the originals. Continue?")
            result = dlg.run()
            dlg.destroy()
        else: 
            result = gtk.RESPONSE_CANCEL

        return result
    
    def fix(self, files):
        l = len(files)
        c = 0
        for j in files:
            im = Image.open(j)
            if (im.size[0] != 720) or (im.size[1] != 480):
                cmd = ['convert', j, '-shave', '126x0', j]
                p = subprocess.Popen(cmd)
                p.wait()

                cmd = ['convert', j, '-chop', '12x0', j]
                p = subprocess.Popen(cmd)
                p.wait()

                cmd = ['convert', j, '-resize', '720x480!', j]
                p = subprocess.Popen(cmd)
                #p.wait()
            self.val += self.frac
            self.pbar.set_fraction(self.val)
            c += 1
            if c < l:
                yield True
            else:
                yield False
        
    def destroy_progress(self, event):
        self.window.destroy()


    

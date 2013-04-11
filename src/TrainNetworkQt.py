'''
Created on Apr 4, 2013

@author: Jeff

TrainNetworkQt.py 
    A Qt version of the network trainer that uses the python version of the deep net code
'''

from PyQt4.QtGui import QMainWindow, QKeySequence, QAction, QFileDialog, QMessageBox, QWidget, \
QPushButton, QLineEdit, QHBoxLayout, QVBoxLayout, QLabel, QApplication, QIntValidator, QDoubleValidator, \
QCheckBox, QDialog, QTextBrowser, QDialogButtonBox
from PyQt4.QtCore import SIGNAL, pyqtSignal, QThread, QObject

import sys
import backprop
import deepnet
import autoencoder
import loadData
import numpy as np
import scipy.io

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.mainWidget = MainWidget(self)
        self.setCentralWidget(self.mainWidget)
        self.setWindowTitle(self.tr("Train Network"))
        self.createActions()
        self.createMenus()

        self.stream = EmittingStream(textWritten=self.write)
        sys.stdout = self.stream
        #sys.stderr = self.stream
        
        self.dataDir = ''
        
        #set the default training parameters in case user doesn't use the parameter dialog
        limit = False
        limit_num = 100
        layer_sizes = [-1,-1,-1,-1]
        layer_types = ['sigmoid', 'sigmoid', 'sigmoid', 'sigmoid']
        pretrain_iter = [225,75,75]
        pretrain_lr = 0.0025
        backprop_iter = 30
        self.trainingParameters = [layer_sizes, layer_types, pretrain_iter, pretrain_lr, backprop_iter, limit, limit_num]

        self.thread = TrainThread(self.stream)
        self.thread.setArgs(self.trainingParameters)
        self.connect(self.thread, SIGNAL('trainingFinished()'), self.trainingFinished)
                
    def __del__(self):
        sys.stdout = sys.__stdout__   
        #sys.stderr = sys.__stderr__ 
        
    def createActions(self):
        self.openAction = QAction(self.tr("Set &data directory"), self)
        self.openAction.setShortcut(QKeySequence.Open)
        self.openAction.setStatusTip(self.tr("Set the data directory"))
        self.connect(self.openAction, SIGNAL('triggered()'), self.openDataDir)
        
        self.exitAction = QAction(self.tr("E&xit"), self)
        self.exitAction.setShortcut(self.tr("Ctrl+Q"))
        self.exitAction.setStatusTip(self.tr("Exit the application"))
        self.connect(self.exitAction, SIGNAL('triggered()'), self.onClose)

        self.parametersAction = QAction(self.tr("Set &parameters"), self)
        self.parametersAction.setStatusTip(self.tr("Set the training parameters"))
        self.connect(self.parametersAction, SIGNAL('triggered()'), self.setParameters)
        
    def createMenus(self):    
        fileMenu = self.menuBar().addMenu(self.tr("&File"))
        fileMenu.addAction(self.openAction)
        fileMenu.addSeparator()
        fileMenu.addAction(self.exitAction)
        
        optionsMenu = self.menuBar().addMenu(self.tr("&Options"))
        optionsMenu.addAction(self.parametersAction)

    def setParameters(self):
        dialog = ParametersDialog()
        if dialog.exec_():
            self.trainingParameters = dialog.getValues()
            self.thread.setArgs(self.trainingParameters)
 
    def onClose(self):
        self.close()
    
    def trainingFinished(self):
        self.mainWidget.textBrowser.append("Training finished")
        self.mainWidget.trainButton.setEnabled(True)
        
    def browseClicked(self):
        self.openDataDir()
        
    def openDataDir(self):
        fileDialog = QFileDialog()
        fileDialog.setFileMode(fileDialog.DirectoryOnly)
        self.dataDir = fileDialog.getExistingDirectory(caption="Choose the data directory")
        self.mainWidget.dataDirLineEdit.setText(self.dataDir)
        self.thread.setDataDir(self.dataDir)
                    
    def trainClicked(self):
        if self.dataDir == '':
            QMessageBox.warning(self, 'No data specified', 'Please specify a data directory', 
                                          QMessageBox.Ok) 
        else:
            self.mainWidget.textBrowser.append(self.tr("Training started"))
            self.mainWidget.trainButton.setEnabled(False)
            self.trainNetwork()
        
    def trainNetwork(self):
        self.thread.start()    
        
    def write(self, text):
        self.mainWidget.textBrowser.append(text)
      
class MainWidget(QWidget):
    def __init__(self, parent):
        super(MainWidget, self).__init__(parent)
        
        self.dataDirLineEdit = QLineEdit()
        self.dataLabel = QLabel(self.tr("Data Directory:"))
        self.dataLabel.setBuddy(self.dataDirLineEdit)
        self.dataBrowseButton = QPushButton(self.tr("&Browse..."))
        self.connect(self.dataBrowseButton, SIGNAL('clicked()'), parent.browseClicked)
             
        self.closeButton = QPushButton(self.tr("Close"))
        self.connect(self.closeButton, SIGNAL('clicked()'), parent.onClose)
        
        self.trainButton = QPushButton(self.tr("&Train"))
        self.connect(self.trainButton, SIGNAL('clicked()'), parent.trainClicked)
        
        self.textBrowser = QTextBrowser()
                
        self.dataLayout = QHBoxLayout()
        self.dataLayout.addWidget(self.dataLabel)
        self.dataLayout.addWidget(self.dataDirLineEdit)
        self.dataLayout.addWidget(self.dataBrowseButton)
        
        self.buttonLayout = QHBoxLayout()
        self.buttonLayout.addWidget(self.closeButton)
        self.buttonLayout.addWidget(self.trainButton)
        
        self.mainLayout = QVBoxLayout()
        self.mainLayout.addLayout(self.dataLayout)
        self.mainLayout.addWidget(self.textBrowser)
        self.mainLayout.addLayout(self.buttonLayout)
        
        self.setLayout(self.mainLayout)    
        
class ParametersDialog(QDialog):
    def __init__(self, parent=None):
        super(ParametersDialog, self).__init__(parent)

        self.limitImagesCheckBox = QCheckBox(self.tr("&Limit number of images"))
        self.limitLineEdit = QLineEdit()
        self.connect(self.limitImagesCheckBox, SIGNAL('clicked()'), self.limitClicked)
        self.limitLineEdit.setText("100")
        self.limitLineEdit.setValidator(QIntValidator())
        self.limitLineEdit.setEnabled(False)
        
        self.useDefaultCheckBox = QCheckBox(self.tr("Use &default parameters"))
        self.useDefaultCheckBox.setChecked(True)
        self.connect(self.useDefaultCheckBox, SIGNAL('clicked()'), self.defaultClicked)
        
        self.layerSizesLabel = QLabel(self.tr("Layer &sizes (-1 for input data size):"))
        self.layerSizesLineEdit = QLineEdit()
        self.layerSizesLineEdit.setText("-1, -1, -1, -1")
        self.layerSizesLineEdit.setEnabled(False)                
        self.layerSizesLabel.setBuddy(self.layerSizesLineEdit)
 
        self.layerTypesLabel = QLabel(self.tr("Layer &types (sigmoid or gaussian):"))
        self.layerTypesLineEdit = QLineEdit()
        self.layerTypesLineEdit.setText("sigmoid, sigmoid, sigmoid, sigmoid")
        self.layerTypesLineEdit.setEnabled(False)
        self.layerTypesLabel.setBuddy(self.layerTypesLineEdit)
        
        self.pretrainIterLabel = QLabel(self.tr("Pretraining &iterations for each layer:"))
        self.pretrainIterLineEdit = QLineEdit()
        self.pretrainIterLineEdit.setText("225, 75, 75")
        self.pretrainIterLineEdit.setEnabled(False)
        self.pretrainIterLabel.setBuddy(self.pretrainIterLineEdit)
        
        self.pretrainLRLabel = QLabel(self.tr("Pretraining &learning rate:"))
        self.pretrainLRLineEdit = QLineEdit()
        self.pretrainLRLineEdit.setText("0.0025")
        self.pretrainLRLineEdit.setValidator(QDoubleValidator())
        self.pretrainLRLineEdit.setEnabled(False)
        self.pretrainLRLabel.setBuddy(self.pretrainLRLineEdit)
        
        self.backpropIterLabel = QLabel(self.tr("&Backprop iterations:"))  
        self.backpropIterLineEdit = QLineEdit()
        self.backpropIterLineEdit.setText("30")
        self.backpropIterLineEdit.setValidator(QIntValidator())
        self.backpropIterLineEdit.setEnabled(False)
        self.backpropIterLabel.setBuddy(self.backpropIterLineEdit)
        
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        self.connect(self.buttonBox, SIGNAL('accepted()'), self.accept)
        self.connect(self.buttonBox, SIGNAL('rejected()'), self.reject)
        
        self.limitLayout = QHBoxLayout()
        self.limitLayout.addWidget(self.limitImagesCheckBox)
        self.limitLayout.addWidget(self.limitLineEdit)
        
        self.layerSizesLayout = QHBoxLayout()
        self.layerSizesLayout.addWidget(self.layerSizesLabel)
        self.layerSizesLayout.addWidget(self.layerSizesLineEdit)
        
        self.layerTypesLayout = QHBoxLayout()
        self.layerTypesLayout.addWidget(self.layerTypesLabel)
        self.layerTypesLayout.addWidget(self.layerTypesLineEdit)
        
        self.pretrainIterLayout = QHBoxLayout()
        self.pretrainIterLayout.addWidget(self.pretrainIterLabel)
        self.pretrainIterLayout.addWidget(self.pretrainIterLineEdit)
        
        self.pretrainLRLayout = QHBoxLayout()
        self.pretrainLRLayout.addWidget(self.pretrainLRLabel)
        self.pretrainLRLayout.addWidget(self.pretrainLRLineEdit)
        
        self.backpropIterLayout = QHBoxLayout()
        self.backpropIterLayout.addWidget(self.backpropIterLabel)
        self.backpropIterLayout.addWidget(self.backpropIterLineEdit)
        
        self.mainLayout = QVBoxLayout()
        self.mainLayout.addLayout(self.limitLayout)
        self.mainLayout.addWidget(self.useDefaultCheckBox)
        self.mainLayout.addLayout(self.layerSizesLayout)
        self.mainLayout.addLayout(self.layerTypesLayout)
        self.mainLayout.addLayout(self.pretrainIterLayout)
        self.mainLayout.addLayout(self.pretrainLRLayout)
        self.mainLayout.addLayout(self.backpropIterLayout)
        self.mainLayout.addWidget(self.buttonBox)

        self.setLayout(self.mainLayout)
        self.setWindowTitle(self.tr("Set training parameters"))
        self.setFixedHeight(self.sizeHint().height())
        
    def getValues(self):
        limit = self.limitImagesCheckBox.isChecked()
        limit_num = int(self.limitLineEdit.text())
        if self.useDefaultCheckBox.isChecked():
            layer_sizes = [-1,-1,-1,-1]
            layer_types = ['sigmoid', 'sigmoid', 'sigmoid', 'sigmoid']
            pretrain_iter = [225,75,75]
            pretrain_lr = 0.0025
            backprop_iter = 30
        else:
            layer_sizes = [int(x) for x in (self.layerSizesLineEdit.text()).split(',')]
            layer_types = [str(x) for x in (self.layerTypesLineEdit.text()).split(',')]
            pretrain_iter = [int(x) for x in (self.pretrainIterLineEdit.text()).split(',')]
            pretrain_lr = float(self.pretrainLRLineEdit.text())
            backprop_iter = int(self.backpropIterLineEdit.text())
        return [layer_sizes, layer_types, pretrain_iter, pretrain_lr, backprop_iter, limit, limit_num]

    def limitClicked(self):
        self.limitLineEdit.setEnabled(self.limitImagesCheckBox.isChecked())    
        
    def defaultClicked(self):
        self.layerSizesLineEdit.setEnabled(not self.useDefaultCheckBox.isChecked())
        self.layerTypesLineEdit.setEnabled(not self.useDefaultCheckBox.isChecked())
        self.pretrainIterLineEdit.setEnabled(not self.useDefaultCheckBox.isChecked())
        self.pretrainLRLineEdit.setEnabled(not self.useDefaultCheckBox.isChecked())
        self.backpropIterLineEdit.setEnabled(not self.useDefaultCheckBox.isChecked())

class EmittingStream(QObject):
    
    textWritten = pyqtSignal(str)
    
    def write(self, text):
        self.textWritten.emit(str(text))
 
class TrainThread(QThread):
    def __init__(self, outputStream, parent=None):
        super(TrainThread, self).__init__(parent)
        self.stream = outputStream
        
    def setArgs(self, args):
        self.layer_sizes = args[0] 
        self.layer_types = args[1] 
        self.pretrain_iter = args[2] 
        self.pretrain_lr = args[3] 
        self.backprop_iter = args[4] 
        self.limit = args[5]
        self.limit_num = args[6]
    
    def setDataDir(self, directory):
        self.dataDir = directory    
        
    def run(self):
        self.stream.write("Input parameters")
        self.stream.write("\tLayer sizes: {}".format(self.layer_sizes))
        self.stream.write("\tLayer types: {}".format(self.layer_types))
        self.stream.write("\tPre-train LR: {}".format(self.pretrain_lr))
        self.stream.write("\tPre-train iterations: {}".format(self.pretrain_iter))
        self.stream.write("\tBackprop iterations: {}".format(self.backprop_iter))
        if self.limit:
            self.stream.write("Limiting input to %d images" % self.limit_num)
        self.train()
        self.emit(SIGNAL('trainingFinished()'))

    def save(self, network, name):
        mdic = {}
        for i in range(len(network)):
            try:
                mdic['W%d'%(i+1)] = network[i].W.as_numpy_array()
                mdic['b%d'%(i+1)] = network[i].hbias.as_numpy_array()
            except AttributeError:
                mdic['W%d'%(i+1)] = network[i].W
                mdic['b%d'%(i+1)] = network[i].hbias
            mdic['hidtype%d'%(i+1)] = network[i].hidtype
            scipy.io.savemat(name, mdic)

    def train(self):
        # this will be replaced by calls to loadData.py
        #data = np.load('scaled_images.npy')
        #data = np.asarray(data, dtype='float32')
        #data /= 255.0
        
        l = loadData.Loader(str(self.dataDir),stream=self.stream)
        if self.layer_types[0] != 'sigmoid':
            layer1_sigmoid = False
        else:
            layer1_sigmoid = True
        l.loadData(layer1_sigmoid)
        data = l.XC
        
        if self.limit:
            inds = np.arange(data.shape[0])
            np.random.shuffle(inds)
            data = data[inds[:self.limit_num],:]
        self.stream.write(data.shape)

        # parse the layer sizes
        sizes = []
        for i in self.layer_sizes:
            if i == -1:
                sizes.append(data.shape[1])
            else:
                sizes.append(i)
        
        #set up and train the initial deepnet
        dnn = deepnet.DeepNet(sizes, self.layer_types, stream=self.stream)
        dnn.train(data, self.pretrain_iter, self.pretrain_lr)

        #save the trained deepnet
        #pickle.dump(dnn, file('pretrained.pkl','wb')) # Looks like pickle won't work with Qt :(
        self.save(dnn.network, 'pretrained.mat')
        
        #unroll the deepnet into an autoencoder
        autoenc = autoencoder.unroll_network(dnn.network)
        
        #fine-tune with backprop
        mlp = backprop.NeuralNet(network=autoenc, stream=self.stream)
        trained = mlp.train(mlp.network, data, data, max_iter=self.backprop_iter, 
                validErrFunc='reconstruction', targetCost='linSquaredErr')
        
        #save
        #pickle.dump(trained, file('network.pkl','wb'))
        self.save(trained, 'network.mat')
   
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
     
    sys.exit(app.exec_())

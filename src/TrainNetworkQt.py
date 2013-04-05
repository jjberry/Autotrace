'''
Created on Apr 4, 2013

@author: Jeff

TrainNetworkQt.py 
    A Qt version of the network trainer that uses the python version of the deep net code
'''

from PyQt4.QtGui import *
from PyQt4.QtCore import *

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.mainWidget = MainWidget(self)
        self.setCentralWidget(self.mainWidget)
        self.setWindowTitle(self.tr("Train Network"))

        self.createActions()
        self.createMenus()
        
    def createActions(self):
        self.openAction = QAction(self.tr("Set &data directory"), self)
        self.openAction.setShortcut(QKeySequence.Open)
        self.openAction.setStatusTip(self.tr("Set the data directory"))
        self.connect(self.openAction, SIGNAL('triggered()'), self.mainWidget.openDataDir)
        
        self.exitAction = QAction(self.tr("E&xit"), self)
        self.exitAction.setShortcut(self.tr("Ctrl+Q"))
        self.exitAction.setStatusTip(self.tr("Exit the application"))
        self.connect(self.exitAction, SIGNAL('triggered()'), self.close)

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
            layer_sizes, layer_types, pretrain_iter, pretrain_lr, backprop_iter, limit, limit_num = dialog.getValues()
            print layer_sizes, layer_types, pretrain_iter, pretrain_lr, backprop_iter, limit, limit_num
        
      
class MainWidget(QWidget):
    def __init__(self, parent):
        super(MainWidget, self).__init__(parent)
        
        self.dataDirLineEdit = QLineEdit()
        self.dataLabel = QLabel(self.tr("Data Directory:"))
        self.dataLabel.setBuddy(self.dataDirLineEdit)
        self.dataBrowseButton = QPushButton(self.tr("&Browse..."))
        self.connect(self.dataBrowseButton, SIGNAL('clicked()'), self.browseClicked)
             
        self.closeButton = QPushButton(self.tr("Close"))
        self.connect(self.closeButton, SIGNAL('clicked()'), parent.close)
        
        self.trainButton = QPushButton(self.tr("&Train"))
        self.connect(self.trainButton, SIGNAL('clicked()'), self.trainClicked)
        
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
    
    def browseClicked(self):
        self.openDataDir()
        
    def openDataDir(self):
        fileDialog = QFileDialog()
        fileDialog.setFileMode(fileDialog.DirectoryOnly)
        self.dataDir = fileDialog.getExistingDirectory(caption="Choose the data directory")
        self.dataDirLineEdit.setText(self.dataDir)
                    
    def trainClicked(self):
        self.textBrowser.append(self.tr("Training started"))    

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
        self.layerSizesLineEdit.setText("-1, -1, -1")
        self.layerSizesLineEdit.setEnabled(False)                
        self.layerSizesLabel.setBuddy(self.layerSizesLineEdit)
 
        self.layerTypesLabel = QLabel(self.tr("Layer &types (sigmoid or gaussian):"))
        self.layerTypesLineEdit = QLineEdit()
        self.layerTypesLineEdit.setText("sigmoid, sigmoid, sigmoid")
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
            layer_sizes = [-1,-1,-1]
            layer_types = ['sigmoid', 'sigmoid', 'sigmoid']
            pretrain_iter = [225,75,75]
            pretrain_lr = 0.0025
            backprop_iter = 30
        else:
            layer_sizes = [int(x) for x in (self.layerSizesLineEdit.text()).split(',')]
            layer_types = [str(x) for x in (self.layerTypesLineEdit.text()).split(',')]
            pretrain_iter = [int(x) for x in (self.pretrainIterLineEdit.text()).split(',')]
            pretrain_lr = float(self.pretrainLRLineEdit.text())
            backprop_iter = int(self.backpropIterLineEdit.text())
        return layer_sizes, layer_types, pretrain_iter, pretrain_lr, backprop_iter, limit, limit_num

    def limitClicked(self):
        self.limitLineEdit.setEnabled(self.limitImagesCheckBox.isChecked())    
        
    def defaultClicked(self):
        self.layerSizesLineEdit.setEnabled(not self.useDefaultCheckBox.isChecked())
        self.layerTypesLineEdit.setEnabled(not self.useDefaultCheckBox.isChecked())
        self.pretrainIterLineEdit.setEnabled(not self.useDefaultCheckBox.isChecked())
        self.pretrainLRLineEdit.setEnabled(not self.useDefaultCheckBox.isChecked())
        self.backpropIterLineEdit.setEnabled(not self.useDefaultCheckBox.isChecked())
        
        
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    
    #dialog = ParametersDialog()
    #dialog.show()
    #if dialog.exec_():
    #    layer_sizes, layer_types, pretrain_iter, pretrain_lr, backprop_iter, limit, limit_num = dialog.getValues()
    #    print layer_sizes, layer_types, pretrain_iter, pretrain_lr, backprop_iter, limit, limit_num
    
    sys.exit(app.exec_())

from PyQt5.QtWidgets import QWidget
from PyQt5 import QtCore, QtMultimedia
from PyQt5.QtWidgets import   QFileDialog
from PyQt5.QtCore import QSettings
from Forms.Ui_Main import Ui_MainWindow
from Forms.BoxOButtons import BoxOButtons
import os
import cv2
import datetime

class EyeGoreWindow(QWidget, Ui_MainWindow):    
    fps = 25.
    indexOfLastUsedCamera = -1
    videocapture = None
    timer = None
    buttonBox = None
    settings = QSettings()
    
    def __init__(self, parent):
        super(QWidget, self).__init__()
        self.setupUi(parent)
        self.comboBoxCameraSelect.addItems(self.getListOfCameras())
        self.buttonBox = BoxOButtons()
        self.comboBoxComport.clear()
        self.comboBoxComport.addItems(self.buttonBox.GetComportList())
       
        self.LoadSettings()
        
        self.pushButtonSave.clicked.connect(self.on_buttonSnapshotClicked)
        self.pushButtonSelectFolder.clicked.connect(self.on_SelectFolderClicked)
        self.comboBoxComport.currentIndexChanged.connect(self.ChangeComport)
        self.comboBoxCameraSelect.currentIndexChanged.connect(self.changeCamera)
        
        self.start()

        self.buttonBox.SetComport(self.comboBoxComport.currentText())
        self.buttonBox.Signal_ButtonState.connect(self.ButtonHandler)
        self.buttonBox.start()

    def start(self):
        cameraindex = self.comboBoxCameraSelect.currentIndex()
        #Only stop the videocapture when the selected camera is changed.
        #Some cameras take a long time to initialize after open is called.
        if not self.indexOfLastUsedCamera == cameraindex:
            if not self.videocapture is None:
                self.videocapture.release()
            #Should be able to do just self.videocapture = cv2.VideoCapture(cameraindex )
            #It worked with my old C170, but the C270 hangs after unpausing.
            #Splitting the calls for the new videocapture and the open keeps the C270 from hanging.
            self.videocapture = cv2.VideoCapture()
            self.videocapture.open(cameraindex )
            #Need to add controls for this.
            self.videocapture.set(cv2.CAP_PROP_FRAME_WIDTH, 1024)
            self.videocapture.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            self.indexOfLastUsedCamera  = cameraindex
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.nextFrameSlot)
        self.timer.start(1000./self.fps)

    def stop(self):
        if not self.timer is None:
            self.timer.stop()
        #Do not stop the video capture.
        #Some cameras take a long to to initialize
        #Only stop the camera in the start method when a new camera is selected.
        
    def getListOfCameras(self):
        camerasInfoList = QtMultimedia.QCameraInfo.availableCameras()
        camerasList=[]
        for cameraInfo in camerasInfoList:
            camerasList.append(cameraInfo.description())
        return camerasList

    def nextFrameSlot(self):
        try:
            ret, frame = self.videocapture.read()
            if self.checkBoxPause.isChecked():
                return                

            if not ret:
                self.stop()
                self.indexOfLastUsedCamera = -1
                self.start()
                return
        # Assume webcam gives BGR format images
        # May need to add an option or check the format from cv2 somehow
        # Opencv has an option to deliver all frames in a specified format - implement this and then we don't have to assume a format.
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        except:
            return

        self.CameraView.show()
        self.CameraView.setImage(frame)

    def changeCamera(self,  selectedCameraIndex):
        self.stop()
        self.start()
        self.SaveSettings()

    def ButtonHandler(self, ButtonID,  State):      
        if ButtonID == "2" and State == "0":
            self.checkBoxPause.setChecked(True)
            
        if ButtonID == "2" and State == "1":
            self.checkBoxPause.setChecked(False)
            
        if ButtonID == "3" and State == "0":
            self.on_buttonSnapshotClicked()

    def on_buttonSnapshotClicked(self):
            snapshot = self.CameraView.getPixmap()
            if snapshot is None:
                return
            #QApplication.primaryScreen().grabWindow(self.CameraView.winId())
            filename = datetime.datetime.now().strftime("%Y%m%d-%H%M%S") + ".png"
            filename = os.path.join(self.plainText_FolderName.toPlainText(),  filename)
            if filename:
                snapshot.save(filename,  "png")

    def on_SelectFolderClicked(self):
        directory = str(QFileDialog.getExistingDirectory(None, "Select Directory"))
        if directory:
            self.plainText_FolderName.clear()
            self.plainText_FolderName.insertPlainText(directory)
            self.SaveSettings()

    def ChangeComport(self):
        self.buttonBox.SetComport(self.comboBoxComport.currentText())
        self.SaveSettings()

    def SaveSettings(self):
        self.settings.setValue("ComPort",  self.comboBoxComport.currentText())
        self.settings.setValue("Camera", self.comboBoxCameraSelect.currentText())
        self.settings.setValue("ImageFolder",  self.plainText_FolderName.toPlainText())

    def LoadSettings(self):
        self.setComboBoxSelectedItemFromSettings("ComPort",self.comboBoxComport)
        self.setComboBoxSelectedItemFromSettings("Camera",self.comboBoxCameraSelect)
        directory = self.settings.value("ImageFolder", "")
        self.plainText_FolderName.clear()
        self.plainText_FolderName.insertPlainText(directory)
        
    def setComboBoxSelectedItemFromSettings(self,  settingName,  combobox):
        savedItemName = self.settings.value(settingName,  "-")
        itemIndex =  combobox.findText(savedItemName )
        if itemIndex>=0:
            combobox.setCurrentIndex(itemIndex)

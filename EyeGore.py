from PyQt5 import QtWidgets
from PyQt5.QtCore import QCoreApplication
from PyQt5 import QtCore, QtMultimedia
from PyQt5.QtWidgets import  QApplication,  QFileDialog
from PyQt5.QtCore import QSettings
import os
import cv2
import datetime

from Forms.Ui_Main import Ui_MainWindow
from Forms.BoxOButtons import BoxOButtons

fps = 25.
indexOfLastUsedCamera = -1
videocapture = None
timer = None
buttonBox = None
settings = QSettings()

def start():
    global indexOfLastUsedCamera 
    global videocapture
    global timer
    global fps
    cameraindex = ui.comboBoxCameraSelect.currentIndex()
    #Only stop the videocapture when the selected camera is changed.
    #Some cameras take a long time to initialize after open is called.
    if not indexOfLastUsedCamera == cameraindex:
        if not videocapture is None:
            videocapture.release()
        #Should be able to do just self.videocapture = cv2.VideoCapture(cameraindex )
        #It worked with my old C170, but the C270 hangs after unpausing.
        #Splitting the calls for the new videocapture and the open keeps the C270 from hanging.
        videocapture = cv2.VideoCapture()
        videocapture.open(cameraindex )
        #Need to add controls for this.
        videocapture.set(cv2.CAP_PROP_FRAME_WIDTH, 1024)
        videocapture.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        indexOfLastUsedCamera  = cameraindex
    timer = QtCore.QTimer()
    timer.timeout.connect(nextFrameSlot)
    timer.start(1000./fps)

def stop():
    global timer
    if not timer is None:
        timer.stop()
    #Do not stop the video capture.
    #Some cameras take a long to to initialize
    #Only stop the camera in the start method when a new camera is selected.
    
def getListOfCameras():
    camerasInfoList = QtMultimedia.QCameraInfo.availableCameras()
    camerasList=[]
    for cameraInfo in camerasInfoList:
        camerasList.append(cameraInfo.description())
    return camerasList

def nextFrameSlot():
    global indexOfLastUsedCamera
    try:
        ret, frame = videocapture.read()
        if ui.checkBoxPause.isChecked():
            return                

        if not ret:
            stop()
            indexOfLastUsedCamera = -1
            start()
            return
    # Assume webcam gives BGR format images
    # May need to add an option or check the format from cv2 somehow
    # Opencv has an option to deliver all frames in a specified format - implement this and then we don't have to assume a format.
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    except:
        return

    ui.CameraView.show()
    ui.CameraView.setImage(frame)

def changeCamera(selectedCameraIndex):
    stop()
    start()
    SaveSettings()

def ButtonHandler(ButtonID,  State):
    print ("ButtonID: " + ButtonID + "  State:" + State)
    
    if ButtonID == "2" and State == "0":
        ui.checkBoxPause.setChecked(True)
        
    if ButtonID == "2" and State == "1":
        ui.checkBoxPause.setChecked(False)
        
    if ButtonID == "3" and State == "0":
        on_buttonSnapshotClicked()

def on_buttonSnapshotClicked():
        snapshot = QApplication.primaryScreen().grabWindow(ui.CameraView.winId())
        filename = datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S") + ".png"
        filename = os.path.join(ui.plainText_FolderName.toPlainText(),  filename)
        if filename:
            snapshot.save(filename,  "png")

def on_SelectFolderClicked():
    directory = str(QFileDialog.getExistingDirectory(None, "Select Directory"))
    if directory:
        ui.plainText_FolderName.clear()
        ui.plainText_FolderName.insertPlainText(directory)
        SaveSettings()

def ChangeComport():
    print("Combobox Comport changed.")
    buttonBox.SetComport(ui.comboBoxComport.currentText())
    SaveSettings()

def SaveSettings():
    global settings
    settings.setValue("ComPort",  ui.comboBoxComport.currentText())
    settings.setValue("Camera", ui.comboBoxCameraSelect.currentText())
    settings.setValue("ImageFolder",  ui.plainText_FolderName.toPlainText())

def LoadSettings():
    global settings
    setComboBoxSelectedItemFromSettings("ComPort",ui.comboBoxComport)
    setComboBoxSelectedItemFromSettings("Camera",ui.comboBoxCameraSelect)
    directory = settings.value("ImageFolder", "")
    ui.plainText_FolderName.clear()
    ui.plainText_FolderName.insertPlainText(directory)
    
def setComboBoxSelectedItemFromSettings( settingName,  combobox):
    global settings
    savedItemName = settings.value(settingName,  "-")
    itemIndex =  combobox.findText(savedItemName )
    if itemIndex>=0:
        combobox.setCurrentIndex(itemIndex)

if __name__ == "__main__":
    QCoreApplication.setOrganizationName("JRE")
    QCoreApplication.setApplicationName("EyeGore")
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    
    ui.comboBoxCameraSelect.addItems(getListOfCameras())
    buttonBox = BoxOButtons()
    ui.comboBoxComport.clear()
    ui.comboBoxComport.addItems(buttonBox.GetComportList())
   
    LoadSettings()
    
    ui.pushButtonSave.clicked.connect(on_buttonSnapshotClicked)
    ui.pushButtonSelectFolder.clicked.connect(on_SelectFolderClicked)
    ui.comboBoxComport.currentIndexChanged.connect(ChangeComport)
    ui.comboBoxCameraSelect.currentIndexChanged.connect(changeCamera)
    
    start()

    buttonBox.SetComport(ui.comboBoxComport.currentText())
    buttonBox.Signal_ButtonState.connect(ButtonHandler)
    buttonBox.start()
    
    MainWindow.show()
    sys.exit(app.exec_())

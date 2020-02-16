from PyQt5 import  QtGui
from PyQt5.QtWidgets import QWidget
from Forms.Ui_WebCamView import Ui_WebCamView

class WebCamView(QWidget, Ui_WebCamView):
    def __init__(self, parent):
            super(QWidget, self).__init__()
            self.setupUi(self)

    def clearImage(self):
        self.viewer.clear()
        
    def setImage(self, Image):
        img = QtGui.QImage(Image, Image.shape[1], Image.shape[0], QtGui.QImage.Format_RGB888)
        pix = QtGui.QPixmap.fromImage(img)
        self.viewer.setPixmap(pix)

    def getPixmap(self):
        return self.viewer.pixmap()

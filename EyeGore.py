from PyQt5 import QtWidgets
from PyQt5.QtCore import QCoreApplication
from Forms.EyeGoreWindow import EyeGoreWindow

if __name__ == "__main__":
    QCoreApplication.setOrganizationName("JRE")
    QCoreApplication.setApplicationName("EyeGore")
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = EyeGoreWindow(MainWindow)
        
    MainWindow.show()
    sys.exit(app.exec_())

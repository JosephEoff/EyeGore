from PyQt5.QtCore import QThread
from PyQt5.QtCore import pyqtSignal
import serial
import serial.tools.list_ports

class BoxOButtons(QThread):
    Signal_ButtonState = pyqtSignal(str,  str)
    
    def __init__(self):
        super(BoxOButtons, self).__init__()
        self.currentSerialPortName = ""
        self.nextComport = ""
        self.keepRunning = True
        self.Comport = None
        
    def __del__(self):
        self.wait()
        
    def cancel(self):
        self.keepRunning=False
   
    def run(self):
        while self.keepRunning:
            self.ChangeSerialPort()
            self.ReadComportAndSendEvents()
            
    def GetComportList(self):
        available_ports = serial.tools.list_ports.comports()
        portnames = []
        for port in available_ports:
                portnames.append(port[0])
                
        return portnames
        
    def SetComport(self,  newComportName):
        self.nextComport = newComportName
        
    def ChangeSerialPort(self):
        if self.currentSerialPortName == self.nextComport :
            return
        
        print ("ChangeSerialPort")
        if not self.Comport is None:
            self.ReleaseComport()

        self.currentSerialPortName = self.nextComport 
       
        if self.Comport is None:
            self.CreateComport()
            
    def CreateComport(self):
        print("Create Comport: " + self.currentSerialPortName  )
        self.Comport = serial.Serial( )
        self.Comport.port =  self.currentSerialPortName 
        self.Comport.baudrate = 115200
        self.Comport.xonxoff = False
        self.Comport.rtscts = False
        self.Comport.dsrdtr = False
        self.Comport.parity = serial.PARITY_NONE
        self.Comport.stopbits = serial.STOPBITS_ONE
        self.Comport.databits = serial.EIGHTBITS
        self.Comport.timeout = 0.5
        self.Comport.open()  
        
    def ReleaseComport(self):
        if not self.Comport is None:
            self.Comport.close()
            self.Comport = None
        
    def ReadComportAndSendEvents(self):
        if self.Comport is None:
            print("Comport not set.")
            return
            
        if not self.Comport.isOpen():
            print ("comport not open")
            return
            
        buttonStateBytes = self.Comport.readline()
        if len(buttonStateBytes) == 0:
            return
        
        buttonState = str(buttonStateBytes, encoding='utf-8')
        buttonState = str.strip(buttonState)
        print("Button State:" + buttonState)
        buttonInfo = buttonState.split(":")
        if len(buttonInfo) == 2:
            self.Signal_ButtonState.emit(buttonInfo[0],  buttonInfo[1])
        

        

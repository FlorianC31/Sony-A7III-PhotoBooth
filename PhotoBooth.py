# -*- coding: utf-8 -*-
"""
Created on Sun Oct 11 13:18:11 2020

@author: Florian CHAMPAIN
"""
import sys,os,glob,win32gui
#sys.coinit_flags = 2

from MainWindow import Ui_PhotoBooth
from Webcam import Thread
from remoteTrigger import Camera
from printer import printer
from relais import relais

from PIL import Image, ExifTags
from PIL.ImageQt import ImageQt

from PyQt5.QtGui import QPixmap, QMovie, QTransform
from PyQt5 import QtWidgets
from PyQt5 import QtCore

import pythoncom

from ntpath import basename

from datetime import datetime

from ctypes import windll





PHOTOFOLDER=r"C:\Users\lord_\Documents\Photos_PhotoBooth\\"
PICTYPE="JPG"
DEVELOPERMODE=True
ROTATE_180=True
WATERMARK=True



class PhotoBooth(Ui_PhotoBooth):
    def __init__(self):
        super(PhotoBooth, self).__init__()
        self.camera=Camera()
        self.ROTATE_180=ROTATE_180

        self.relais = relais(('light', 'fanPrinter', 'fanCam', ''))

        self.initUI()
        self.status=0
              



    def initUI(self):
    
        self.full=False
        self.MainWindow = QtWidgets.QMainWindow()
        self.setupUi(self.MainWindow)

        self.dark = False
        self.ct_active = False
        
        self.movie = QMovie('ressources\Spinner-1s-400px_white.gif')
        self.loading.setMovie(self.movie)
        self.movie.start()
        
        self.buttonExit.clicked.connect(lambda:self.CloseWindow())
        self.buttonRestart.clicked.connect(lambda:self.ShowCam())
        self.buttonPrinter.clicked.connect(lambda:self.send2printer())
        self.buttonDecrease.clicked.connect(lambda:self.changeNbPrint(-1))
        self.buttonIncrease.clicked.connect(lambda:self.changeNbPrint(1))
        self.buttonCancel.clicked.connect(lambda:self.modeVeille())     
        self.veilleButton.clicked.connect(lambda:self.ShowCam()) 
        self.buttonPhoto.clicked.connect(lambda:self.StartCountdown())  
        
        self.widgetPrint.hide()
        self.widgetPhoto.hide()
        self.warning.hide()
        self.countdown.hide()
        
        self.getComptPrint()

        self.MainWindow.show()
        self.ShowCam()
        
        if DEVELOPERMODE:
            rect = win32gui.GetWindowRect(win32gui.FindWindow(None, 'PhotoBooth'))
            win32gui.MoveWindow(win32gui.FindWindow(None, 'PhotoBooth'), rect[0]+3000, rect[1], rect[2]+3000, rect[3], True)
        else:            
            self.widgetDevelopper.hide()
        self.fullScreen()
    
    
    #@pyqtSlot(QImage)
    def setImage(self, image):
        self.camView.setPixmap(QPixmap.fromImage(image))
    
      
        
        
    def fullScreen(self):
        if self.full:
            self.MainWindow.showNormal()
        else:
            self.MainWindow.showFullScreen()
        self.full=not self.full
        #self.MainWindow.resize(1920, 1080)
        #self.centralwidget.resize(1920,1080)
        #self.background.resize(1920,1080)
                  
        
    def CloseWindow(self):
        self.relais.OFF('light')
        self.relais.OFF('fanCam')
        self.relais.OFF('fanPrinter')
        self.camera.close()
        self.StopCam()
        self.MainWindow.close()
        
        
    def showPhoto(self):
        
        pixmap=self.lastPhoto.QImage

        self.viewer.setPixmap(pixmap)
        
        self.widgetPhoto.hide()
        self.widgetPrint.show()
        
        self.changeNbPrint(0)
        

    def StartCountdown(self):
        self.ct_active = True
        self.countdown.setText(QtCore.QCoreApplication.translate("MainWindow", '10'))
        self.countdown.show()
        self.buttonPhoto.hide()
        self.th.StartCountdown(10)

        


    def ShowCam(self):

        self.veilleButton.hide()
        self.widgetPrint.hide()   
        self.widgetPhoto.show()    
        self.lookUp.hide()

        if self.dark:
            self.relais.ON('light')
        self.relais.ON('fanCam')
        
        self.th = Thread()
        self.th.changePixmap.connect(self.setImage)
        self.th.init(self)
        self.th.start()
        
        
        
    def StopCam(self):
        self.camView.clear()
        self.widgetPhoto.hide()  
        try:
            self.th.stop()
        except:
            pass
     
        
        
    def TakePhoto(self):

        self.ct_active = False

        oldPic=photo()
        
        self.camera.Trigger()
        
        self.StopCam()  
        self.countdown.setText(QtCore.QCoreApplication.translate("MainWindow", '0'))
        self.countdown.hide()
        self.buttonPhoto.show()
        
        self.lastPhoto=photo()
        while self.lastPhoto.path==oldPic.path:
            self.lastPhoto=photo()


        if self.lastPhoto.isDarker(1600):
            self.relais.ON('light')
            self.dark=True
        self.lastPhoto.watermark()

        self.showPhoto()


    def modeVeille(self):
        self.StopCam()
        self.veilleButton.show()
        self.relais.OFF('light')
        self.relais.OFF('fanCam')
        self.relais.OFF('fanPrinter')
        
    def changeNbPrint(self, i):
        if i==0: # Init
            self.nbPrint=1
        else:
            self.nbPrint=min(max(1,self.nbPrint+i),6)
        self.nbPrintLabel.setText(QtCore.QCoreApplication.translate("MainWindow", str(self.nbPrint)))

        
    def send2printer(self):
        self.relais.ON('fanPrinter')
        for i in range(self.nbPrint):
            printer(self.lastPhoto, self.ROTATE_180)
        self.setComptPrint(self.nbPrint)
        self.ShowCam()
        
        
    def getComptPrint(self):
        file1 = open("compteur.txt","r")
        self.comptPrint=int(file1.read())
        file1.close
        self.compteur.setText(QtCore.QCoreApplication.translate("MainWindow", str(self.comptPrint)+' photos restantes'))

    def setComptPrint(self,n):
        self.comptPrint-=n
        file1 = open("compteur.txt","w")
        file1.write(str(self.comptPrint))
        file1.close
        self.compteur.setText(QtCore.QCoreApplication.translate("MainWindow", str(self.comptPrint)+' photos restantes'))
        
        file2 = open("Printlog.csv","a")
        line=[]
        line.append(str(datetime.now()))
        line.append(self.lastPhoto.name)
        line.append(str(n))
        file2.write(';'.join(line))
        file2.close



class photo():
    def __init__(self):
        self.width=1620
        self.height=1080
        self.folder=PHOTOFOLDER
        self.PicType=PICTYPE
        try:
            list_of_files = glob.glob(self.folder + '*.' + self.PicType)
            self.path=max(list_of_files, key=os.path.getctime)
            self.name=basename(self.path)
            self.Image=Image.open(self.path)
        except:
            self.path=''

    
    def isDarker(self,ISOmax):
        exif = { ExifTags.TAGS[k]: v for k, v in self.Image._getexif().items() if k in ExifTags.TAGS }
        ISO=exif['ISOSpeedRatings']
        return(ISO>=ISOmax)
    
    def watermark(self):
        
        WATERMARK="ressources\logo_blanc_sur_transparent.png"
        SIZE=(6,4) #in inch
        RESOLUTION=300 #ppi
        
        
        self.Image = Image.open(self.path)
        self.Image.thumbnail((SIZE[0]*RESOLUTION,SIZE[1]*RESOLUTION), Image.ANTIALIAS)

        if ROTATE_180:
            self.Image=self.Image.transpose(Image.ROTATE_180)

        if WATERMARK:
            watermark = Image.open(WATERMARK)
            width, height = self.Image.size
            transparent = Image.new('RGBA', (width, height), (0,0,0,0))
            transparent.paste(self.Image, (0,0))
            transparent.paste(watermark, (SIZE[0]*RESOLUTION-watermark.size[0]-20,SIZE[1]*RESOLUTION-watermark.size[1]-40), mask=watermark)
        else:
            transparent.paste(self.Image, (0, 0))

        self.Image2print=transparent
        transparent=transparent.resize((1620,1080))
        self.QImage=QPixmap.fromImage(ImageQt(transparent))
       

 


if __name__ == '__main__':
    pythoncom.CoInitialize()
    app = QtWidgets.QApplication(sys.argv)
    PhotoBooth=PhotoBooth()
    sys.exit(app.exec_())

    #test_photo=photo()
    #test_photo.folder='/home/florian/Téléchargements/onedrive/docs/images'
    #print(test_photo.isDarker(1600))

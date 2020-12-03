# -*- coding: utf-8 -*-
"""
Created on Sun Oct 11 13:22:40 2020

@author: Florian CHAMPAIN
"""

import cv2
from PyQt5 import QtCore
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QImage
from datetime import datetime

class Thread(QThread):
    changePixmap = pyqtSignal(QImage)
    
    
    def init(self,PhotoBooth):
        cv2.destroyAllWindows()
        self.PhotoBooth=PhotoBooth
        self.setResolution(1)
        self.cdRunning=False
        self.StartTime=datetime.now()
        
    def ChangeResolution(self):
        resolutionID=self.resolutionID+1
        if resolutionID==3:
            resolutionID=0
        self.setResolution(resolutionID)
                
        
    def setResolution(self,ResolutionID):
        
        resolutions=((1920,1080),(1280,720),(640,360))
        
        if ResolutionID=='old':
            self.resolution=resolutions[self.oldResolutionID]
            self.resolutionID=self.oldResolutionID
        else:
            self.resolution=resolutions[ResolutionID]
            self.resolutionID=ResolutionID
            
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution[0])
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution[1])
        
        self.cropLeft=int((1920-1620)/(2*1920)*self.resolution[0])
        self.cropRight=int((1-(1920-1620)/(2*1920))*self.resolution[0])
        
        #self.mainWindow.ButtonResolution.setText(QtCore.QCoreApplication.translate("MainWindow", str(self.resolution)))
        
    
    
    def StartCountdown(self,duree):
        self.cdStart=datetime.now()
        self.cdRunning=True
        self.cdValue=-1
        self.duree=duree


    def run(self):
        
        broken=0
        self.runing=True
        self.setResolution(1)
        
        while self.runing:
            cv2.destroyAllWindows()
            try:
                self.cap.release()
            except:
                pass
            
            self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution[0])
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution[1])
            
    
    
            while self.runing:
                ret, frame = self.cap.read()
                if ret:
                    
                    #self.mainWindow.labelCompteur.setText(QtCore.QCoreApplication.translate("MainWindow", str(frame.shape)))
                    
                    
                    # Mirror Flip
                    frame = cv2.flip(frame, 1)  
                    
                    # Crop
                    frame = frame[0:self.resolution[1], self.cropLeft:self.cropRight] 
                    
                    # Resize
                    if self.resolutionID>0:
                        frame = cv2.resize(frame,(1620,1080),fx=0,fy=0, interpolation = cv2.INTER_CUBIC)
                    
                    
                    if self.cdRunning:
                        duree=datetime.now()-self.cdStart
                        if duree.seconds>self.cdValue:
                            self.cdValue=duree.seconds
                            self.PhotoBooth.countdown.setText(QtCore.QCoreApplication.translate("MainWindow", str(self.duree-self.cdValue-1)))
                        if duree.seconds==self.duree-3:
                            self.PhotoBooth.countdown.hide()
                            self.PhotoBooth.lookUp.show()
                        if duree.seconds==self.duree-2:
                            self.PhotoBooth.TakePhoto()
                    else:
                        duree=datetime.now()-self.StartTime
                        if duree.seconds>=60:
                            self.PhotoBooth.modeVeille()

                    

                    # Send to Qt
                    rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    h, w, ch = rgbImage.shape
                    bytesPerLine = ch * w
                    convertToQtFormat = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format_RGB888)
                    self.changePixmap.emit(convertToQtFormat)

    
    
                else:
                    broken+=1
                    brokenMsg=str(broken)+" broken frames"
                    self.Photobooth.warning.setText(QtCore.QCoreApplication.translate("MainWindow", brokenMsg))
                    self.Photobooth.warning.show()
                    self.cap.release()
                    break
                
    

        
                
    def stop(self):
        self.changePixmap.disconnect()
        self.runing=False
        self.cap.release()
        cv2.destroyAllWindows()
        del(self)
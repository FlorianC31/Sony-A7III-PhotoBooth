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


class CamThread(QThread):
    changePixmap = pyqtSignal(QImage)

    def __init__(self, photobooth):
        super(CamThread, self).__init__()

        cv2.destroyAllWindows()
        self.PhotoBooth = photobooth
        self.set_resolution(1)
        self.StartTime = datetime.now()
        self.runing = False
        self.changePixmap.connect(photobooth.set_image)

        self.resolution = None
        self.cap = None
        self.cropLeft = None
        self.cropRight = None

    def set_resolution(self, resolution_id):

        resolutions = ((1920, 1080), (1280, 720), (640, 360))
        self.resolution = resolutions[resolution_id]

        self.cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution[0])
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution[1])

        self.cropLeft = int((1920-1620) / (2*1920) * self.resolution[0])
        self.cropRight = int((1-(1920-1620) / (2*1920)) * self.resolution[0])

    def launch_cam(self):
        cv2.destroyAllWindows()
        self.cap.release()

        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution[0])
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution[1])

    def run(self):
        
        broken = 0
        self.runing = True
        self.set_resolution(1)

        self.launch_cam()

        while self.runing:
            ret, frame = self.cap.read()
            if ret:

                # Check if the picture is full black
                if self.is_black(frame):
                    self.launch_cam()
                else:
                    self.PhotoBooth.camView.show()

                # Mirror Flip
                frame = cv2.flip(frame, 1)

                # Rotation 180°
                if self.PhotoBooth.ROTATE_180:
                    frame = cv2.rotate(frame, cv2.cv2.ROTATE_180)

                # Crop
                frame = frame[0:self.resolution[1], self.cropLeft:self.cropRight]

                # Resize
                if self.resolution[1] < 1920:
                    frame = cv2.resize(frame, (1620, 1080), fx=0, fy=0, interpolation=cv2.INTER_CUBIC)

                # Send to Qt
                rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb_image.shape
                bytes_per_line = ch * w
                convert_to_qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
                self.changePixmap.emit(convert_to_qt_format)

            else:
                # print('Broken Frame')
                broken += 1
                broken_msg = str(broken)+" broken frames"
                self.Photobooth.warning.setText(QtCore.QCoreApplication.translate("MainWindow", broken_msg))
                self.Photobooth.warning.show()
                self.cap.release()
                break

    def is_black(self, frame):
        # Check if less than 10% of the picture is not black
        grey_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        if cv2.countNonZero(grey_frame) < self.resolution[0] * self.resolution[1]*0.1:
            # print("The image is full black")
            return True
        else:
            return False
                
    def stop(self):
        self.changePixmap.disconnect()
        self.runing = False
        self.cap.release()
        cv2.destroyAllWindows()
        # del self

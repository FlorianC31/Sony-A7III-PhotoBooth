# -*- coding: utf-8 -*-
"""
Created on Sun Oct 11 13:18:11 2020

@author: Florian CHAMPAIN
"""
import sys
import os
import glob
import win32gui

from MainWindow import Ui_PhotoBooth
from Webcam import CamThread
from remoteTrigger import Camera
from printer import printer
from relais import Relais
from logger import log

from PIL import Image, ExifTags
from PIL.ImageQt import ImageQt

from PyQt5.QtGui import QPixmap, QMovie, QTransform
from PyQt5 import QtWidgets
from PyQt5 import QtCore, QtGui

import pythoncom

from CPU_temp import upper_fan_controller

from ntpath import basename

from datetime import datetime
from time import sleep

from ctypes import windll

from threading import Thread
from setproctitle import setproctitle


PHOTOFOLDER = r"C:\Photos_PhotoBooth\\"
PICTYPE = "JPG"
DEVELOPERMODE = False
ROTATE_180 = True
WATERMARK = True
SCALE = 1.5
MAX_ISO = 480  # 480 for Rx10-III / 1600 for a7-III
COUNTDOWN = 6  # 10s

WTMRK = r"ressources\logo_blanc_sur_transparent.png"
SIZE = (6, 4)  # in inch
RESOLUTION = 300  # ppi


class PhotoBooth(Ui_PhotoBooth):
    def __init__(self, app):
        super(PhotoBooth, self).__init__()

        self.app = app

        self.dark = False
        self.veille_countdown = False
        self.fullscreen = False

        self.action_done = False

        self.movie = QMovie(r'ressources\Spinner-1s-400px_white.gif')

        self.camera = Camera(SCALE)
        self.ROTATE_180 = ROTATE_180

        self.relais = Relais(('light', 'fanPrinter', 'fanCam', ''))

        self.cam_thread = None
        self.cd_thread = None
        self.lastPhoto = None

        self.veille_th = None

        self.MainWindow = QtWidgets.QMainWindow()
        self.status = 0
        self.nbPrint = 0
        self.comptPrint = 0
        self.init_ui()

        self.printer_fan_thread = None
        self.upper_fan_th = Thread(target=upper_fan_controller, args=[self.relais])
        self.upper_fan_th.start()

    def init_ui(self):
        log("Note", "Initialisation de l'UI", "PhotoBooth")

        self.setupUi(self.MainWindow)

        if SCALE != 1:
            self.set_scale()

        self.loading.setMovie(self.movie)
        self.movie.start()
        
        self.buttonExit.clicked.connect(lambda: self.close_window())
        self.buttonRestart.clicked.connect(lambda: self.show_cam(1))
        self.buttonPrinter.clicked.connect(lambda: self.send2printer())
        self.buttonDecrease.clicked.connect(lambda: self.change_nb_print(-1))
        self.buttonIncrease.clicked.connect(lambda: self.change_nb_print(1))
        self.buttonCancel.clicked.connect(lambda: self.mode_veille(0))
        self.veilleButton.clicked.connect(lambda: self.show_cam(2))
        self.buttonPhoto.clicked.connect(lambda: self.start_countdown())
        
        self.widgetPrint.hide()
        self.widgetPhoto.hide()
        self.warning.hide()
        self.countdown.hide()
        self.flash.hide()
        
        self.get_compt_print()

        self.MainWindow.show()
        self.show_cam(0)
        
        if not DEVELOPERMODE:
            self.full_screen()
            # self.widgetDevelopper.hide()

    def set_scale(self):
        log("Note", "Mise a l'echelle des tailles de police", "PhotoBooth")
        self.sef_font(self.MainWindow)
        self.sef_font(self.compteur)
        self.sef_font(self.nbPrintLabel)
        self.sef_font(self.buttonIncrease)
        self.sef_font(self.buttonDecrease)
        self.sef_font(self.buttonPrinter)
        self.sef_font(self.buttonRestart)
        self.sef_font(self.buttonCancel)
        self.sef_font(self.buttonPhoto)
        self.sef_font(self.veilleButton)
        self.sef_font(self.countdown)
        self.sef_font(self.lookUp)

    def sef_font(self, qt_elm):
        font_info = qt_elm.fontInfo()
        font = QtGui.QFont()

        font.setFamily(font_info.family())
        font.setBold(font_info.bold())
        font.setItalic(font_info.italic())

        ref_font_size = font_info.pointSize() 
        font.setPointSize(int(round(ref_font_size / SCALE, 0)))

        ref_font_weight = font_info.weight() 
        font.setWeight(int(round(ref_font_weight / SCALE, 0)))
                
        qt_elm.setFont(font)

    def set_image(self, image):
        self.camView.setPixmap(QPixmap.fromImage(image))

    def full_screen(self):
        log("Note", "Passeage en plein ecran", "PhotoBooth")
        if self.fullscreen:
            self.MainWindow.showNormal()
        else:
            self.MainWindow.showFullScreen()
        self.fullscreen = not self.fullscreen
        
    def close_window(self):
        log("Admin", "Click sur le bouton de fermeture", "PhotoBooth")
        with open("run.txt", "w") as file:
            file.write("0")
        self.stop_veille()
        self.relais.close()
        self.camera.close()
        self.stop_cam()
        self.MainWindow.close()
        
    def show_photo(self):
        log("Note", "Affichage de la derniere photo", "PhotoBooth")
        pixmap = self.lastPhoto.QImage

        self.viewer.setPixmap(pixmap)

        self.widgetPrint.show()
        
        self.change_nb_print(0)

    def start_countdown(self):
        log("user", "Click sur le bouton de prise de photo", "PhotoBooth")
        self.action_done = True
        self.countdown.setText(QtCore.QCoreApplication.translate("MainWindow", str(COUNTDOWN)))
        self.countdown.show()
        self.buttonPhoto.hide()
        self.cd_thread = Thread(target=self.countdown_thread)
        self.cd_thread.start()

    def countdown_thread(self):
        cd = COUNTDOWN
        while cd > 0:
            sleep(1)
            cd -= 1

            self.countdown.setText(QtCore.QCoreApplication.translate("MainWindow", str(cd)))

            if cd == COUNTDOWN - 2 and COUNTDOWN > 4 :
                log("Note", "Focus Photo initial", "PhotoBooth")
                focus_thread = Thread(target=self.camera.focus)
                focus_thread.start()

            elif cd == 2:
                self.loading.hide()

                self.camView.hide()
                log("Note", "Arret du flux video", "PhotoBooth")
                stop_thread = Thread(target=self.stop_cam)
                stop_thread.start()
                self.camView.clear()

                self.lookUp.show()
                self.camView.hide()

            elif cd == 1:
                log("Note", "Focus Photo final", "PhotoBooth")
                focus_thread = Thread(target=self.camera.focus, args=[True])
                focus_thread.start()

        self.take_photo()

        self.camView.show()

    def show_cam(self, boutton):
        if boutton == 1:
            log("User", "Click sur le bouton de relance photo", "PhotoBooth")
        elif boutton == 2:
            log("User", "Click sur le bouton de sortie de la mise en veille", "PhotoBooth")

        self.buttonPhoto.hide()
        self.action_done = True
        self.camView.hide()
        self.veilleButton.hide()
        self.widgetPrint.hide()   
        self.widgetPhoto.show()    
        self.lookUp.hide()


        log("Note", "Lancement du flux video", "PhotoBooth")
        self.cam_thread = CamThread(self)
        self.cam_thread.start()

        if self.dark:
            self.relais.on('light')

        self.stop_veille()
        self.veille_countdown = True
        self.veille_th = Thread(target=self.veille_thread)
        self.veille_th.start()

    def veille_thread(self):
        timer = 0
        while timer < 60 and self.veille_countdown and self.camera.PhotoBoothWindow.is_open():
            timer += 1
            if self.action_done:
                timer = 0
                self.action_done = False
            # print("Veille thread - ", str(timer))
            sleep(1)
        if timer == 60:
            log("User", "Mise en veille", "Veille")
            self.mode_veille(0)

    def mode_veille(self, button):
        if button == 1:
            log("user", "Click sur le bouton de mise en veille", "PhotoBooth")
        self.stop_cam()
        self.veilleButton.show()
        self.relais.off('light')

    def stop_veille(self):
        self.veille_countdown = False
        if self.veille_th:
            while self.veille_th.is_alive():
                pass
        
    def stop_cam(self):
        # print(cam_thread)
        try:
            self.cam_thread.stop()
            self.cam_thread.quit()
            del self.cam_thread
        except AttributeError:
            pass
        # print("Closing")
        # print(cam_thread)
        
    def take_photo(self):
        log("Note", "Prise de la photo", "PhotoBooth")

        old_pic = Photo()

        self.camera.trigger_on()
        self.flash.show()
        sleep(0.4)
        self.flash.hide()
        self.camera.trigger_off()
        self.widgetPhoto.hide()
        self.loading.show()
        self.countdown.hide()

        self.lastPhoto = Photo()
        while self.lastPhoto.path == old_pic.path:
            self.lastPhoto = Photo()

        # self.buttonPhoto.show()

        if self.lastPhoto.is_darker(MAX_ISO):
            log("user", "ISO trop eleve, allumage de la lumiere", "PhotoBooth")
            self.relais.on('light')
            self.dark = True
        self.lastPhoto.watermark()

        self.show_photo()

    def change_nb_print(self, i):
        log("user", "Click sur les boutons de changement du nombre d'impressions", "PhotoBooth")
        self.action_done = True
        if i == 0:
            self.nbPrint = 1
        else:
            self.nbPrint = min(max(1, self.nbPrint+i), 6)
        self.nbPrintLabel.setText(QtCore.QCoreApplication.translate("MainWindow", str(self.nbPrint)))

        if self.nbPrint == 1:
            self.gray(self.buttonDecrease)
        elif self.nbPrint == 6:
            self.gray(self.buttonIncrease)
        else:
            self.ungray(self.buttonDecrease)
            self.ungray(self.buttonIncrease)

    def ungray(self, button):
        button.setStyleSheet("background-color: transparent;\ncolor: rgb(255, 255, 255);")

    def gray(self, button):
        button.setStyleSheet("background-color: transparent;\ncolor: rgb(127, 127, 127);")

    def printer_fan_controler(self):
        log("Note", "Mise en route du ventilo de l'imprimante", "PhotoBooth")
        self.relais.on('fanPrinter')
        sleep(60)
        self.relais.off('fanPrinter')
        log("Note", "Extinction du ventilo de l'imprimante", "PhotoBooth")

    def send2printer(self):
        log("user", "Click sur le bouton d'impression", "PhotoBooth")
        self.action_done = True
        for _ in range(self.nbPrint):
            printer(self.lastPhoto)

        self.printer_fan_thread = Thread(target=self.printer_fan_controler)
        self.printer_fan_thread.start()

        self.set_compt_print(self.nbPrint)
        self.show_cam(0)

    def get_compt_print(self):
        with open("compteur.txt", "r") as file:
            self.comptPrint = int(file.read())
        self.show_compt_print()

    def set_compt_print(self, n):
        self.comptPrint -= n
        with open("compteur.txt", "w") as file:
            file.write(str(self.comptPrint))
        self.show_compt_print()

        with open("Printlog.csv", "a") as csvFile:
            line = [str(datetime.now()), self.lastPhoto.name, str(n) + '\n']
            csvFile.write(';'.join(line))

    def show_compt_print(self):
        text = str(self.comptPrint)+'\nphotos\nrestantes'
        self.compteur.setText(QtCore.QCoreApplication.translate("MainWindow", text))


class Photo:
    def __init__(self):
        self.width = 1620
        self.height = 1080
        self.folder = PHOTOFOLDER
        self.PicType = PICTYPE
        self.Image2print = ''
        self.QImage = ''

        list_of_files = glob.glob(self.folder + '*.' + self.PicType)
        if list_of_files:
            self.path = max(list_of_files, key=os.path.getctime)
            self.name = basename(self.path)
            self.Image = Image.open(self.path)
        else:
            self.path = ''

    def is_darker(self, iso_max):
        exif = {ExifTags.TAGS[k]: v for k, v in self.Image._getexif().items() if k in ExifTags.TAGS}
        iso = exif['ISOSpeedRatings']
        return iso >= iso_max

    def watermark(self):

        self.Image = Image.open(self.path)
        self.Image.thumbnail((SIZE[0]*RESOLUTION, SIZE[1]*RESOLUTION), Image.ANTIALIAS)

        if ROTATE_180:
            self.Image = self.Image.transpose(Image.ROTATE_180)

        width, height = self.Image.size
        transparent = Image.new('RGBA', (width, height), (0, 0, 0, 0))

        if WTMRK:
            watermark = Image.open(WTMRK)
            transparent.paste(self.Image, (0, 0))
            pos_x = SIZE[0] * RESOLUTION - watermark.size[0] - 20
            pos_y = SIZE[1] * RESOLUTION - watermark.size[1] - 40
            transparent.paste(watermark, (pos_x, pos_y), mask=watermark)
        else:
            transparent.paste(self.Image, (0, 0))

        self.Image2print = transparent
        transparent = transparent.resize((1620, 1080))
        self.QImage = QPixmap.fromImage(ImageQt(transparent))


def run_photobooth():
    process_name = "PhotoBooth-run"
    setproctitle(process_name)

    log("WAYPOINT", "Lancement d'un nouveau processus " + process_name, process_name)

    with open("run.txt", "w") as file:
        file.write("1")

    pythoncom.CoInitialize()
    new_app = QtWidgets.QApplication(sys.argv)
    PhotoBooth(new_app)
    log("WAYPOINT", "Fermeture normale du processus " + process_name, process_name)
    sys.exit(new_app.exec_())


if __name__ == '__main__':
    run_photobooth()

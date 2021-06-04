import keyboard
import time
import win32com.client
import win32gui
import pywinauto
import os, sys
#import ftd2xx as ft
import time, sys
import win32print
import win32ui
from PIL import Image, ImageWin
import sys,os,glob,win32gui

from MainWindow import Ui_PhotoBooth
from Webcam import CamThread
from remoteTrigger import Camera
from printer import printer
#from relais import relais

from PIL import Image, ExifTags
from PIL.ImageQt import ImageQt

from PyQt5.QtGui import QPixmap, QMovie
from PyQt5 import QtWidgets
from PyQt5 import QtCore

import pythoncom

from ntpath import basename

from datetime import datetime
from PyQt5 import QtCore, QtGui, QtWidgets
import cv2
from PyQt5 import QtCore
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QImage
from datetime import datetime
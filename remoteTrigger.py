import keyboard
import time
import win32com.client
import win32gui
import pywinauto
import os
import sys

from threading import Thread


class Window:
    def __init__(self, window_name, scale=1):
        self.name = window_name
        self.scale = scale
        self.x_init = 0
        
    def is_open(self):
        return self.get_hwnd() > 0

    def show(self):
        if self.is_open():
            shell = win32com.client.Dispatch("WScript.Shell")
            shell.SendKeys('%')
            while not self.is_focus():
                time.sleep(0.1)
                win32gui.SetForegroundWindow(self.get_hwnd())
        else:
            print('ERROR: Enable to show ', self.name, ' because it is not opened')
            sys.exit(1)

    def get_hwnd(self):
        return win32gui.FindWindow(None, self.name)

    def x_move(self, x, absolute=True):
        if self.is_open():
            rect = win32gui.GetWindowRect(self.get_hwnd())
            width = rect[2] - rect[0]
            height = rect[3] - rect[1]
            if absolute:
                win32gui.MoveWindow(self.get_hwnd(), x, rect[1], width, height, True)
            else:
                win32gui.MoveWindow(self.get_hwnd(), rect[0] + x, rect[1], width, height, True)

    def y_move(self, y, absolute=True):
        if self.is_open():
            rect = win32gui.GetWindowRect(self.get_hwnd())
            width = rect[2] - rect[0]
            height = rect[3] - rect[1]
            if absolute:
                win32gui.MoveWindow(self.get_hwnd(), rect[0], y, width, height, True)
            else:
                win32gui.MoveWindow(self.get_hwnd(), rect[0], rect[1] + y, width, height, True)

    def resize(self, w, h):
        if self.is_open():
            rect = win32gui.GetWindowRect(self.get_hwnd())
            win32gui.MoveWindow(self.get_hwnd(), rect[0], rect[1], w, h, True)

    def click(self, x_relative, y_relative, double_click=False):
        if self.is_open():
            self.show()
            rect = win32gui.GetWindowRect(self.get_hwnd())
            x = rect[0] + int(x_relative * self.scale)
            y = rect[1] + int(y_relative * self.scale)

            if double_click:
                pywinauto.mouse.double_click(button='left', coords=(x, y))
            else:
                pywinauto.mouse.click(button='left', coords=(x, y))

        else:
            print('ERROR:', self.name, 'is not opened')
            sys.exit(1)

    def is_focus(self):
        return win32gui.GetForegroundWindow() == self.get_hwnd()

    def set_x_init(self, x=0):
        if x == 0:
            rect = win32gui.GetWindowRect(self.get_hwnd())
            self.x_init = rect[0]
        else:
            self.x_init = x
    
    
class Remote(Window):

    def is_disconet_msg(self):
        return self.check_size(427, 173)

    def is_pre_remote(self):
        return self.check_size(930, 376)

    def check_size(self, w, h):
        rect = win32gui.GetWindowRect(self.get_hwnd())
        width = int((rect[2] - rect[0]) / self.scale)
        height = int((rect[3] - rect[1]) / self.scale)
        if rect:
            return w - 1 < width < w + 1 and h - 1 < height < h + 1
        else:
            return False

    def acknowledge_disconect(self):
        self.click(354, 132)
        time.sleep(0.1)
    
    def close(self):
        self.click(841, 340)
        
    def refresh(self):
        self.click(712, 340)
        time.sleep(5)
        
    def launch_cam(self):
        time.sleep(2)
        
        # Wait for the camera is available
        while self.is_disconet_msg():
            self.acknowledge_disconect()
            self.refresh()
            time.sleep(1)

        # launch of the final Remote Window
        while self.is_pre_remote():
            self.click(89, 78, True)
            time.sleep(3)
            keyboard.press('Enter')
            time.sleep(0.2)
            keyboard.release('Enter')

    def is_operationnal(self):
        cond_a = self.is_open()
        cond_b = not self.is_pre_remote()
        cond_c = not self.is_disconet_msg()
        return cond_a and cond_b and cond_c


class Camera:
    def __init__(self, scale):
        self.PhotoBoothWindow = Window("PhotoBooth", scale)
        self.ImagingWindow = Window("Imaging Edge Desktop", scale)
        self.RemoteWindow = Remote("Remote", scale)
        self.ViewerWindow = Remote("Viewer", scale)

        self.scale = scale

        self.chek_connect_th = None
        self.launch()
        self.running = True

        if self.ViewerWindow.is_open():
            self.ViewerWindow.close()

    def close(self):
        self.RemoteWindow.x_move(self.RemoteWindow.x_init)
        if self.ViewerWindow.is_open():
            self.ViewerWindow.x_move(300)
        self.running = False

    def trigger_on(self):
        self.RemoteWindow.x_move(6000, False)
        self.RemoteWindow.show()
        keyboard.press('&')

    def trigger_off(self):
        keyboard.release('&')
        self.PhotoBoothWindow.show()
        self.RemoteWindow.x_move(self.RemoteWindow.x_init)

    def focus(self, preshot=False):
        self.RemoteWindow.x_move(6000, False)
        self.RemoteWindow.show()

        if preshot:
            keyboard.press('g')
            time.sleep(0.5)
            keyboard.release('g')
        else:
            keyboard.press('g')
            time.sleep(2)
            keyboard.release('g')
            keyboard.press('g')
            keyboard.release('g')

        self.PhotoBoothWindow.show()
        self.RemoteWindow.x_move(self.RemoteWindow.x_init)

    def launch(self):
        while self.chek_connect_th:
            pass  # print("Le thread tourne encore")
        # Open the main Imaging Edge programm
        nb_iter = 1
        if not self.ImagingWindow.is_open():
            print("Ouverture de Imaging Edge Desktop - " + str(int(nb_iter/20*100)) + "%")
            os.popen(r"C:\Program Files\Sony\Imaging Edge Desktop\ied.exe")
            while not self.ImagingWindow.is_open():
                time.sleep(1)
                nb_iter += 1
                print("Ouverture de Imaging Edge Desktop - " + str(int(nb_iter/20*100)) + "%")
            print("Imaging Edge Desktop est ouvert")

        if not self.RemoteWindow.is_open():
            time.sleep(1)

            while not self.ImagingWindow.is_focus():
                self.ImagingWindow.show()
                time.sleep(1)

            nb_iter = 1
            print("Ouverture de Remote Window - " + str(int(nb_iter/20*100)) + "%")
            self.ImagingWindow.click(665, 160)
            while not self.RemoteWindow.is_open():
                time.sleep(1)
                nb_iter += 1
                print("Ouverture de Remote Window - " + str(int(nb_iter/20*100)) + "%")
            print("Remote Window est ouvert")
        
        # If the Remote application can not find the Camera and send an error message
        time.sleep(2)
        if not self.RemoteWindow.is_operationnal():
            print("APN pas encore opérationnel")
            self.RemoteWindow.launch_cam()

        self.RemoteWindow.set_x_init(1400)
        self.ImagingWindow.x_move(800)

        self.close_liveview()
        self.PhotoBoothWindow.show()
        # self.trigger_on()
        # self.trigger_off()

        self.chek_connect_th = Thread(target=self.chek_connect)
        # self.chek_connect_th.start()

    def close_liveview(self):
        time.sleep(2)
        rect = win32gui.GetWindowRect(self.RemoteWindow.get_hwnd())
        width = int((rect[2] - rect[0]) / self.scale)
        if width > 500:
            self.ImagingWindow.show()
            self.RemoteWindow.show()
            time.sleep(1)
            keyboard.press('Ctrl')
            keyboard.press('l')
            keyboard.release('l')
            keyboard.release('Ctrl')
        # sys.exit(0)

    def chek_connect(self):
        while not self.RemoteWindow.is_disconet_msg() and self.running:
            # print("Thread de check en cours")
            time.sleep(5)
        if self.running:
            self.launch()


if __name__ == '__main__':
    # RemoteWindow = Remote("Remote", 1.5)
    # RemoteWindow.x_move(300)

    test_camera = Camera(1.5)
    # print(test_camera.is_disconet_msg())

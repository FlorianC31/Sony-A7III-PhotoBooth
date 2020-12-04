import keyboard
import time
import win32com.client
import win32gui
import pywinauto
import os, sys



class Window():
    def __init__(self,WindowName):
        self.name=WindowName
        
    def isOpen(self):
        return self.getHwnd()>0
        
       
    def Show(self):
        if self.isOpen():
            shell = win32com.client.Dispatch("WScript.Shell")
            shell.SendKeys('%')
            while not self.isFocus():
                time.sleep(0.1)
                win32gui.SetForegroundWindow(self.getHwnd())
        else:
            print('ERROR:',self.name,'is not opened')
            sys.exit(1)
            
        
    def getHwnd(self):
        return win32gui.FindWindow(None, self.name)
        

    
    def Move(self,X,delta=False):
        rect = win32gui.GetWindowRect(self.getHwnd())
        if delta:
            win32gui.MoveWindow(self.getHwnd(), rect[0] + X, rect[1], rect[2]+X, rect[3], True)
        else:
            win32gui.MoveWindow(self.getHwnd(), X, rect[1], X, rect[3], True)
    
    def Click(self,Xrelative,Yrelative,doubleClick=False):
        if self.isOpen():
            self.Show()
            rect = win32gui.GetWindowRect(self.getHwnd())
    
            pywinauto.mouse.click(button='left', coords=(rect[0]+Xrelative, rect[1]+Yrelative))
    
            if doubleClick:
                time.sleep(0.3)
                pywinauto.mouse.click(button='left', coords=(rect[0]+Xrelative, rect[1]+Yrelative))

        else:
            print('ERROR:',self.name,'is not opened')
            sys.exit(1)
    

    def isFocus(self):
        return win32gui.GetForegroundWindow()==self.getHwnd()
    
    
class Remote(Window):
    
    def isPreRemote(self):
        try:
            rect=win32gui.GetWindowRect(self.getHwnd())
            return rect[2]-rect[0]==930 and rect[3]-rect[1]==376
        except:
            return False

    def isDisconetMsg(self):
        try:
            rect=win32gui.GetWindowRect(self.getHwnd())
            return rect[2]-rect[0]==427 and  rect[3]-rect[1]==159
        except:
            return False
    
    
    def AgreeDisconect(self):
        self.Click(354,132)
        time.sleep(0.1)
    
    def Close(self):
        self.Click(841,340)
        
    def Refresh(self):
        self.Click(712,340)
        time.sleep(5)
        
    def LaunchCam(self):
        
        time.sleep(2)
        
        # Wait for the camera is available
        while self.isDisconetMsg():
            self.AgreeDisconect()
            self.Refresh()


        # launch of the final Remote Window
        while self.isPreRemote():
            self.Click(89,78,True)
            time.sleep(3)
            keyboard.press('Enter')
            time.sleep(0.2)
            keyboard.release('Enter')

        
    def isOperationnal(self):
        a=self.isOpen()
        b=not self.isPreRemote()
        c=not self.isDisconetMsg()
        return a and b and c

        
        
    


class Camera:
    def __init__(self):
        
        self.PhotoBoothWindow=Window("PhotoBooth")
        self.ImagingWindow=Window("Imaging Edge Desktop")
        self.RemoteWindow=Remote("Remote")
        self.ViewerWindow=Remote("Viewer")
        
        self.Launch()
        self.RemoteWindow.Move(3000,True)
        if self.ViewerWindow.isOpen():
            self.ViewerWindow.Move(3000,True)


    def close(self):
        self.RemoteWindow.Move(300)
        if self.ViewerWindow.isOpen():
            self.ViewerWindow.Move(300)


    def Trigger(self):

        self.RemoteWindow.Show()

        keyboard.press('&')
        time.sleep(2)
        keyboard.release('&')
        
        self.PhotoBoothWindow.Show()

        

        
        
    def Launch(self):
        
        # Open the main Imaging Edge programm
        if not self.ImagingWindow.isOpen():
            os.popen("C:\Program Files\Sony\Imaging Edge Desktop\ied.exe")
            while not self.ImagingWindow.isOpen():
                pass
            time.sleep(1)
            
        if not self.RemoteWindow.isOpen():
            self.ImagingWindow.Click(665,160)
            while not self.RemoteWindow.isOpen():
                time.sleep(1)

        
        # If the Remote application can not find the Camera and send an error message
        if not self.RemoteWindow.isOperationnal():
            self.RemoteWindow.LaunchCam()

             
             
if __name__ == '__main__':
    Camera=Camera()
    time.sleep(5)
    Camera.close()

from relais import relais
import time

relais=relais(('light','fanCam','fanPrinter',''))


relais.ON('light')
time.sleep(0.005)
relais.ON('light')
relais.OFF('fanPrinter')
time.sleep(5)

for i in range(10):
    relais.ON('light')
    time.sleep(0.005)
    relais.ON('light')
    relais.OFF('fanCam')
    time.sleep(0.995)
    relais.OFF('light')
    time.sleep(0.005)
    relais.OFF('light')
    relais.ON('fanCam')
    time.sleep(0.995)
time.sleep(3) 
relais.OFF('fanCam')
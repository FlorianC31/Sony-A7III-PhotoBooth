from relais import Relais
import time

relais=Relais(('light', 'fanCam', 'fanPrinter', ''))


relais.on('light')
time.sleep(0.005)
relais.on('light')
relais.off('fanPrinter')
time.sleep(5)

for i in range(10):
    relais.on('light')
    time.sleep(0.005)
    relais.on('light')
    relais.off('fanCam')
    time.sleep(0.995)
    relais.off('light')
    time.sleep(0.005)
    relais.off('light')
    relais.on('fanCam')
    time.sleep(0.995)
time.sleep(3) 
relais.off('fanCam')
relais.off('fanPrinter')
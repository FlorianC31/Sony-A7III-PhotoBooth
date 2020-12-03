from relais import relais
import time

relais=relais(('light','fanCam','fanPrinter',''))

for i in range(10):
    relais.ON('light')
    time.sleep(1)
    relais.OFF('light')
    time.sleep(1)
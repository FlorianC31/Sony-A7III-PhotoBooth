# -*- coding: utf-8 -*-
"""
Created on Thu Sep 17 14:47:36 2020
@author: Florian
"""

import ftd2xx as ft
import time
import sys
from logger import log

MAXITER = 4


class Relais():
    """Exception class for status messages"""

    def __init__(self, name):

        self.init(0)
        self.slot = {}

        i = 1
        for n in name:
            self.slot[n] = i
            i += 1

    def init(self, iter):

        # print("Tentative de connexion " + str(iter + 1) + "/" + str(MAXITER))
        log("NOTE", "Tentative de connexion " + str(iter + 1) + "/" + str(MAXITER), "Module Relais")

        if iter < MAXITER:
            try:
                print
                self.device = ft.open(0)
                self.device.setBitMode(0xFF, 0x01)  # IMPORTANT TO HAVE: This sets up the FTDI device as "Bit Bang" mode.
            except:
                time.sleep(4)  # Wait 4 seconds
                self.init(iter + 1)
        else:
            # print('Impossible de se connecter à la carte relais, vérifier les connexions')
            log("ERROR", "Impossible de se connecter à la carte relais, vérifier les connexions", "Module Relais")
            sys.exit(0)

    def setRelay(self, relay, state):
        relayStates = self.device.getBitMode()  # Get the current state of the relays

        if state:
            newRelayStates = relayStates | relay
        else:
            newRelayStates = relayStates & ~relay

        if newRelayStates == 0:
            self.device.write('0')
        else:
            self.device.write(chr(newRelayStates))

    def getDeviceInfo(self):
        # print(self.device.getDeviceInfo())
        log("INFO", "Relais Device Info: " + self.device.getDeviceInfo(), "Module Relais")

    def ON(self, SlotName):
        slotID = self.slot[SlotName]
        self.setRelay(self.getRelayID(slotID), True)
        # print("Relais " + str(slotID) + ": ON")
        log("NOTE", "Relais " + str(slotID) + ": ON", "Module Relais")

    def OFF(self, SlotName):
        slotID = self.slot[SlotName]
        self.setRelay(self.getRelayID(slotID), False)
        # print("Relais " + str(slotID) + ": OFF")
        log("NOTE", "Relais " + str(slotID) + ": OFF", "Module Relais")

    def close(self):
        self.device.close()

    def getRelayID(self, ID):
        return 2 ** (ID - 1)

    def reinit(self):
        self.device.write('0')

    def test(self):

        for i in range(1, 5):
            Relais.ON(i)
            time.sleep(.5)  # Wait 0.5 seconds

        for i in range(1, 5):
            Relais.OFF(i)
            time.sleep(.5)  # Wait 0.5 seconds


    def focus(self,t):
        self.ON('focus')
        time.sleep(t)
        self.OFF('focus')

    def trigger(self):
        self.ON('focus')
        time.sleep(1)
        self.ON('photo')
        time.sleep(0.3)
        self.OFF('focus')
        self.OFF('photo')

if __name__ == '__main__':

    relais = Relais(('focus', 'photo', 'relais3', 'relais4'))
    relais.trigger()

    #relais.test()
    #relais.focus(1)

    relais.close()


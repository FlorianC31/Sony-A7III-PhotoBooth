# -*- coding: utf-8 -*-
"""
Created on Thu Sep 17 14:47:36 2020

@author: Florian
"""

import ftd2xx as ft
import time
import sys

MAXITER = 4


class Relais:
    """Exception class for status messages"""
    def __init__(self, name):

        self.device = None
        self.connect(1)
        self.slot = {}

        i = 1
        for n in name:
            self.slot[n] = i
            i += 1

        self.running = True

    def connect(self, iter):

        print("Tentative de connexion " + str(iter) + "/" + str(MAXITER))

        if iter < MAXITER:
            try:
                self.device = ft.open(0)
                self.device.setBitMode(0xFF, 0x01)  # IMPORTANT TO HAVE: This sets up the FTDI device as "Bit Bang" mode
            except Exception as e:
                if e.message == 'DEVICE_NOT_FOUND':
                    time.sleep(4)  # Wait 4 seconds
                    self.connect(iter + 1)
                else:
                    print(e.message)
                    sys.exit(1)
        else:
            print('Impossible de se connecter à la carte relais, vérifier les connexions')
            sys.exit(1)

    def set_relay(self, relay, state):
        relay_states = self.device.getBitMode()  # Get the current state of the relays

        if state:
            new_relay_states = relay_states | relay
        else:
            new_relay_states = relay_states & ~relay
        
        if new_relay_states == 0:
            self.device.write('0')
        else:
            self.device.write(chr(new_relay_states))

    def get_device_info(self):
        print(self.device.get_device_info())
        
    def on(self, slot_name):
        slot_id = self.slot[slot_name]
        self.set_relay(self.get_relay_id(slot_id), True)
        time.sleep(0.005)
        self.set_relay(self.get_relay_id(slot_id), True)
        # print("Relais "+str(slot_id)+": ON")
        
    def off(self, slot_name):
        slot_id = self.slot[slot_name]
        self.set_relay(self.get_relay_id(slot_id), False)
        time.sleep(0.005)
        self.set_relay(self.get_relay_id(slot_id), False)
        # print("Relais "+str(slot_id)+": OFF")
        
    def close(self):
        self.running = False
        for s in self.slot:
            self.off(s)
        self.device.close()

    @staticmethod
    def get_relay_id(id):
        return 2**(id - 1)
    
    def reinit(self):
        self.device.write('0')
        
    def test(self):
        
        for i in range(1, 5):
            self.on(i)
            time.sleep(.5)  # Wait 0.5 seconds
            
        for i in range(1, 5):
            self.off(i)
            time.sleep(.5)  # Wait 0.5 seconds


if __name__ == '__main__':

    relais = Relais(('relais1', 'relais2', 'relais3', 'relais4'))

    relais.on('relais1')
    relais.on('relais2')
    relais.on('relais3')
    relais.on('relais4')

    time.sleep(5)

    relais.off('relais1')
    relais.off('relais2')
    relais.off('relais3')
    relais.off('relais4')

import os
import pyautogui as p
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import pyqtSignal, QRunnable
from RsInstrument import RsInstrument
import time


class Signals:
    osci = pyqtSignal(str)


# Update Device List
def getPorts():
    if os.name == 'nt':  # sys.platform == 'win32':
        # from tools.list_ports_windows import comports
        from tools.list_ports_windows import comports
        hits = 0
        comPortList = []
        iterator = sorted(comports())

        for n, (port, desc, hwid) in enumerate(iterator, 1):
            portName = "{}".format(port)
            # sys.stdout.write(portName)
            comPortList.append(portName)
            hits += 1

        if hits == 0:
            # sys.stderr.write("no ports found\n")
            return []
        return comPortList


# Add Oscilloscope
def getOscilloscope(window):

    address = p.password(text='Enter only IP', mask='', default='10.65.2.17')  # 'TCPIP::10.65.1.116::inst0::INSTR'
    if address is None:
        return None, None
    try:
        instr = RsInstrument('TCPIP::' + str(address) + '::inst0::INSTR', True, False)
        time.sleep(0.1)
        return instr, address
    except:
        print(f"Couldn't connect to {address}")
        QMessageBox.warning(window, "CRO/DSO Warning", f"Couldn't connect to {address}")
        return None, None

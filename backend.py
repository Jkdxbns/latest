import serial
from PyQt5.QtCore import QThreadPool, QRunnable, pyqtSlot
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from FindDevices import *
import time
from RsInstrument import *
from CustomWidgets import *
import pyautogui
from test_sir import Convert, convert_string_to_data
from datetime import datetime
import numpy as np
from test_sir import *


class Signals(QObject):
    new = pyqtSignal(str)
    removed = pyqtSignal(str)
    checked = pyqtSignal(str)
    unchecked = pyqtSignal(str)
    parameters = pyqtSignal(str)
    oscilloscope_data = pyqtSignal(list)
    osci_checked = pyqtSignal(str)
    osci_removed = pyqtSignal(str)


class UpdatePorts(QRunnable):

    def __init__(self, list_layout):
        super().__init__()
        self.list = list_layout
        self.signal = Signals()

    def run(self):
        children = set()
        while True:
            device_list = getPorts()
            for i in range(self.list.count()):
                item = self.list.itemAt(i).widget()
                children.add(item.objectName())
                if item.objectName() not in device_list and item.objectName()[0:3] == 'COM':
                    children.remove(item.objectName())
                    self.signal.removed.emit(item.objectName())
            for device in device_list:
                if device not in children:
                    self.signal.new.emit(device)
            time.sleep(1)


class PortName(QRunnable):

    def __init__(self, list_layout):
        super().__init__()
        self.list = list_layout
        self.signal = Signals()

    def parameters(self, portname):
        try:
            ser = serial.Serial(portname)
            ser.flush()
            data_num = len(ser.readline().decode().strip().split(','))
            self.signal.parameters.emit(portname+':'+str(data_num))
            # print(len(data_num), data)
        except:
            pass

    def run(self):
        while True:
            for i in range(self.list.count()):
                item = self.list.itemAt(i).widget()
                if item.isChecked():
                    name = item.objectName()
                    self.parameters(portname=name)
                    self.signal.checked.emit(name)
                else:
                    self.signal.unchecked.emit(item.objectName())
            time.sleep(1)


class ShowContextMenu:

    def __init__(self, parent, position):
        # super.__init__(parent)
        # Creates QMenu obtains tab info for Rename purpose
        context_menu = QMenu("Menu", parent.tabWidget)
        tab_index = parent.tabWidget.tabBar().tabAt(position)
        # Adds New Tab to QTabWidget
        new_tab = QAction("New Tab", parent.tabWidget)
        context_menu.addAction(new_tab)
        new_tab.triggered.connect(lambda: NewTab(parent.tabWidget, urgent=True))
        # Adds Screenshot feature to QMenu
        screenshot_action = QAction('ScreenShot', parent.tabWidget)
        context_menu.addAction(screenshot_action)
        screenshot_action.triggered.connect(lambda: print('ScreenShot requested.'))

        # Rename restricted to tabs only
        if tab_index != -1 and tab_index != parent.tabWidget.count() - 1 and tab_index != 0:
            rename_action = QAction('Rename Tab', parent.tabWidget)
            context_menu.addAction(rename_action)
            rename_action.triggered.connect(
                lambda: parent.tabWidget.setTabText(tab_index,
                                                    pyautogui.prompt(text='Enter new tab name:', title='Rename Tabs',
                                                                     default=parent.tabWidget.tabText(tab_index)))
                # QInputDialog.getText(self.tabWidget, 'Rename', 'Enter name:', text=self.tabWidget.tabText(tab_index))[0]
            )
        context_menu.popup(QtGui.QCursor.pos())


class Oscilloscope(QRunnable):

    def __init__(self, oscilloscope=None):
        super().__init__()
        self.signal = Signals()
        self.instr = oscilloscope
        self.instr.write('SYSTem:DISPlay:UPDate ON')

        # scal_str = 'CHAN1:SCAL {}'
        # range_str = 'CHAN1:RANG {}'
        # tim_scal_str = 'TIM:SCAL {}'
        # tim_range_str = 'TIM:RANG {}'
        # trig_level_str = 'TRIG1:LEV1 {}'

        self.curs1_left_posn_str = 'CURS1:X1P {}'
        self.curs1_right_posn_str = 'CURS1:X2P {}'
        self.curs1_top_posn_str = 'CURS1:Y1P {}'
        self.curs1_bottom_posn_str = 'CURS1:Y2P {}'
        self.curs2_left_posn_str = 'CURS2:X1P {}'
        self.curs2_right_posn_str = 'CURS2:X2P {}'

        # curs2_top_posn_str = 'CURS2:Y1P {}'
        # curs2_bottom_posn_str = 'CURS2:Y2P {}'
        # osc_area_array = []
        # comp_area_array = []
        self.new_array_area1 = []
        self.new_array_area2 = []
        self.new_array_area3 = []
        self.new_array_area4 = []
        # cummulative_array_area = []

        # index = 0
        # sum = 0
        # sum35 = 0
        self.left1 = 0
        self.right1 = 0
        self.left2 = 0
        self.right2 = 0
        # final_area1 = 0
        # final_area2 = 0
        # final_area3 = 0
        # final_area4 = 0
        # start_time = datetime.now()
        self.sum34 = 0
        self.previous_time = datetime.now()

    def run(self):
        # Infinite while loop started
        while True:
            self.instr.write('SYSTem:DISPlay:UPDate ON')
            self.instr.write('MEAS1:ENAB ON')
            self.instr.write('MEAS1:CAT AMPT')
            self.instr.write('MEAS1:SOUR C1W1')
            self.instr.write('MEAS1:MAIN AREA')
            self.meas_area = self.instr.query_str('MEAS1:ARES?')  # Gets Area from Oscilloscope
            self.area_list = self.meas_area.split(',')  # Splits the Area List as measured area is the first item
            self.measured_area = float(self.area_list[0])  # This is the area as reported by the oscilloscop
            self.instr.query_str('*OPC?')
            self.instr.write('EXP:WAV:INCX ON')
            self.data = self.instr.query_str('CHAN1:WAV:DATA:VAL?')  # This is where we get the waveform from Osci
            self.instr.query_str('*OPC?')
            self.instr.write('*OPC')

            self.num_array1 = convert_string_to_data(self.data)  # The data comes as a string, it's converted to a arr
            self.num_array_dict1 = Convert(self.num_array1)
            self.xax1 = [float(x) for x in list(self.num_array_dict1.keys())]
            self.yax1 = [float(x) for x in list(self.num_array_dict1.values())]
            self.xax_array1 = np.array(self.xax1)
            self.yax_array1 = np.array(self.yax1)

            self.left_xax_array1 = self.xax_array1[0:int(len(self.xax_array1) / 2)]
            self.right_xax_array1 = self.xax_array1[int(len(self.xax_array1) / 2):]
            self.left_yax_array1 = self.yax_array1[0:int(len(self.yax_array1) / 2)]
            self.right_yax_array1 = self.yax_array1[int(len(self.yax_array1) / 2):]

            self.left_minimum = np.min(self.left_yax_array1)
            self.right_minimum = np.min(self.right_yax_array1)
            self.left_ab = self.left_yax_array1 + abs(0.95 * self.left_minimum)
            self.right_ab = self.right_yax_array1 + abs(0.95 * self.right_minimum)
            # print("Left Min:",left_minimum,"Right Min:",right_minimum)

            self.left_maxi = np.max(self.left_yax_array1)
            self.right_maxi = np.max(self.right_yax_array1)
            self.area1 = np.trapz(self.yax_array1, self.xax_array1)

            self.left_yax_array1[self.left_yax_array1 < 0] = 0
            self.right_yax_array1[self.right_yax_array1 < 0] = 0
            self.left_ab[self.left_ab < 0] = 0
            self.right_ab[self.right_ab < 0] = 0

            self.left_area_a1 = np.trapz(self.left_yax_array1, self.left_xax_array1)
            self.left_area_ab1 = np.trapz(self.left_ab, self.left_xax_array1)
            self.right_area_a1 = np.trapz(self.right_yax_array1, self.right_xax_array1)
            self.right_area_ab1 = np.trapz(self.right_ab, self.right_xax_array1)
            self.time_diff = datetime.now() - self.previous_time
            ##print(datetime.now())
            # print(previous_time)

            self.delta_t_str = str(self.time_diff)
            self.delta_t = float(self.delta_t_str[6:])
            # print(delta_t)

            if self.left_area_a1 < 0:
                self.sum34 = self.sum34
            else:
                self.sum34 = self.sum34 + self.left_area_a1 * self.delta_t * 455600
            # print(left_area_a1)
            self.previous_time = datetime.now()
            # print(sum34)

            self.left11, self.right11 = zero_crossing(self.left_xax_array1, self.left_yax_array1)
            self.left12, self.right12 = zero_crossing(self.left_xax_array1, self.left_ab)
            self.left21, self.right21 = zero_crossing(self.right_xax_array1, self.left_yax_array1)
            self.left22, self.right22 = zero_crossing(self.right_xax_array1, self.left_ab)
            # print("left1:",left11,"Right1",right11)
            # print("left2:", left12, "Right2", right12)

            self.instr.write('CURS1:FUNC PAIR')
            self.instr.write('CURS1:STAT ON')
            self.instr.write('CURS2:FUNC PAIR')
            self.instr.write('CURS2:STAT ON')
            # instr.write('CURS3:FUNC HOR')
            # instr.write('CURS3:STAT ON')

            self.instr.write(self.curs1_left_posn_str.format(self.left11))
            self.instr.write(self.curs1_right_posn_str.format(self.right11))
            self.instr.write(self.curs1_top_posn_str.format(self.left_maxi))
            self.instr.write(self.curs1_bottom_posn_str.format(self.left_minimum))
            self.instr.write(self.curs2_left_posn_str.format(self.left21))
            self.instr.write(self.curs2_right_posn_str.format(self.right21))
            # instr.write(curs2_top_posn_str.format(right_maxi))
            # instr.write(curs2_bottom_posn_str.format(right_minimum))

            # self.new_array_area1.append(self.left_area_ab1 * 1640000)  # 1left a+b
            # self.new_array_area2.append(self.left_area_a1 * 1640000)  # 1left a
            # self.new_array_area3.append(self.right_area_ab1 * 1640000)  # 2left a+b
            # self.new_array_area4.append(self.right_area_a1 * 1640000)  # 2left a

            data = [(self.left_area_ab1 * 1640000), self.left_area_a1 * 1640000, self.right_area_ab1 * 1640000,
                    self.right_area_a1 * 1640000]
            self.signal.oscilloscope_data.emit(data)
            time.sleep(1)

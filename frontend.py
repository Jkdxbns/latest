from PyQt5 import QtCore, QtGui, QtWidgets
from CustomWidgets import *
from PyQt5.QtWidgets import *
from FindDevices import getOscilloscope, getPorts
from PyQt5.QtCore import QThreadPool, QRunnable
from backend import *
import threading
import pyautogui
import numpy as np

WINDOW_SIZE = (1200, 800)
DEVICES_SELECTED = set()
DEVICES_ALL = set()
MASTER_DATA = dict()
MASTER_PLOT = dict()


class MainWindow(object):

    def __init__(self, main_window):
        # Central widget for main_window
        self.centralwidget = QtWidgets.QWidget(main_window)
        self.centralwidget.setObjectName("centralwidget")
        # Initialising everything
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.add_osci = PushButton(objectName="add_oscilloscope", text="Add CRO/DSO", style=True)
        self.button_plot_all = PushButton(objectName="button_plot_all", text="Plot All", style=True)
        self.rename = PushButton(objectName='Rename', text='Rename Axes', style=True)
        self.set_limits = PushButton(objectName='set_limits', text='Set Limits', style=True)
        self.reset_limits = PushButton(objectName='reset_limits', text='Reset Limits', style=True)
        self.box_devices = Box(objectName="device_list", title="Device List")
        self.box_parameters = Box(objectName="parameter_list", title="Parameter List")
        self.tabWidget = TabWidget(parent=self.centralwidget, objectName="graphs_holder", closeable=True, updated=True)
        self.rename_xaxis = LineEdit(objectName='rename_xaxis', text='X-axis')
        self.rename_yaxis = LineEdit(objectName='rename_yaxis', text='Y-axis')
        self.set_xlim = LineEdit(objectName="set_xlim", text="X:[0, max]")
        self.set_ylim = LineEdit(objectName="set_ylim", text="Y:[0, max]")
        self.SetupUI(main_window)

        # Starts threads for backend
        self.port_updater = QThreadPool()
        changed_ports = UpdatePorts(list_layout=self.device_listLayout)
        changed_ports.signal.new.connect(
            lambda name: self.device_listLayout.addWidget(CheckBox(text=name, objectName=name)))
        changed_ports.signal.new.connect(lambda name: DEVICES_ALL.add(name))
        changed_ports.signal.removed.connect(
            lambda name: self.device_listLayout.removeWidget(self.closed_ports(name, 'device')))
        changed_ports.signal.removed.connect(lambda name: DEVICES_ALL.remove(name))
        self.port_updater.start(changed_ports)

        # Adds Groupbox to parameter list
        self.check_ports = QThreadPool()
        port_parameter = PortName(list_layout=self.device_listLayout)
        port_parameter.signal.checked.connect(lambda name: self.device_checked(name))
        port_parameter.signal.unchecked.connect(
            lambda name: self.box_parameters_layout.removeWidget(self.closed_ports(name, 'parameter')))
        port_parameter.signal.parameters.connect(lambda params: print(params))
        self.check_ports.start(port_parameter)

    def SetupUI(self, main_window):
        # Stores the received main window in main_window
        main_window.setObjectName("MainWindow")
        main_window.setWindowTitle("MainWindow")
        main_window.resize(WINDOW_SIZE[0], WINDOW_SIZE[1])
        main_window.setMinimumSize(QtCore.QSize(WINDOW_SIZE[0], WINDOW_SIZE[1]))
        # Grid Layout for our Central Widget
        self.gridLayout.setContentsMargins(10, 10, 10, 10)
        self.gridLayout.setObjectName("gridLayout")
        # Buttons Section and Line Edits
        # ---------- Add CRO
        self.add_osci.setSizePolicy(custom_size_policy(QSizePolicy.Expanding, QSizePolicy.Expanding))
        self.add_osci.clicked.connect(lambda: self.add_oscilloscope(window=self.box_devices))
        self.gridLayout.addWidget(self.add_osci, 1, 0, 1, 2)
        # ---------- Rename Axes
        # ---------------Xaxis
        self.rename_xaxis.setSizePolicy(custom_size_policy(QSizePolicy.Expanding, QSizePolicy.Expanding))
        self.rename_xaxis.setAlignment(QtCore.Qt.AlignCenter)
        self.rename_xaxis.setMinimumSize(100, 30)
        self.gridLayout.addWidget(self.rename_xaxis, 2, 0)
        # ---------------Yaxis
        self.rename_yaxis.setSizePolicy(custom_size_policy(QSizePolicy.Expanding, QSizePolicy.Expanding))
        self.rename_yaxis.setAlignment(QtCore.Qt.AlignCenter)
        self.rename_yaxis.setMinimumSize(100, 30)
        self.gridLayout.addWidget(self.rename_yaxis, 2, 1)
        # ---------------Button
        self.rename.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.gridLayout.addWidget(self.rename, 3, 0, 1, 2)
        # ---------------Limits
        self.set_xlim.setSizePolicy(custom_size_policy(QSizePolicy.Expanding, QSizePolicy.Expanding))
        self.set_xlim.setAlignment(QtCore.Qt.AlignCenter)
        self.set_xlim.setMinimumSize(100, 30)
        self.gridLayout.addWidget(self.set_xlim, 2, 8, 1, 1)
        self.set_ylim.setSizePolicy(custom_size_policy(QSizePolicy.Expanding, QSizePolicy.Expanding))
        self.set_ylim.setAlignment(QtCore.Qt.AlignCenter)
        self.set_ylim.setMinimumSize(100, 30)
        self.gridLayout.addWidget(self.set_ylim, 2, 9, 1, 1)
        # ---------------Reset/Set limit switch
        self.set_limits.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.gridLayout.addWidget(self.set_limits, 3, 8, 1, 1)
        self.reset_limits.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.gridLayout.addWidget(self.reset_limits, 3, 9, 1, 1)
        # Group Boxes for Listing
        # ---------- Parameter List
        self.box_parameters.setSizePolicy(custom_size_policy(QSizePolicy.Expanding, QSizePolicy.Expanding, 2, 1))
        self.box_parameters_layout = QVBoxLayout()
        self.box_parameters_layout.setContentsMargins(15, 10, 20, 20)
        self.box_parameters_layout.setAlignment(QtCore.Qt.AlignTop)
        self.box_parameters.setLayout(self.box_parameters_layout)
        self.box_parameters.setAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        self.gridLayout.addWidget(self.box_parameters, 0, 8, 2, 2)
        # ---------- Device List
        self.box_devices.setSizePolicy(
            custom_size_policy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding, 2, 1))
        self.box_devices.setAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        self.device_listLayout = QVBoxLayout(self.box_devices)
        self.device_listLayout.setContentsMargins(15, 20, 20, 20)
        self.device_listLayout.setAlignment(QtCore.Qt.AlignTop)
        self.gridLayout.addWidget(self.box_devices, 0, 0, 1, 2)
        # Tab Widget
        self.tabWidget.setWindowTitle("Graph Holder")
        self.tabWidget.setSizePolicy(custom_size_policy(QSizePolicy.Expanding, QSizePolicy.Expanding, 5, 1))
        self.tabWidget.setTabShape(QtWidgets.QTabWidget.Triangular)
        self.tabWidget.tabCloseRequested.connect(lambda index: remove_tab(index=index, parent=self.tabWidget))
        self.tabWidget.customContextMenuRequested.connect(
            lambda position: ShowContextMenu(parent=self, position=position))
        # ---------- Adding Start Tabs
        # self.tabWidget.insertTab(0, QWidget(), "Main Tab")
        NewTab(parent=self.tabWidget)
        self.gridLayout.addWidget(self.tabWidget, 0, 2, 4, 4)
        # Sets Central Widget
        main_window.setCentralWidget(self.centralwidget)

    def closed_ports(self, name, port_type):
        if port_type == 'device':
            for i in range(self.device_listLayout.count()):
                widget = self.device_listLayout.itemAt(i).widget()
                if widget.objectName() == name:
                    widget.setParent(None)
                    return widget
        elif port_type == 'parameter':
            for i in range(self.box_parameters_layout.count()):
                widget = self.box_parameters_layout.itemAt(i).widget()
                if widget.objectName() == name:
                    widget.setParent(None)
                    DEVICES_SELECTED.remove(name)
                    return widget
        return

    def device_checked(self, comport):
        if comport in DEVICES_SELECTED:
            return
        com_box = Box(objectName=comport, title=comport, add_layout="QVBoxLayout", size=10)
        com_box.setSizePolicy(custom_size_policy(QSizePolicy.Expanding, QSizePolicy.Expanding))
        self.box_parameters_layout.addWidget(com_box)
        DEVICES_SELECTED.add(comport)

    def add_oscilloscope(self, window):
        oscilloscope, address = getOscilloscope(window=window)
        if oscilloscope is not None:
            self.device_listLayout.addWidget(CheckBox(text=address, objectName='Oscilloscope'))

            self.osci_thread = QThreadPool()
            osci_data = Oscilloscope(oscilloscope)
            self.osci_thread.start(osci_data)


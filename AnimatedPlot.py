from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT
import matplotlib.pyplot as plt
from matplotlib import animation
import matplotlib
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QRunnable, QThreadPool
# import pandas as pd
import time
import serial

# plt.style.use('fivethirtyeight')
plot_dict = dict()
THREADS = []


class LivePlotting(QRunnable):
    def __init__(self, index=1, com=None, data=None):
        super().__init__()
        self.run_ = 'data'
        self.index = index
        if com is not None:
            self.com = com
            self.run_ = 'com'
        if data is not None:
            self.data = data
            self.run_ = 'data'

    def run(self):
        if self.run_ == 'com':
            x = []
            y = []
            while True:
                plt.ion()
                try:
                    msg = self.com.readline().decode('utf-8').split(',')
                    msg[-1] = msg[-1][0:-2]
                    msg = [float(i) for i in msg]
                    # plot_dict[self.com].append(msg[0])
                    y.append(msg[0])
                    x.append(time.ctime()[-13:-5])
                    plt.figure(2)
                    self.plot(x, y)
                    if len(x) > 5:
                        plt.xticks([i for i in range(1, len(x), int(len(x)/5))])
                    plt.figure(1)
                    self.plot(x, y)
                    time.sleep(1)
                except:
                    pass

        elif self.run_ == 'data':
            pass

    @staticmethod
    def plot(x, y):
        plt.clf()
        time.sleep(0.02)
        plt.plot(x, y)


class AddPlot:

    def check_existence(self, parent):
        for i in range(parent.count()):
            if self.tabname == parent.widget(i).objectName():
                return False
        return True

    def __init__(self, parent, tabName: str = 'tab'):
        self.tabname = tabName
        self.parent = parent
        if self.check_existence(self.parent):
            # Adds layout to Main Tab first
            self.parent.widget(0).setLayout(self.get_layout())  # Figure number 1
            # Creates a new widget
            self.widget = QWidget()
            self.widget.setLayout(self.get_layout())  # Adds layout to new tab anf figure is 2
            # Inserts widget with total tabs-1 index
            index = self.parent.count()
            self.parent.insertTab(index, self.widget, self.tabname)
            self.parent.widget(index).setObjectName(self.tabname)
            self.parent.setCurrentIndex(index)
            # Threads to start plotting
            index += 1
            self.plot_com(index=index)

    def plot_com(self, index):
        serial.Serial(self.tabname).close()  # Closes serial port is opened already
        time.sleep(0.5)
        comport = serial.Serial(self.tabname)  # Opens the port
        plot_dict[comport] = list([])
        self.add_com_thread(comport, index=index)

    @staticmethod
    def add_com_thread(com, index):
        thread = QThreadPool.globalInstance()
        thread.setObjectName(str(com))
        THREADS.append(thread)
        obj = LivePlotting(com=com, index=index)
        thread.start(obj)

    @staticmethod
    def add_osci_thread(data_list):
        pass

    @staticmethod
    def get_layout():
        figure = plt.figure()
        canvas = FigureCanvasQTAgg(figure)
        toolbar = NavigationToolbar2QT(canvas, None)
        layout = QVBoxLayout()
        layout.addWidget(canvas)
        layout.addWidget(toolbar)
        return layout

from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

_translate = QtCore.QCoreApplication.translate


# GUI functions
def custom_font(family: str = "Segeo UI", size: int = 10):
    font = QtGui.QFont()
    font.setFamily(family)
    font.setPointSize(size)
    return font


def custom_size_policy(x: object = "QSizePolicy", y: object = "QSizePolicy", h: int = None, v: int = None):
    sizePolicy = QSizePolicy(x, y)
    if h and v is not None:
        sizePolicy.setHorizontalStretch(h)
        sizePolicy.setVerticalStretch(v)
    return sizePolicy


def CheckBox(text: str, objectName: str, location: list = None, parent: object = None, size: int = 10):
    check_box = QCheckBox()
    if parent is not None:
        check_box = QCheckBox(parent)
    if location is not None:
        check_box.setGeometry(QtCore.QRect(location[0], location[1], location[2], location[3]))
    check_box.setText(text)
    check_box.setObjectName(objectName)
    check_box.setFont(custom_font(size=size))
    check_box.setStyleSheet(" border : None; ")
    return check_box


def PushButton(text: str, objectName: str, parent: object = None, location: list = None, size: int = 10, style: bool = False):
    button = QPushButton()
    if parent is not None:
        button = QPushButton(parent)
    if location is not None:
        button.setGeometry(QtCore.QRect(location[0], location[1], location[2], location[3]))
    button.setFont(custom_font(size=size))
    button.setObjectName(objectName)
    button.setText(text)
    button.setMaximumHeight(50)
    if style:
        button.setStyleSheet("""
            QPushButton{
                background-color : rgb(235, 235, 235);
                border : 1px solid gray;
            }
    
            QPushButton:hover {
                background-color : rgb(220, 220, 220);
            }
        """)
    return button


def Box(objectName: str, title: str, location: list = None, parent: object = None, add_layout: str = None, size: int = 11):
    box = QGroupBox()
    if parent is not None:
        box = QGroupBox(parent)
    if location is not None:
        box.setGeometry(QtCore.QRect(location[0], location[1], location[2], location[3]))
    if add_layout is not None:
        if add_layout == "QVBoxLayout":
            box.setLayout(QVBoxLayout())
        elif add_layout == "QHBoxLayout":
            box.setLayout(QHBoxLayout())
        elif add_layout == "QGridLayout":
            box.setLayout(QGridLayout())
    box.setFont(custom_font(size=size))
    box.setObjectName(objectName)
    box.setTitle(title)
    # box.setStyleSheet(" border : 1px solid gray; ")
    return box


def LineEdit(text: str, objectName: str, location: list = None, parent: object = None, size: int = 10):
    line_edit = QLineEdit()
    if parent is not None:
        line_edit = QLineEdit(parent)
    if location is not None:
        line_edit.setGeometry(QtCore.QRect(location[0], location[1], location[2], location[3]))
    line_edit.setObjectName(objectName)
    line_edit.setFont(custom_font(size=size))
    line_edit.setText(text)
    line_edit.setMaximumHeight(50)
    return line_edit


def ScrollBox(objectName: str, parent: object = None, location: list = None):
    Scroll = QScrollArea()
    if parent is not None:
        Scroll = QScrollArea(parent)
        if location is not None:
            Scroll.setGeometry(QtCore.QRect(location[0], location[1], location[2], location[3]))
    Scroll.setWidgetResizable(True)
    Scroll.setAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
    Scroll.setObjectName(objectName)
    return Scroll


def TabWidget(parent: object, objectName: str, location: list = None,  closeable: bool = True, updated: bool = True, size: int = 10):
    tab = QTabWidget(parent)
    if location is not None:
        tab.setGeometry(QtCore.QRect(location[0], location[1], location[2], location[3]))
    tab.setTabShape(QTabWidget.Triangular)
    tab.setTabsClosable(closeable)
    if updated:
        tab.setUpdatesEnabled(True)
        tab.currentChanged.connect(lambda: NewTab(parent=tab, megaparent=parent))
    tab.setObjectName(objectName)
    tab.setFont(custom_font(size=size))
    tab.setContextMenuPolicy(Qt.CustomContextMenu)
    return tab


# ----Tab functions
def remove_tab(parent, index):
    if parent.count() != 2 and index != 0 and index != parent.count() - 1:
        if parent.currentIndex() == parent.count() - 2:
            parent.setCurrentIndex(parent.currentIndex() - 1)
        parent.removeTab(index)


def NewTab(parent, megaparent=False, urgent: bool = False):
    tab = QWidget()
    # tab.setStyleSheet("""
    #     border : 2px solid black;
    # """)

    count = parent.count()
    try:
        if count == 1:
            megaparent.findChild(QGroupBox, 'parameter_list').setDisabled()
    except:
        pass
    if not urgent:
        if count == 0:
            parent.addTab(tab, '')
            parent.setTabText(parent.indexOf(tab), _translate("MainWindow", 'Main Tab'))
        elif count - 1 == parent.currentIndex():
            parent.addTab(tab, '')
            parent.setTabText(parent.indexOf(tab), _translate("MainWindow", ' + '))
            parent.widget(parent.indexOf(tab)).setObjectName('AddTab')
        if parent.count() == 2:
            return
    elif urgent:
        parent.addTab(tab, '')
        parent.setTabText(parent.indexOf(tab), _translate("MainWindow", ' + '))
        parent.widget(parent.indexOf(tab)).setObjectName('AddTab')
    parent.setTabText(parent.indexOf(tab) - 1, _translate("MainWindow", "Tab"))

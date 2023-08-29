################################################################################
##
## BY: WANDERSON M.PIMENTA
## PROJECT MADE WITH: Qt Designer and PySide2
## V: 1.0.0
##
## This project can be used freely for all uses, as long as they maintain the
## respective credits only in the Python scripts, any information in the visual
## interface (GUI) can be modified without any implication.
##
## There are limitations on Qt licenses if you want to use your products
## commercially, I recommend reading them on the official website:
## https://doc.qt.io/qtforpython/licenses.html
##
################################################################################

from glob import glob
import sys
import platform
from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtCore import (QCoreApplication, QPropertyAnimation, QDate, QDateTime, QMetaObject, QObject, QPoint, QRect, QSize, QTime, QUrl, Qt, QEvent)
from PySide2.QtGui import (QBrush, QColor, QConicalGradient, QCursor, QFont, QFontDatabase, QIcon, QKeySequence, QLinearGradient, QPalette, QPainter, QPixmap, QRadialGradient)
from PySide2.QtWidgets import *
import openpyxl, csv, subprocess, os, pathlib, psutil
from time import sleep

# GUI FILE
from app_modules import *

# from PySide2 import uic
from PySide2.QtWidgets import QWidget

class ItemWidget(QWidget):
    def __init__(self, parent = None):
        QWidget.__init__(self, parent = parent)
        # uic.loadUi(r'interface/TestItemWidget.ui', self)


class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        ## PRINT ==> SYSTEM
        print('System: ' + platform.system())
        print('Version: ' + platform.release())

        ########################################################################
        ## START - WINDOW ATTRIBUTES
        ########################################################################

        ## REMOVE ==> STANDARD TITLE BAR
        UIFunctions.removeTitleBar(True)
        ## ==> END ##

        ## SET ==> WINDOW TITLE
        self.setWindowTitle('OLC PORESIPPR')
        UIFunctions.labelTitle(self, 'OLC PORESIPPR')
        UIFunctions.labelDescription(self, '')
        ## ==> END ##

        ## WINDOW SIZE ==> DEFAULT SIZE
        startSize = QSize(1000, 720)
        self.resize(startSize)
        self.setMinimumSize(startSize)
        # UIFunctions.enableMaximumSize(self, 500, 720)
        ## ==> END ##

        ## ==> CREATE MENUS
        ########################################################################

        ## ==> TOGGLE MENU SIZE
        self.ui.btn_toggle_menu.clicked.connect(lambda: UIFunctions.toggleMenu(self, 220, True))
        ## ==> END ##

        ## ==> ADD CUSTOM MENUS
        self.ui.stackedWidget.setMinimumWidth(20)
        UIFunctions.addNewMenu(self, "HOME", "btn_home", "url(:/16x16/icons/16x16/cil-home.png)", True)
        UIFunctions.addNewMenu(self, "Start Run", "btn_run", "url(:/16x16/icons/16x16/cil-data-transfer-down.png)", True)

        ## ==> END ##

        # START MENU => SELECTION
        UIFunctions.selectStandardMenu(self, "btn_home")
        ## ==> END ##

        ## ==> START PAGE
        self.ui.stackedWidget.setCurrentWidget(self.ui.page_home)
        self.ui.stackedWidget_2.setCurrentWidget(self.ui.page_0)
        ## ==> END ##

        ## USER ICON ==> SHOW HIDE
        #UIFunctions.userIcon(self, "", "url(:/24x24/icons/24x24/confindrlogo.png)", True)
        ## ==> END ##


        ## ==> MOVE WINDOW / MAXIMIZE / RESTORE
        ########################################################################
        def moveWindow(event):
            # IF MAXIMIZED CHANGE TO NORMAL
            if UIFunctions.returStatus() == 1:
                UIFunctions.maximize_restore(self)

            # MOVE WINDOW
            if event.buttons() == Qt.LeftButton:
                self.move(self.pos() + event.globalPos() - self.dragPos)
                self.dragPos = event.globalPos()
                event.accept()

        # WIDGET TO MOVE
        self.ui.frame_label_top_btns.mouseMoveEvent = moveWindow
        ## ==> END ##

        ## ==> LOAD DEFINITIONS
        ########################################################################
        UIFunctions.uiDefinitions(self)
        ## ==> END ##

        ########################################################################
        ## END - WINDOW ATTRIBUTES
        ############################## ---/--/--- ##############################

        appIcon = QIcon("ConFindrIcon.png")
        self.setWindowIcon(appIcon)

        ########################################################################
        #                                                                      #
        ## START -------------- WIDGETS FUNCTIONS/PARAMETERS ---------------- ##

        # Firstly, defines all widgets used
        self.widgetDefiner()

        # Then, calls each function according to each button clicked
        self.runBtn.clicked.connect(self.runClicker)

        # Swaps between all the pages in the stacked widget
        self.leftBtn.clicked.connect(lambda: self.ui.stackedWidget_2.setCurrentIndex(self.ui.stackedWidget_2.currentIndex() - 1))
        self.rightBtn.clicked.connect(lambda: self.ui.stackedWidget_2.setCurrentIndex(self.ui.stackedWidget_2.currentIndex() + 1))

        ########################################################################

        ########################################################################
        #                                                                      #
        ## END --------------- WIDGETS FUNCTIONS/PARAMETERS ----------------- ##
        #                                                                      #
        ############################## ---/--/--- ##############################


        ## SHOW ==> MAIN WINDOW
        ########################################################################
        self.show()
        ## ==> END ##

    ########################################################################
    ## MENUS ==> DYNAMIC MENUS FUNCTIONS
    ########################################################################
    
    # Function for when the run button is clicked
    def runClicker(self):

        # Resets the error text to nothing
        self.runLabelError.setText("")

        # Prints a success message to say the run will take place
        msg = QMessageBox()
        msg.setWindowTitle("Success")
        msg.setText("Starting run now...")
        msg.setIcon(QMessageBox.Information)
        x = msg.exec_()  

        # RUNS THE NANOPORE SEQUENCE HERE ADD THE CODE FOR THAT WHENEVER 
        # Starts adding new photos inside
        subprocess.Popen("python poresippr_placeholder.py", shell=True)

        # self.stackedWidget.addWidget(self.page_home)
        sleep(1)

        complete = False

        while not complete:
            QtCore.QCoreApplication.processEvents()
            
            images = sorted(glob('*.png'))

            if len(images) == 1:
                qpixmap = QPixmap(images[-1])
                self.imageLabel_0.setPixmap(qpixmap)

            elif len(images) == 2:
                qpixmap = QPixmap(images[-1])
                self.imageLabel_1.setPixmap(qpixmap)
            
            elif len(images) == 3:
                qpixmap = QPixmap(images[-1])
                self.imageLabel_2.setPixmap(qpixmap)

            print(len(images))

            # Checks to finish run
            #complete = self.cancelBtn.clicked.connect(self.cancelClicker(complete))

    # Finished the run and breaks the while loop
    def cancelClicker(self, complete):
        complete = True
        return complete
        
        # while True:
        #     images = sorted(glob('*.png'))
        #     qpixmap = QPixmap(images[-1])
        #     self.imageLabel.setPixmap(qpixmap)
        #     sleep(5)
        # for i, image in enumerate(images):
            # w = ItemWidget(self)
            # w.label.setText(i)
            # self.ItemStackedWidget.insertWidget(f'test_{i}', w)
            # self.stackedWidget.addWidget(self.page_home)

    # Buttons that take you to different pages in stacked widget
    def Button(self):
        # GET BT CLICKED
        btnWidget = self.sender()

        # PAGE HOME
        if btnWidget.objectName() == "btn_home":
            self.ui.stackedWidget.setCurrentWidget(self.ui.page_home)
            UIFunctions.resetStyle(self, "btn_home")
            UIFunctions.labelPage(self, "Home")
            btnWidget.setStyleSheet(UIFunctions.selectMenu(btnWidget.styleSheet()))

        # PAGE RUN
        if btnWidget.objectName() == "btn_run":
            self.ui.stackedWidget.setCurrentWidget(self.ui.page_table)
            UIFunctions.resetStyle(self, "btn_run")
            UIFunctions.labelPage(self, "Start Run")
            btnWidget.setStyleSheet(UIFunctions.selectMenu(btnWidget.styleSheet()))

    ## ==> END ##

    ########################################################################
    ## START ==> APP EVENTS
    ########################################################################

    ## EVENT ==> MOUSE DOUBLE CLICK
    ########################################################################
    def eventFilter(self, watched, event):
        if watched == self.le and event.type() == QtCore.QEvent.MouseButtonDblClick:
            print("pos: ", event.pos())
    ## ==> END ##

    ## EVENT ==> MOUSE CLICK
    ########################################################################
    def mousePressEvent(self, event):
        self.dragPos = event.globalPos()
        if event.buttons() == Qt.LeftButton:
            print('Mouse click: LEFT CLICK')
        if event.buttons() == Qt.RightButton:
            print('Mouse click: RIGHT CLICK')
        if event.buttons() == Qt.MidButton:
            print('Mouse click: MIDDLE BUTTON')
    ## ==> END ##

    ## EVENT ==> KEY PRESSED
    ########################################################################
    def keyPressEvent(self, event):
        print('Key: ' + str(event.key()) + ' | Text Press: ' + str(event.text()))
    ## ==> END ##

    ## EVENT ==> RESIZE EVENT
    ########################################################################
    def resizeEvent(self, event):
        self.resizeFunction()
        return super(MainWindow, self).resizeEvent(event)

    def resizeFunction(self):
        print('Height: ' + str(self.height()) + ' | Width: ' + str(self.width()))
    ## ==> END ##

    ########################################################################
    ## END ==> APP EVENTS
    ############################## ---/--/--- ##############################

    def widgetDefiner(self):
        # Defines all the widgets used [there is a lot of them]
        self.runBtn = self.findChild(QPushButton, "runBtn")
        self.leftBtn = self.findChild(QPushButton, "leftBtn")
        self.rightBtn = self.findChild(QPushButton, "rightBtn")
        self.cancelBtn = self.findChild(QPushButton, "cancelBtn")
        self.runLabelError = self.findChild(QLabel, "runLabelError")
        self.timeLabel = self.findChild(QLabel, "timeLabel")
        self.imageLabel_0 = self.findChild(QLabel, "imageLabel_0")
        self.imageLabel_1 = self.findChild(QLabel, "imageLabel_1")
        self.imageLabel_2 = self.findChild(QLabel, "imageLabel_2")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    QtGui.QFontDatabase.addApplicationFont('fonts/segoeui.ttf')
    QtGui.QFontDatabase.addApplicationFont('fonts/segoeuib.ttf')
    window = MainWindow()
    sys.exit(app.exec_())

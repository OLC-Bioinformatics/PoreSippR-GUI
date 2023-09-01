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
from PySide2.QtCore import (QCoreApplication, QPropertyAnimation, QDate, QDateTime, QMetaObject, QObject, QPoint, QRect, QSize, QTime, QTimer, QUrl, Qt, QEvent)
from PySide2.QtGui import (QBrush, QColor, QConicalGradient, QCursor, QFont, QFontDatabase, QIcon, QKeySequence, QLinearGradient, QPalette, QPainter, QPixmap, QRadialGradient)
from PySide2.QtWidgets import *
import subprocess
import time
from time import sleep
from datetime import datetime

# GUI FILE
from app_modules import *

# from PySide2 import uic
from PySide2.QtWidgets import QWidget

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
        #self.ui.stackedWidget_2.setCurrentWidget(self.ui.page_0)
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
        self.runBtn.setCheckable(True)
        self.runBtn.clicked.connect(self.runClicker)
        self.cancelBtn.clicked.connect(self.cancelClicker)

        # Also displays the current time passing. 1000 is in miliseconds which is the amount of time the timer updates
        self.timer = QTimer()
        self.timer.timeout.connect(self.lcd_number)
        self.timer.start(1000)

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
    
    # Function to get the current time each second
    def lcd_number(self):
        time = datetime.now()
        formatted_time = time.strftime("%H:%M:%S")

        # Makes text flat (no white outlines)
        self.lcd.setSegmentStyle(QLCDNumber.Flat)

        # Set number of LCD digits
        self.lcd.setDigitCount(8)

        # Displays the time
        self.lcd.display(formatted_time)

    # Function for when the run button is clicked
    def runClicker(self):

        # Checks if the button is checked when you click on it. If there is another process running, cancel it
        if self.runBtn.isChecked():

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
            p = subprocess.Popen("python poresippr_placeholder.py", shell=True)

            # 1 second delay to allow pictures to load in
            sleep(1)

            # Allows the button to be toggleable and sets the complete var to false. Also defines the listOfImages variable before using it.
            self.cancelBtn.setCheckable(True)
            complete = False
            listOfImages = 0
            
            # While loop to constantly look for new images to add into the GUI. Always adds the last image to the GUI
            while not complete:
                QtCore.QCoreApplication.processEvents()
                
                # Gathers all avalaible images in the current directory and puts them in a sorted list
                images = sorted(glob('*.png'))

                # Sets the page number for each page you travel through
                self.pageLabel.setText(str(self.ui.stackedWidget_2.currentIndex() + 1))

                # Watches to see which page you are on to disable arrow buttons if you are on one of the extreme pages
                if self.ui.stackedWidget_2.currentIndex() == 0:
                    self.leftBtn.setVisible(False)
                    self.rightBtn.setVisible(True) 

                elif self.ui.stackedWidget_2.currentIndex() == self.ui.stackedWidget_2.count() - 1:
                    self.rightBtn.setVisible(False)
                    self.leftBtn.setVisible(True)
                
                else:
                    self.leftBtn.setVisible(True)
                    self.rightBtn.setVisible(True) 

                # Checks to see if a new image is added in, and if it is, this if statement executes once to add a new photo through a label and vericalLayout. Grabs the last image in the list added
                if len(images) == listOfImages + 1:

                    self.newPage = QWidget()
                    self.ui.stackedWidget_2.addWidget(self.newPage)

                    self.imageLabel = QLabel(self.newPage)
                    self.imageLabel.setObjectName(u"imageLabel")
                    self.imageLabel.setAlignment(Qt.AlignCenter)

                    self.verticalLayout = QVBoxLayout(self.newPage)
                    self.verticalLayout.setObjectName(u"verticalLayout")
                    self.verticalLayout.addWidget(self.imageLabel)

                    qpixmap = QPixmap(images[-1])
                    self.imageLabel.setPixmap(qpixmap)
                
                # Updates the number of images added
                listOfImages = len(images)

                # Checks if you want to cancel the run and asks a warning before you cancel it
                if self.cancelBtn.isChecked():
                    msg = QMessageBox()
                    msg.setWindowTitle("Warning")
                    msg.setText("Are you sure you want to stop the run?")
                    msg.setIcon(QMessageBox.Warning)
                    
                    # If you are using the linux, it will return an error but this cannot be fixed as it's a PySide 2 error
                    msg.setStandardButtons(QMessageBox.Yes|QMessageBox.Cancel)

                    msg.buttonClicked.connect(self.dialogClicked)
                    x = msg.exec_()  
                    print(x)

                    # The variable x above produces these two integers below that corrospond to either yes or cancel. Not sure why they produce these numbers but we can make code from them
                    #Yes = 16384     
                    #Cancel = 4194304     
                    if x == 16384:
                        complete = True
                        self.runBtn.setChecked(False)
                        self.runLabelError.setText("Process has been stopped and completed!")
                        self.runLabelError.setStyleSheet(u"color:rgb(34,139,34);")

                    # Rechecks the button to false to make sure we don't loop
                    self.cancelBtn.setChecked(False)
                
                #print(len(images)) 
        
        else:
            # Warns there is a process in run, and resets setChecked to true to make sure you don't press it again
            self.runLabelError.setText("There is a process in run. Please cancel and try again!")
            self.runLabelError.setStyleSheet(u"color:rgb(190, 9, 9);")
            self.runBtn.setChecked(True)

    # Prevents you from cancelling a run if there is no run active
    def cancelClicker(self):
        if self.runBtn.isChecked():
            pass

        else:
            self.runLabelError.setText("There is no run active. Please try when a run is active!")
            self.runLabelError.setStyleSheet(u"color:rgb(190, 9, 9);")
            self.cancelBtn.setChecked(False)

    # Allows you to cancel if you accidently try cancelling a run
    def dialogClicked(self, dialog_button):
        
        if dialog_button.text() == "&Yes":
            if self.cancelBtn.isChecked():
                msg = QMessageBox()
                msg.setWindowTitle("STOPPED")
                msg.setText("Application has stopped reading images")
                msg.setIcon(QMessageBox.Warning)
                msg.exec_()  
        
        if dialog_button.text() == "Cancel":
                msg = QMessageBox()
                msg.setWindowTitle("CONTINUED")
                msg.setText("Application will continue to read images")
                msg.setIcon(QMessageBox.Warning)
                msg.exec_()  
    

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
        self.pageLabel = self.findChild(QLabel, "pageLabel")
        self.imageLabel_0 = self.findChild(QLabel, "imageLabel_0")
        self.imageLabel_1 = self.findChild(QLabel, "imageLabel_1")
        self.imageLabel_2 = self.findChild(QLabel, "imageLabel_2")
        self.lcd = self.findChild(QLCDNumber, "lcdNumber")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    QtGui.QFontDatabase.addApplicationFont('fonts/segoeui.ttf')
    QtGui.QFontDatabase.addApplicationFont('fonts/segoeuib.ttf')
    window = MainWindow()
    sys.exit(app.exec_())

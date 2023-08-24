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

import sys
import platform
from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtCore import (QCoreApplication, QPropertyAnimation, QDate, QDateTime, QMetaObject, QObject, QPoint, QRect, QSize, QTime, QUrl, Qt, QEvent)
from PySide2.QtGui import (QBrush, QColor, QConicalGradient, QCursor, QFont, QFontDatabase, QIcon, QKeySequence, QLinearGradient, QPalette, QPainter, QPixmap, QRadialGradient)
from PySide2.QtWidgets import *
import openpyxl, csv, subprocess, os, pathlib, psutil, glob

# GUI FILE
from app_modules import *

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
        UIFunctions.addNewMenu(self, "Analyze", "btn_analyze", "url(:/16x16/icons/16x16/cil-folder-open.png)", True)
        UIFunctions.addNewMenu(self, "Start Run", "btn_run", "url(:/16x16/icons/16x16/cil-chart.png)", True)

        ## ==> END ##

        # START MENU => SELECTION
        UIFunctions.selectStandardMenu(self, "btn_home")
        ## ==> END ##

        ## ==> START PAGE
        self.ui.stackedWidget.setCurrentWidget(self.ui.page_home)
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
        self.addIsolateBtn.clicked.connect(self.isolateClicker)
        self.deleteIsolateBtn.clicked.connect(self.deleteClicker)

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
    
    # Function for when the button in analyzation station is clicked
    def runClicker(self):

        # Gets the name of the folder with the data
        folderName = str(QFileDialog.getExistingDirectory(self, "Select Folder of Sequences"))
        print("This is the folder directory: " + folderName)

        # Checks if the folder selected contains any fastq.gz or fasta files which is what confindr uses. If not, return that dummy back
        if glob.glob(f'{folderName}/*.fastq.gz') or glob.glob(f'{folderName}/*.fasta'):

            # Prints a success message to say the file is found
            msg = QMessageBox()
            msg.setWindowTitle("Success")
            msg.setText("Successfully found folder. Results may take up to 5 minutes to complete")
            msg.setIcon(QMessageBox.Information)
            x = msg.exec_()

            # Checks what options are selected and applies those arguements to our command line
            rmlst = self.rmlstOptions()
            fasta = self.fastaOptions()
            baseCutoff = self.baseCutoffOptions()
            dataChoice = self.dataChoiceOptions()
            keepFiles = self.keepOptions()
            versionDisplay = self.versionOptions()
            crossDetails = self.crossDetailsOptions()
            verbosity = self.verbosityOptions()
            databases = self.databaseOptions()
            tmp = self.TMPOptions()
            baseFraction = self.baseFractionOptions()
            threads = self.threadsOptions()
            qualityCutoff = self.qualityOptions()
            cgmlst = self.CGMLISTOptions()
            forwardId = self.forwardOptions()
            reverseId = self.reverseOptions()
            MMH = self.MMHOptions()


            # Uses the folder name as an argument to run ConFindr and get the results. Mem represents total allocated memory that is being reserved for confindr
            self.test_out = os.path.join(folderName, "test_out")
            mem = int(0.85 * float(psutil.virtual_memory().total) / 1024)
            subprocess.run(f'confindr -i {folderName} -o {self.test_out}{databases}{rmlst}{threads}{tmp}{keepFiles}{qualityCutoff}{baseCutoff}{baseFraction}{forwardId}{reverseId}{versionDisplay}{dataChoice}{cgmlst}{fasta}{verbosity}{crossDetails}{MMH} -Xmx {mem}K', shell=True)
            print(f'confindr -i {folderName} -o {self.test_out}{databases}{rmlst}{threads}{tmp}{keepFiles}{qualityCutoff}{baseCutoff}{baseFraction}{forwardId}{reverseId}{versionDisplay}{dataChoice}{cgmlst}{fasta}{verbosity}{crossDetails}{MMH} -Xmx {mem}K')
            self.analyzeLabelError.setText("")

            # Prints a success message to say the results are successfully completed
            msg = QMessageBox()
            msg.setWindowTitle("Success")
            msg.setText("Successfully created a csv results file!")
            msg.setIcon(QMessageBox.Information)
            x = msg.exec_()


        # Checks if there is a folder containing your sequence or if there is anything written
        elif len(folderName) == 0:
            self.analyzeLabelError.setText("Please select a folder to continue")

        else:
            self.analyzeLabelError.setText("The folder does not contain any fastq.gz or fasta files")        

    # Function for when the button addIsolate is clicked
    def isolateClicker(self):

        # Adds whatever is typed into the isolateInput into the variable isolateName
        isolateName = self.isolateInput.text()

        # If something is typed in, add this to the first coloumn of the table
        if isolateName != "":

            numOfRows = self.resultsTableWidget.rowCount() + 1
            self.resultsTableWidget.setRowCount(numOfRows)
            self.resultsTableWidget.setItem(numOfRows - 1, 0, QtWidgets.QTableWidgetItem(isolateName))
            #print(numOfRows)

        else:
            self.runLabelError.setText("Please type in an isolate name to continue")

    # Function for when the button deleteIsolate is clicked
    def deleteClicker(self):

        # Deletes the selected row
        indices = self.resultsTableWidget.selectionModel().selectedRows() 

        for index in sorted(indices):
            if self.resultsTableWidget.item(index.row(), 0) == "Isolate":
                print("DO NOT DELETE THE ROW")

            else:
                self.resultsTableWidget.removeRow(index.row()) 


    # Loads the data from the xlsx file to the table widget in PyQt5
    
    def load_data(self, fileName):
        
        # Gathers the path and locates the excel file. Takes the file path, removes the all files header, subtracts the csv portion and adds on the xlsx
        fileName = str(fileName).replace(".xlsx", ".csv", 1)
        path = str(fileName[:-3] + "xlsx")
        workbook = openpyxl.load_workbook(path)
        sheet = workbook.active

        # Sets the number of rows and columns to the max rows and columns of the excel sheet entered
        self.resultsTableWidget.setRowCount(sheet.max_row)
        self.resultsTableWidget.setColumnCount(sheet.max_column)

        # Sets the headers of the widget table to the headers in the excel sheet entered
        list_values = list(sheet.values)

        # Gives a success message
        msg = QMessageBox()
        msg.setWindowTitle("Success")
        msg.setText("Table successfully generated!")
        msg.setIcon(QMessageBox.Information)
        x = msg.exec_()

        # Adds all other elements (value_tuple) of the excel file, skipping the header (starting at column 1 -> # of columns left)
        row_index = 0
        for value_tuple in list_values:
            col_index = 0
            for value in value_tuple:
                self.resultsTableWidget.setColumnWidth(col_index, 200)                
                self.resultsTableWidget.setItem(row_index, col_index, QTableWidgetItem(str(value))) 

                # Sets a whole row to red if there is contamination
                if str(value) == "True":
                    self.resultsTableWidget.item(row_index, col_index).setBackground(QtGui.QColor(255,114,118))    

                col_index += 1                   
                                            
            row_index += 1

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

        # PAGE ANALYZE
        if btnWidget.objectName() == "btn_analyze":
            self.ui.stackedWidget.setCurrentWidget(self.ui.page_analysis)
            UIFunctions.resetStyle(self, "btn_analyze")
            UIFunctions.labelPage(self, "Analyze")
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
        self.addIsolateBtn = self.findChild(QPushButton, "addIsolateBtn")
        self.deleteIsolateBtn = self.findChild(QPushButton, "deleteIsolateBtn")
        self.runLabelError = self.findChild(QLabel, "runLabelError")
        self.timeLabel = self.findChild(QLabel, "timeLabel")
        self.resultsTableWidget = self.findChild(QTableWidget, "resultsTableWidget")
        self.isolateInput = self.findChild(QLineEdit, "isolateInput")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    QtGui.QFontDatabase.addApplicationFont('fonts/segoeui.ttf')
    QtGui.QFontDatabase.addApplicationFont('fonts/segoeuib.ttf')
    window = MainWindow()
    sys.exit(app.exec_())

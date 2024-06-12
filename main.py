#!/usr/bin/env python

"""
Graphical User Interface for PoreSippr. This script creates a GUI for the
PoreSippr, allowing users to start a run and view the summary as it is
processed in real-time. The GUI is created using PySide6 and Qt Designer.
"""
# Standard library imports
from glob import glob
import logging
import os
import platform
import signal
import subprocess
import sys
from time import sleep

# Third party imports
from PySide6 import QtCore, QtGui
from PySide6.QtCore import (
    QEasingCurve,
    QEvent,
    QPoint,
    QPropertyAnimation,
    QSize,
    QTime,
    QTimer,
    Qt
)
from PySide6.QtGui import (
    QColor,
    QFont,
    QIcon,
    QPixmap
)
from PySide6.QtWidgets import (
    QApplication,
    QGraphicsDropShadowEffect,
    QLabel,
    QLCDNumber,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSizeGrip,
    QSizePolicy,
    QVBoxLayout,
    QWidget
)

from ui_main import Ui_MainWindow
from ui_styles import (
    Style
)

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s %(message)s',
)


class MainWindow(QMainWindow):
    """
    Main window class for the PoreSippR GUI application.
    """

    def __init__(self):
        QMainWindow.__init__(self)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.user_interface = Ui_MainWindow()
        self.user_interface.setupUi(self)
        self.user_interface_functions = UIFunctions(self)

        # Define class variables
        self.drag_pos = QPoint()
        # Defines all the widgets used [there is a lot of them]
        self.run_button = self.findChild(QPushButton, name="runBtn")
        self.left_button = self.findChild(QPushButton, name="leftBtn")
        self.right_button = self.findChild(QPushButton, name="rightBtn")
        self.cancel_button = self.findChild(QPushButton, name="cancelBtn")
        self.run_label_error = self.findChild(QLabel, name="runLabelError")
        self.time_label = self.findChild(QLabel, name="timeLabel")
        self.page_label = self.findChild(QLabel, name="pageLabel")
        self.imageLabel_0 = self.findChild(QLabel, name="imageLabel_0")
        self.imageLabel_1 = self.findChild(QLabel, name="imageLabel_1")
        self.imageLabel_2 = self.findChild(QLabel, name="imageLabel_2")
        self.lcd = self.findChild(QLCDNumber, name="lcdNumber")

        # Debug system information
        logging.debug('System: ' + platform.system())
        logging.debug('Version: ' + platform.release())

        # Remove standard title bar
        self.user_interface_functions.removeTitleBar(True)

        # Set the window title
        self.setWindowTitle('PoreSippr')
        self.user_interface_functions.labelTitle(text='PoreSippr')
        self.user_interface_functions.labelDescription(
            text='Graphical User Interface for PoreSippr'
        )

        # Set the default window size
        start_size = QSize(1000, 720)
        self.resize(start_size)
        self.setMinimumSize(start_size)

        # Create menus
        # Toggle menu size
        self.user_interface.btn_toggle_menu.clicked.connect(
            lambda: self.user_interface_functions.toggleMenu(
                maxWidth=220,
                enable=True
            )
        )

        # Add new menus
        self.user_interface.stackedWidget.setMinimumWidth(20)
        self.user_interface_functions.addNewMenu(
            name="HOME",
            objName="btn_home",
            icon="url(:/16x16/icons/16x16/cil-home.png)",
            isTopMenu=True
        )
        self.user_interface_functions.addNewMenu(
            name="Start Run",
            objName="btn_run",
            icon="url(:/16x16/icons/16x16/cil-data-transfer-down.png)",
            isTopMenu=True
        )

        # Apply a style to the menu button that is currently
        # selected, indicating that it's the currently active or selected menu
        self.user_interface_functions.selectStandardMenu(widget="btn_home")

        # Set the current widget of the 'stackedWidget' to be 'page_home'.
        self.user_interface.stackedWidget.setCurrentWidget(
            self.user_interface.page_home
        )

        # Assign the 'move_window' method to the 'mouseMoveEvent' of
        # 'frame_label_top_btns'. When a mouse movement event occurs within the
        # 'frame_label_top_btns' widget, the 'move_window' method will
        # be called.
        self.user_interface.frame_label_top_btns.mouseMoveEvent = \
            self.move_window

        # Load the user interface definitions
        self.user_interface_functions.user_interface_definitions()

        # Set the application icon for the system taskbar
        app_icon = QIcon("cfia.png")
        self.setWindowIcon(app_icon)

        # Call each function according to each button clicked
        self.run_button.setCheckable(True)
        self.run_button.clicked.connect(self.run_clicker)
        self.cancel_button.clicked.connect(self.cancel_clicker)

        # Swap between all the pages in the stacked widget
        self.left_button.clicked.connect(
            lambda: self.user_interface.stackedWidget_2.setCurrentIndex(
                self.user_interface.stackedWidget_2.currentIndex() - 1
            )
        )
        self.right_button.clicked.connect(
            lambda: self.user_interface.stackedWidget_2.setCurrentIndex(
                self.user_interface.stackedWidget_2.currentIndex() + 1
            )
        )

        # Register the signal handler for SIGINT (Ctrl+C)
        signal.signal(signal.SIGINT, self.signal_handler)

        # Create a QTimer to periodically check for SIGINT signals
        self.exit_timer = QTimer()
        self.exit_timer.timeout.connect(self.check_signals)
        # Check every 0.1 seconds
        self.exit_timer.start(100)

        # Create a timer to show the elapsed time of the run
        self.timer = QTimer()

        # Initialise the timer to 0:00:00
        self.time = QTime(0, 0)

        # Set number of LCD digits
        self.lcd.setDigitCount(8)

        # Display the initial time on the LCD
        time_str = self.time.toString('hh:mm:ss')
        self.lcd.display(time_str)

        # Initialise the PoreSippr parsing process
        self.process = None

        # Set the complete flag to False
        self.complete = False

        # Show the main window
        self.show()

    def move_window(self, event):
        """
        Handles the movement of the window when it's dragged with the mouse.

        This method is connected to the mouse move event of the window. If the
        window is maximized, it will be restored to its previous size. Then, if
        the left mouse button is pressed, the window is moved to the new mouse
        position.

        Parameters:
        event (QMouseEvent): The mouse event triggered by the user.
        """
        # If the window is maximized, restore it to its previous size
        if self.user_interface_functions.return_status():
            self.user_interface_functions.maximize_restore()

        # If the left mouse button is pressed, move the window
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(
                self.pos() + event.globalPosition().toPoint() - self.drag_pos)
            self.drag_pos = event.globalPosition().toPoint()
            event.accept()

    def lcd_number(self):
        """
        This method updates the LCD with the elapsed time.

        It increments the current time by one second, sets the LCD
        style to flat, sets the number of digits on the LCD to 8, and
        then displays the updated time on the LCD in the format
        'hh:mm:ss'.
        """
        self.time = self.time.addSecs(1)

        # Displays the time
        self.lcd.display(self.time.toString('hh:mm:ss'))

    # Function for when the run button is clicked
    def run_clicker(self):

        # Checks if the button is checked when you click on it. If there is another process running, cancel it
        if self.run_button.isChecked():

            # Disables the run button to prevent starting another run
            self.run_button.setEnabled(False)

            # Resets the error text to nothing
            self.run_label_error.setText("")

            # Prints a success message to say the run will take place
            message = QMessageBox()
            message.setWindowTitle("Success")
            message.setText("Starting run now...")
            message.setIcon(QMessageBox.Information)
            self.move_message(message=message)
            x = message.exec()

            self.timer.timeout.connect(self.lcd_number)
            self.timer.start(1000)

            # Runs the PoreSippr output parsing script
            self.process = subprocess.Popen(
                ["python", "poresippr_placeholder.py"], preexec_fn=os.setsid)

            # Give a one-second delay to allow pictures to load in
            sleep(1)

            # Allows the button to be toggleable and sets the complete var to false. Also defines the listOfImages variable before using it.
            self.cancel_button.setCheckable(True)
            complete = False
            listOfImages = 0

            # While loop to constantly look for new images to add into the GUI. Always adds the last image to the GUI
            while not self.complete:
                QtCore.QCoreApplication.processEvents()

                # Gathers all avalaible images in the current directory and puts them in a sorted list
                images = sorted(glob('*.png'))

                # Sets the page number for each page you travel through
                self.page_label.setText(
                    str(self.user_interface.stackedWidget_2.currentIndex() + 1))

                # Watches to see which page you are on to disable arrow buttons if you are on one of the extreme pages
                if self.user_interface.stackedWidget_2.currentIndex() == 0:
                    self.left_button.setVisible(False)
                    self.right_button.setVisible(True)

                elif self.user_interface.stackedWidget_2.currentIndex() == self.user_interface.stackedWidget_2.count() - 1:
                    self.right_button.setVisible(False)
                    self.left_button.setVisible(True)

                else:
                    self.left_button.setVisible(True)
                    self.right_button.setVisible(True)

                # Checks to see if a new image is added in, and if it is, this if statement executes once to add a new photo through a label and vericalLayout. Grabs the last image in the list added
                if len(images) == listOfImages + 1:
                    self.newPage = QWidget()
                    self.user_interface.stackedWidget_2.addWidget(self.newPage)

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

                # Checks if you want to cancel the run and asks a warning
                # before you cancel it
                if self.cancel_button.isChecked():
                    message = QMessageBox()
                    message.setWindowTitle("Warning")
                    message.setText("Are you sure you want to stop the run?")
                    message.setIcon(QMessageBox.Warning)

                    # If you are using the linux, it will return an error but this cannot be fixed as it's a PySide 2 error
                    message.setStandardButtons(
                        QMessageBox.Yes | QMessageBox.Cancel)

                    message.buttonClicked.connect(self.dialogClicked)
                    self.move_message(message=message)
                    response = message.exec()

                    # The variable x above produces these two integers below that corrospond to either yes or cancel. Not sure why they produce these numbers but we can make code from them
                    # Yes = 16384
                    # Cancel = 4194304
                    if response == QMessageBox.Yes:
                        self.complete = True
                        self.run_button.setChecked(False)
                        self.run_label_error.setText(
                            "Process has been stopped and completed!")
                        self.run_label_error.setStyleSheet(
                            u"color:rgb(34,139,34);")
                        # Stop the timer
                        self.timer.stop()
                    # Rechecks the button to false to make sure we don't loop
                    self.cancel_button.setChecked(False)

            # Enables the run button again after the run is finished or cancelled
            self.run_button.setEnabled(True)

        else:
            # Warns there is a process in run, and resets setChecked to true to
            # make sure you don't press it again
            self.run_label_error.setText(
                "There is a process in run. Please cancel and try again!"
            )
            self.run_label_error.setStyleSheet(u"color:rgb(190, 9, 9);")
            # Stop the timer
            self.timer.stop()
            # Reset the time to 0:00:00
            self.time.setHMS(h=0, m=0, s=0)
            # Display the reset time
            self.lcd.display(
                self.time.toString('hh:mm:ss'))
            self.cancel_button.setChecked(False)

    # Prevents you from cancelling a run if there is no run active
    def cancel_clicker(self):
        if self.run_button.isChecked():
            return

        self.run_label_error.setText(
            "There is no run active. Please try when a run is active!")
        self.run_label_error.setStyleSheet(u"color:rgb(190, 9, 9);")
        self.cancel_button.setChecked(False)

    # Allows you to cancel if you accidently try cancelling a run
    def dialogClicked(self, dialog_button):

        # if dialog_button.text() == "&Yes":
        #     if self.cancel_button.isChecked():
        #         message = QMessageBox()
        #         message.setWindowTitle("STOPPED")
        #         message.setText("Application has stopped reading images")
        #         message.setIcon(QMessageBox.Warning)
        #         self.move_message(message=message)
        #         message.exec()

        if dialog_button.text() == "Cancel":
            message = QMessageBox()
            message.setWindowTitle("CONTINUED")
            message.setText("Application will continue to read images")
            message.setIcon(QMessageBox.Warning)
            self.move_message(message=message)
            message.exec()

    def closeEvent(self, event):
        """
        This method is called when the window is about to close.

        Parameters:
        event (QCloseEvent): The close event.
        """
        # If a run is in progress (i.e., the run button is checked)
        if self.run_button.isChecked():
            # Create a message box
            message = QMessageBox()
            message.setIcon(QMessageBox.Warning)
            message.setWindowTitle("Warning")
            message.setText(
                "A run is in progress. Are you sure you want to "
                "close the application?"
            )
            message.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)

            # Move the message box to the desired position
            self.move_message(message=message)

            # Show the message box and get the user's response
            response = message.exec()

            # If the user clicked 'Yes', kill the process and accept
            # the close event
            if response == QMessageBox.Yes:
                if self.process is not None:
                    self.complete = True
            # If the user clicked 'Cancel', ignore the close event
            else:
                event.ignore()
        # If no run is in progress, accept the close event
        else:
            event.accept()

    def move_message(self, message):
        """
        Moves the message box to the center of the window.
        :param message: Message box to move
        """
        # Move the message box to the desired position
        message.move(
            self.geometry().center().x() - message.width() // 2,
            self.geometry().center().y() - message.height() // 2
        )

    def check_signals(self):
        """
        Checks for pending signals and handles them.

        This method is connected to the timeout signal of a QTimer. It
        periodically checks for pending signals and handles them.
        """
        # Check for pending signals
        signal.siginterrupt(signal.SIGINT, False)

    def signal_handler(self, signum, frame):
        """
        Handles termination signals sent to the process.

        This function is designed to be used as a signal handler for the
        SIGINT (Ctrl+C) signal. When this signal is received, it sets
        `self.complete` to `True`, which causes the `run_clicker` method
        to exit its while loop and stop the process.

        Parameters:
        signum : int
            The signal number that was sent to the process.
        frame : frame
            The current stack frame at the time the signal was received.
        """
        print('Signal received, stopping...')
        self.complete = True

    def button(self):
        """
        This method handles the button clicks in the User Interface (UI).
        It identifies the button that was clicked and performs the
        corresponding action based on the button's object name.

        If the 'btn_home' button is clicked, it sets the current widget
        of the stacked widget to the home page, resets the style of the
        home button, sets the page label to 'Home', and applies the
        selected menu style to the home button.

        If the 'btn_run' button is clicked, it sets the current widget
        of the stacked widget to the run page, resets the style of the
        run button, sets the page label to 'Start Run', and applies the
        selected menu style to the run button.
        """
        # Get the button that was clicked
        button_widget = self.sender()

        # Check if the 'btn_home' button was clicked
        if button_widget.objectName() == "btn_home":
            # Set the current widget of the stacked widget to the home page
            self.user_interface.stackedWidget.setCurrentWidget(
                self.user_interface.page_home
            )
            # Reset the style of the home button
            self.user_interface_functions.resetStyle("btn_home")
            # Set the page label to 'Home'
            self.user_interface_functions.labelPage("Home")
            # Apply the selected menu style to the home button
            # noinspection PyTypeChecker
            button_widget.setStyleSheet(
                UIFunctions.selectMenu(
                    button_widget.styleSheet()
                )
            )

        # Check if the 'btn_run' button was clicked
        if button_widget.objectName() == "btn_run":
            # Set the current widget of the stacked widget to the run page
            self.user_interface.stackedWidget.setCurrentWidget(
                self.user_interface.page_table
            )
            # Reset the style of the run button
            self.user_interface_functions.resetStyle("btn_run")
            # Set the page label to 'Start Run'
            self.user_interface_functions.labelPage("Start Run")
            # Apply the selected menu style to the run button
            # noinspection PyTypeChecker
            button_widget.setStyleSheet(
                UIFunctions.selectMenu(
                    button_widget.styleSheet()
                )
            )

    # App events

    def mousePressEvent(self, event):
        """
        This method handles mouse press events in the application.

        It records the global position of the mouse cursor at the time of the
        event.It also logs a debug message indicating which mouse button was
        pressed.

        Parameters:
        event (QMouseEvent): The mouse press event.

        """
        # Store the global position of the mouse at the time of the event
        self.drag_pos = event.globalPosition().toPoint()

        # Check which mouse button was pressed and log a debug message
        if event.buttons() == Qt.MouseButton.LeftButton:
            logging.debug('Mouse click: LEFT CLICK')
        if event.buttons() == Qt.MouseButton.RightButton:
            logging.debug('Mouse click: RIGHT CLICK')
        if event.buttons() == Qt.MouseButton.MiddleButton:
            logging.debug('Mouse click: MIDDLE BUTTON')

    def keyPressEvent(self, event):
        """
        This method handles key press events in the application.

        It logs a debug message indicating which key was pressed and the text
        representation of the key press event.

        Parameters:
        event (QKeyEvent): The key press event.
        """
        # Log the key code and the text of the key press event
        logging.debug(
            'Key: ' + str(event.key()) + ' | Text Press: ' + str(event.text())
        )

    def resizeEvent(self, event):
        """
        This method handles the resize event in the application.

        It calls the 'resize_function' method when a resize event is detected.
        The 'resize_function' method is expected to contain the logic for
        handling the resize event.

        Parameters:
        event (QResizeEvent): The resize event.
        """
        # Call the resize function
        self.resize_function()

        # Call the parent class's resizeEvent method
        return super(MainWindow, self).resizeEvent(event)

    def resize_function(self):
        """
        This method logs the current height and width of the application window.

        It's typically called during a resize event to keep track of the
        window's dimensions for debugging purposes.
        """
        # Log the current height and width of the window
        logging.debug(
            'Height: ' + str(self.height()) + ' | Width: ' + str(self.width())
        )

class UIFunctions:
    def __init__(self, main_window):
        self.main_window = main_window
        self.user_interface = self.main_window.user_interface
        self.is_maximized = False
        # Store the initial geometry
        self.previous_geometry = self.main_window.geometry()
        # self.main_window.initialize_ui()

    ########################################################################
    ## START - GUI FUNCTIONS
    ########################################################################

    ## ==> MAXIMIZE/RESTORE
    ########################################################################
    def maximize_restore(self):
        # global GLOBAL_STATE
        # status = GLOBAL_STATE
        if not self.is_maximized:
            # Store the current geometry before maximizing
            self.previous_geometry = self.main_window.geometry()
            self.is_maximized = True

            self.main_window.showMaximized()
            self.user_interface.horizontalLayout.setContentsMargins(0, 0, 0, 0)
            self.user_interface.btn_maximize_restore.setToolTip("Restore")
            self.user_interface.btn_maximize_restore.setIcon(QIcon(u":/16x16/icons/16x16/cil-window-restore.png"))
            self.user_interface.frame_top_btns.setStyleSheet("background-color: rgb(27, 29, 35)")
            self.user_interface.frame_size_grip.hide()
        else:
            # Restore the window to its previous geometry
            self.main_window.setGeometry(self.previous_geometry)
            self.is_maximized = False
            self.main_window.showNormal()
            self.main_window.resize(self.main_window.width()+1, self.main_window.height()+1)
            self.user_interface.horizontalLayout.setContentsMargins(10, 10, 10, 10)
            self.user_interface.btn_maximize_restore.setToolTip("Maximize")
            self.user_interface.btn_maximize_restore.setIcon(QIcon(u":/16x16/icons/16x16/cil-window-maximize.png"))
            self.user_interface.frame_top_btns.setStyleSheet("background-color: rgba(27, 29, 35, 200)")
            self.user_interface.frame_size_grip.show()

    # ## ==> RETURN STATUS
    def return_status(self):
        return self.is_maximized
    #

    ## ==> ENABLE MAXIMUM SIZE
    ########################################################################
    def enableMaximumSize(self, width, height):
        if width != '' and height != '':
            self.main_window.setMaximumSize(QSize(width, height))
            self.user_interface.frame_size_grip.hide()
            self.user_interface.btn_maximize_restore.hide()


    ## ==> TOGGLE MENU
    ########################################################################
    def toggleMenu(self, maxWidth, enable):
        if enable:
            # GET WIDTH
            width = self.user_interface.frame_left_menu.width()
            maxExtend = maxWidth
            standard = 70

            # SET MAX WIDTH
            if width == 70:
                widthExtended = maxExtend
            else:
                widthExtended = standard

            # ANIMATION
            self.animation = QPropertyAnimation(self.user_interface.frame_left_menu, b"minimumWidth")
            self.animation.setDuration(300)
            self.animation.setStartValue(width)
            self.animation.setEndValue(widthExtended)
            self.animation.setEasingCurve(QEasingCurve.InOutQuart)
            self.animation.start()

    ## ==> SET TITLE BAR
    ########################################################################
    @staticmethod
    def removeTitleBar(status):
        global GLOBAL_TITLE_BAR
        GLOBAL_TITLE_BAR = status

    ## ==> HEADER TEXTS
    ########################################################################
    # LABEL TITLE
    def labelTitle(self, text):
        self.user_interface.label_title_bar_top.setText(text)

    # LABEL DESCRIPTION
    def labelDescription(self, text):
        self.user_interface.label_top_info_1.setText(text)

    ## ==> DYNAMIC MENUS
    ########################################################################
    def addNewMenu(self, name, objName, icon, isTopMenu):
        font = QFont()
        font.setFamily(u"Segoe UI")
        button = QPushButton()
        button.setObjectName(objName)
        sizePolicy3 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(button.sizePolicy().hasHeightForWidth())
        button.setSizePolicy(sizePolicy3)
        button.setMinimumSize(QSize(0, 70))
        button.setLayoutDirection(Qt.LeftToRight)
        button.setFont(font)
        button.setStyleSheet(Style.style_bt_standard.replace('ICON_REPLACE', icon))
        button.setText(name)
        button.setToolTip(name)
        button.clicked.connect(self.main_window.button)

        if isTopMenu:
            self.user_interface.layout_menus.addWidget(button)
        else:
            self.user_interface.layout_menu_bottom.addWidget(button)

    ## ==> SELECT/DESELECT MENU
    ########################################################################
    ## ==> SELECT
    def selectMenu(getStyle):
        select = getStyle + ("QPushButton { border-right: 7px solid rgb(44, 49, 60); }")
        return select

    ## ==> DESELECT
    def deselectMenu(getStyle):
        deselect = getStyle.replace("QPushButton { border-right: 7px solid rgb(44, 49, 60); }", "")
        return deselect

    ## ==> START SELECTION
    def selectStandardMenu(self, widget):
        for w in self.user_interface.frame_left_menu.findChildren(QPushButton):
            if w.objectName() == widget:
                w.setStyleSheet(UIFunctions.selectMenu(w.styleSheet()))

    ## ==> RESET SELECTION
    def resetStyle(self, widget):
        for w in self.user_interface.frame_left_menu.findChildren(QPushButton):
            if w.objectName() != widget:
                w.setStyleSheet(UIFunctions.deselectMenu(w.styleSheet()))

    ## ==> CHANGE PAGE LABEL TEXT
    def labelPage(self, text):
        newText = '| ' + text.upper()
        self.user_interface.label_top_info_2.setText(newText)

    ## ==> USER ICON
    ########################################################################
    def userIcon(self, initialsTooltip, icon, showHide):
        if showHide:
            # SET TEXT
            self.user_interface.label_user_icon.setText(initialsTooltip)

            # SET ICON
            if icon:
                style = self.user_interface.label_user_icon.styleSheet()
                setIcon = "QLabel { background-image: " + icon + "; }"
                self.user_interface.label_user_icon.setStyleSheet(style + setIcon)
                self.user_interface.label_user_icon.setText('')
                self.user_interface.label_user_icon.setToolTip(initialsTooltip)
        else:
            self.user_interface.label_user_icon.hide()

    ########################################################################
    ## END - GUI FUNCTIONS
    ########################################################################


    ########################################################################
    ## START - GUI DEFINITIONS
    ########################################################################

    ## ==> UI DEFINITIONS
    ########################################################################
    def user_interface_definitions(self):
        def dobleClickMaximizeRestore(event):
            # IF DOUBLE CLICK CHANGE STATUS
            if event.type() == QEvent.MouseButtonDblClick:
                QTimer.singleShot(250, lambda: self.user_interface_functions.maximize_restore(self))

        ## REMOVE ==> STANDARD TITLE BAR
        if GLOBAL_TITLE_BAR:

            self.main_window.setAttribute(Qt.WA_TranslucentBackground)
            self.user_interface.frame_label_top_btns.mouseDoubleClickEvent = dobleClickMaximizeRestore
        else:
            self.user_interface.horizontalLayout.setContentsMargins(0, 0, 0, 0)
            self.user_interface.frame_label_top_btns.setContentsMargins(8, 0, 0, 5)
            self.user_interface.frame_label_top_btns.setMinimumHeight(42)
            self.user_interface.frame_icon_top_bar.hide()
            self.user_interface.frame_btns_right.hide()
            self.user_interface.frame_size_grip.hide()

        ## SHOW ==> DROP SHADOW
        self.shadow = QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(17)
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(0)
        self.shadow.setColor(QColor(0, 0, 0, 150))
        self.user_interface.frame_main.setGraphicsEffect(self.shadow)

        ## ==> RESIZE WINDOW
        self.sizegrip = QSizeGrip(self.user_interface.frame_size_grip)
        self.sizegrip.setStyleSheet("width: 20px; height: 20px; margin 0px; padding: 0px;")

        ### ==> MINIMIZE
        self.user_interface.btn_minimize.clicked.connect(
            lambda: self.main_window.showMinimized()
        )

        ## ==> MAXIMIZE/RESTORE
        self.user_interface.btn_maximize_restore.clicked.connect(
            self.main_window.user_interface_functions.maximize_restore
        )

        ## SHOW ==> CLOSE APPLICATION
        self.user_interface.btn_close.clicked.connect(
            lambda: self.main_window.close()
        )

if __name__ == "__main__":
    app = QApplication(sys.argv)
    QtGui.QFontDatabase.addApplicationFont('fonts/segoeui.ttf')
    QtGui.QFontDatabase.addApplicationFont('fonts/segoeuib.ttf')
    window = MainWindow()
    signal.signal(signal.SIGINT, lambda *args: app.quit())
    app.exec()

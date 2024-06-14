#!/usr/bin/env python

"""
Graphical User Interface for PoreSippr. This script creates a GUI for the
PoreSippr, allowing users to start a run and view the summary as it is
processed in real-time. The GUI is created using PySide6 and Qt Designer.
"""
# Standard library imports
from glob import glob
import logging
import multiprocessing
import sys

# Third party imports
from PySide6 import QtCore, QtGui
from PySide6.QtCore import (
    QEvent,
    QPoint,
    QSize,
    QThread,
    QTime,
    QTimer,
    Qt,
    Signal
)
from PySide6.QtGui import (
    QColor,
    QIcon,
    QPixmap
)
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QGraphicsDropShadowEffect,
    QLabel,
    QLCDNumber,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSizeGrip,
    QVBoxLayout,
    QWidget
)

# Local imports
from methods import (
    parse_dataframe,
    read_csv_file,
    validate_data_dict,
    validate_headers
)
from poresippr_placeholder import HoldPlace
from ui_main import Ui_MainWindow

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s %(message)s',
)


class Worker(QThread):
    """
    Worker thread class for running
    """
    finished = Signal()

    def __init__(self, hold_place):
        super().__init__()
        self.hold_place = hold_place

    def run(self):
        """
        Run the worker thread.
        """
        self.hold_place.main_loop()
        self.finished.emit()

    def terminate(self):
        """
        Terminate the worker thread.
        """
        print('terminating')
        self.hold_place.terminate()


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

        # Defines the buttons
        self.left_button = self.findChild(QPushButton, name="left_button")
        self.right_button = self.findChild(QPushButton, name="right_button")
        self.cancel_button = self.findChild(QPushButton, name="cancel_button")
        self.file_selection_button = self.findChild(
            QPushButton,
            name="file_selection_button"
        )

        # Disables the left and right buttons until images are added
        self.update_button_states()

        # Defines the labels
        self.run_label_error = self.findChild(QLabel, name="run_label_error")
        self.time_label = self.findChild(QLabel, name="timeLabel")
        self.page_label = self.findChild(QLabel, name="pageLabel")

        # Hide the error QLabel
        self.user_interface.file_label_error.hide()
        
        # Defines the LCD
        self.lcd = self.findChild(QLCDNumber, name="lcd_display")

        # Remove standard title bar
        self.user_interface_functions.remove_title_bar(True)

        # Set the window title
        self.setWindowTitle('PoreSippr')
        self.user_interface_functions.label_title(text='PoreSippr')
        self.user_interface_functions.label_description(
            text='Graphical User Interface for PoreSippr'
        )

        # Get the screen that contains the application window
        screen = QApplication.screenAt(self.geometry().topLeft())

        # If the application is not on any screen (for example, if it hasn't
        # been shown yet), use the primary screen
        if screen is None:
            screen = QApplication.primaryScreen()

        # Get the screen size
        screen_size = screen.availableGeometry()

        # Calculate 75% of the screen dimensions
        start_width = int(screen_size.width() * 0.60)
        start_height = int(screen_size.height() * 0.60)
        start_size = QSize(start_width, start_height)

        # Calculate the center position
        x = int((screen_size.width() - start_size.width()) / 2)
        y = int((screen_size.height() - start_size.height()) / 2)

        # Set the window size and position
        self.setGeometry(x, y, start_size.width(), start_size.height())

        # Set the current widget of the 'stackedWidget' to be 'run_page'.
        self.user_interface.stackedWidget.setCurrentWidget(
            self.user_interface.run_page
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
        app_icon = QIcon("cfia.jpg")
        self.setWindowIcon(app_icon)

        # Set the run button to be uncheckable and disable it initially
        self.user_interface.run_button.setCheckable(False)
        self.user_interface.run_button.setEnabled(False)

        # Connect the run button to the run_clicker method
        self.user_interface.run_button.clicked.connect(self.run_clicker)

        # Set the cancel button to be checkable
        self.cancel_button.setEnabled(False)

        # Initialize the left and right buttons
        self.left_button.clicked.connect(
            lambda: [
                self.user_interface.progress_widget.setCurrentIndex(
                    self.user_interface.progress_widget.currentIndex() - 1
                ),
                self.update_button_states()
            ]
        )

        # Disables the left button until images are added
        self.left_button.setEnabled(False)

        self.right_button.clicked.connect(
            lambda: [
                self.user_interface.progress_widget.setCurrentIndex(
                    self.user_interface.progress_widget.currentIndex() + 1
                ),
                self.update_button_states()
            ]
        )

        # Disable the right button until images are added
        self.right_button.setEnabled(False)

        # Connect the 'select_file' method to the 'clicked' signal of the
        # 'file_selection_button'.
        self.user_interface.file_selection_button.clicked.connect(
            self.select_file
        )

        # Hide the QLineEdit initially
        self.user_interface.file_selection_label.hide()

        # Create a timer to show the elapsed time of the run
        self.timer = QTimer()

        # Initialise the timer to 0:00:00
        self.time = QTime(0, 0)

        # Set number of LCD digits
        self.lcd.setDigitCount(8)

        # Display the initial time on the LCD
        time_str = self.time.toString('hh:mm:ss')
        self.lcd.display(time_str)

        # Create a timer to update the page label
        self.page_label_timer = QTimer()

        # Connect the timeout signal to the update_page_label method
        self.page_label_timer.timeout.connect(self.update_page_label)

        # Update the page label every second
        self.page_label_timer.start(10)

        # Initialise the PoreSippr parsing process
        self.process = None

        # Set the complete flag to False
        self.complete = False

        # Initialise the HoldPlace instance
        self.hold_place = None

        # Initialise the Worker instance
        self.worker = None

        # Show the main window
        self.show()

    def select_file(self):
        """
        Opens a file dialog to select a file.
        :return:
        """
        # Set the options for the file dialog
        options = QFileDialog.Options()

        # Set the file dialog to read-only
        options |= QFileDialog.ReadOnly

        # Set the default directory path
        default_dir = "/home/adamkoziol/Bioinformatics/poresippr_gui/"

        # Get the file name and directory from the file dialog
        file_name, _ = QFileDialog.getOpenFileName(
            self, caption="Select File",
            dir=default_dir,
            filter="CSV Files (*.csv)",  # Filter for CSV files
            options=options
        )

        # Check if a file was selected
        if file_name:
            # Read the CSV file
            df = read_csv_file(file_name)

            # Parse the DataFrame
            data_dict = parse_dataframe(df)

            # Validate the headers
            missing_headers = validate_headers(data_dict)
            if missing_headers:
                print(missing_headers)

                # Update the QLabel text with the error message
                self.user_interface.file_label_error.setText(missing_headers)
                self.user_interface.file_label_error.show()  # Show the QLabel
                return

            # Validate the data
            errors = validate_data_dict(data_dict)
            if errors:
                print(errors)

                # Update the QLabel text with the error message
                self.user_interface.file_label_error.setText(errors)
                self.user_interface.file_label_error.show()  # Show the QLabel
                return

            # Set the text of the QLabel to the selected file name
            self.user_interface.file_selection_label.setText(
                f'PoreSippr configuration file:\n {file_name}'
            )

            # Show the QLabel
            self.user_interface.file_selection_label.show()

            # Hide the error QLabel
            self.user_interface.file_label_error.hide()

            # Get the font metrics of the QLabel
            font_metrics = \
                self.user_interface.file_selection_label.fontMetrics()

            # Calculate the width of the text
            text_width = font_metrics.horizontalAdvance(file_name)

            # Add a buffer to the width
            buffer = 30
            total_width = text_width + buffer

            # Set the minimum width of the QLabel
            self.user_interface.file_selection_label.setMinimumWidth(
                total_width)

            # Enable the run button and make it checkable
            self.user_interface.run_button.setEnabled(True)
            self.user_interface.run_button.setCheckable(True)

    def update_button_states(self) -> list:
        """
        Updates the state of the left and right buttons based on the current
        page index.

        :return: A list of images in the current directory.
        """
        # Find all the images in the directory
        images = self.get_images()

        # If there are no images, disable both buttons
        if not images:
            self.left_button.setEnabled(False)
            self.right_button.setEnabled(False)

        # Watches to see which page you are on to disable arrow buttons if
        # you are on one of the extreme pages
        elif self.user_interface.progress_widget.currentIndex() == 0:
            self.left_button.setEnabled(False)
            self.right_button.setEnabled(True)

        elif self.user_interface.progress_widget.currentIndex() == \
                self.user_interface.progress_widget.count() - 1:
            self.right_button.setEnabled(False)
            self.left_button.setEnabled(True)

        else:
            self.left_button.setEnabled(True)
            self.right_button.setEnabled(True)

        return images

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

    def on_worker_finished(self):
        """
        This method is called when the worker thread finishes.
        """
        self.user_interface.run_button.setChecked(False)
        self.run_label_error.setText(
            "Your PoreSippr run has been successfully terminated")
        self.run_label_error.setStyleSheet(
            u"color:rgb(34,139,34);")
        # Stop the timer
        self.timer.stop()
        # Rechecks the button to false to make sure we don't loop
        self.cancel_button.setChecked(False)
        # Enables the run button again after the run is finished or cancelled
        self.user_interface.run_button.setEnabled(True)
        self.worker.terminate()

    def update_page_label(self):
        """
        Updates the page label to display the current page number out of the
        total number of pages.
        """
        # Gets the current page and total number of pages
        current_page = self.user_interface.progress_widget.currentIndex() + 1

        # Gets the total number of pages
        total_pages = self.user_interface.progress_widget.count()

        # Updates the page_label to display the current page out of the total
        # number of pages
        self.page_label.setText(f"{current_page} / {total_pages}")

    @staticmethod
    def get_images():
        """
        Gathers all available images in the current directory and puts them
        in a sorted list.
        """
        return sorted(glob('*.png'))

    def add_image_to_gui(self, image_path):
        """
        Adds an image to the GUI.

        This method creates a new QWidget, adds it to the progress_widget, and
        then creates a QLabel to display the image. The QLabel is added to the
        QVBoxLayout of the new QWidget. The QPixmap of the image is set as the
        pixmap of the QLabel.

        Parameters:
        image_path (str): The path to the image file.
        """

        # Create a new QWidget
        new_page = QWidget()

        # Add the new QWidget to the progress_widget
        self.user_interface.progress_widget.addWidget(new_page)

        # Create a QLabel to display the image
        image_label = QLabel(new_page)
        image_label.setObjectName(u"imageLabel")
        image_label.setAlignment(Qt.AlignCenter)

        # Create a QVBoxLayout for the new QWidget
        vertical_layout = QVBoxLayout(new_page)
        vertical_layout.setObjectName(u"verticalLayout")

        # Add the QLabel to the QVBoxLayout
        vertical_layout.addWidget(image_label)

        # Create a QPixmap from the image file
        qpixmap = QPixmap(image_path)

        # Set the QPixmap as the pixmap of the QLabel
        image_label.setPixmap(qpixmap)

    def run_clicker(self):
        """
        This method is called when the run button is clicked. It starts the
        PoreSippr process and displays the images in the GUI. It also handles
        the cancellation of the run process. The run process is run in a
        separate thread to prevent the GUI from freezing. The run process
        is terminated when the user clicks the cancel button, closes the
        application window, or when the user sends a SIGINT signal
        :return:
        """

        # Checks if the button is checked when you click on it. If there is
        # another process running, cancel it
        if self.user_interface.run_button.isChecked():

            # If a run has been previously started and stopped
            if self.worker is not None and not self.worker.isRunning():
                # Create a message box
                message = QMessageBox()
                message.setIcon(QMessageBox.Warning)
                message.setWindowTitle("Warning")
                message.setText(
                    "A run has been previously started and stopped. "
                    "Starting a new run, will delete the previous data."
                )
                message.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)

                # Show the message box and get the user's response
                response = message.exec()

                # If the user clicked 'Cancel', return and do not start
                # a new run
                if response == QMessageBox.Cancel:
                    self.user_interface.run_button.setChecked(False)
                    return

            # Disables the run button to prevent starting another run
            self.user_interface.run_button.setEnabled(False)

            # Disable the file_selection_button
            self.file_selection_button.setEnabled(False)

            # Resets the error text to nothing
            self.run_label_error.setText("")

            # Resets the time to 0:00:00
            self.time = QTime(0, 0, 0)

            # Disconnect the timeout signal from the lcd_number slot
            try:
                self.timer.timeout.disconnect(self.lcd_number)
            except TypeError:
                # Ignore the TypeError that occurs if the timeout signal is
                # not connected to the lcd_number slot
                pass

            # Reconnect the timeout signal to the lcd_number slot
            self.timer.timeout.connect(self.lcd_number)

            # Start the timer
            self.timer.start(1000)

            # Create a shared value for the complete flag
            complete = multiprocessing.Value('b', False)
            self.complete = False

            # Create a HoldPlace instance and pass the shared complete
            # flag to it
            self.hold_place = HoldPlace(complete)

            # Create a Worker instance and connect its finished signal to a
            # slot method
            self.worker = Worker(self.hold_place)
            self.worker.finished.connect(self.on_worker_finished)
            self.worker.start()

            # Allows the button to be toggleable
            self.cancel_button.setCheckable(True)
            self.cancel_button.setEnabled(True)

            # Remove all widgets from progress_widget
            for i in reversed(
                    range(self.user_interface.progress_widget.count())):
                self.user_interface.progress_widget.removeWidget(
                    self.user_interface.progress_widget.widget(i)
                )

            # Reset the page label
            self.page_label.setText("0 / 0")

            # Initialise the number of images added to the GUI
            number_of_images = 0

            # While loop to constantly look for new images to add into the GUI.
            # Always adds the last image to the GUI
            while not self.complete:
                # Process events to keep the GUI responsive
                QtCore.QCoreApplication.processEvents()

                # Gets all the images in the current directory
                images = self.get_images()

                # Updates the state of the left and right buttons based on the
                # current page index
                self.update_button_states()

                # If there are new images, add them to the GUI
                if len(images) > number_of_images:
                    for image_path in images[number_of_images:]:
                        self.add_image_to_gui(image_path)

                # Updates the number of images added
                number_of_images = len(images)

                # If the cancel button is checked, stop the run
                if self.cancel_button.isChecked():

                    # Create a message box to confirm the user wants to stop
                    # the run
                    message = QMessageBox()
                    message.setWindowTitle("Warning")
                    message.setText("Are you sure you want to stop the run?")
                    message.setIcon(QMessageBox.Warning)

                    # Create the buttons for the message box
                    message.setStandardButtons(
                        QMessageBox.Yes | QMessageBox.Cancel)

                    # Connect the buttonClicked signal to the dialog_clicked
                    message.buttonClicked.connect(self.dialog_clicked)

                    # Move the message box to the center of the window
                    self.move_message(message=message)

                    # Display the message box and wait for the user to close it
                    response = message.exec()

                    # Pass the response to the dialog_clicked method
                    self.dialog_clicked(response)

                    # Process all pending events
                    QtCore.QCoreApplication.processEvents()

            # Enable the run button again after the run is finished or
            # cancelled
            self.user_interface.run_button.setEnabled(True)

            # Enable the file_selection_button
            self.file_selection_button.setEnabled(True)

    def dialog_clicked(self, response):
        """
        Handles the event when a dialog button is clicked.

        If the "Yes" button is clicked, the run is stopped and the
        complete flag is set to True. The run button is unchecked, and a
        message is displayed to the user indicating that the process has
        been terminated

        If the "Cancel" button is clicked, a message box is displayed to the
        user indicating that the application will continue to read images.

        Parameters:
        response: The button that was clicked in the dialog.
        """

        # If the user clicked 'Yes', stop the run
        if response == QMessageBox.Yes:

            # Set the complete flag to True
            self.complete = True

            # Uncheck the run button
            self.user_interface.run_button.setChecked(False)

            # Display a message indicating the run has been stopped
            self.run_label_error.setText(
                "Your PoreSippr run has been successfully terminated")
            self.run_label_error.setStyleSheet(
                u"color:rgb(34,139,34);")
            # Stop the timer
            self.timer.stop()

            # Uncheck the cancel button
            self.cancel_button.setChecked(False)

            # Disable the cancel button
            self.cancel_button.setEnabled(False)

            # Enable the file_selection_button
            self.file_selection_button.setEnabled(True)

            # Terminate the worker thread
            self.worker.terminate()

            # Update the number of pages
            self.update_button_states()

            # Get the list of images after the dialog box is closed
            images = self.get_images()

            # If there are new images, add them to the GUI
            if len(images) > self.user_interface.progress_widget.count():
                for image_path in \
                        images[
                        self.user_interface.progress_widget.count():]:
                    self.add_image_to_gui(image_path)

        # Check if the "Cancel" button was clicked
        elif response == QMessageBox.Cancel:
            # Create a new message box
            message = QMessageBox()

            # Set the title of the message box
            message.setWindowTitle("CONTINUED")

            # Set the text of the message box
            message.setText("Application will continue to read images")

            # Set the icon of the message box to a warning icon
            message.setIcon(QMessageBox.Warning)

            # Move the message box to the center of the window
            self.move_message(message=message)

            # Display the message box and wait for the user to close it
            message.exec()

            # Uncheck the cancel button
            self.cancel_button.setChecked(False)

    def closeEvent(self, event):
        """
        This method is called when the window is about to close.

        Parameters:
        event (QCloseEvent): The close event.
        """
        # If a run is in progress (i.e., the run button is checked)
        if self.user_interface.run_button.isChecked():
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
                self.complete = True
                self.worker.terminate()
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


class UIFunctions:
    """
    Class for defining the user interface functions. This class contains
    functions for enabling and disabling the maximum size of the window,
    toggling the menu, and setting the title bar.
    """
    def __init__(self, main_window):

        # Store the main window
        self.main_window = main_window

        # Get the user interface
        self.user_interface = self.main_window.user_interface

        # Set the is_maximized flag to False
        self.is_maximized = False

        # Store the initial geometry
        self.previous_geometry = self.main_window.geometry()

        # Set the global title bar flag to True
        self.global_title_bar = True

        # Create a shadow effect
        self.shadow = QGraphicsDropShadowEffect()

        # Create a size grip
        self.sizegrip = QSizeGrip(self.user_interface.frame_size_grip)
        self.sizegrip.setStyleSheet(
            "width: 20px; height: 20px; margin 0px; padding: 0px;")

    def maximize_restore(self):
        """
        Maximizes or restores the window.

        If the window is maximized, it will restore the window to its previous
        geometry. If the window is restored, it will maximize the window.
        """
        # Check if the window is maximized
        if not self.is_maximized:

            # Store the current geometry before maximizing
            self.previous_geometry = self.main_window.geometry()

            # Set the is_maximized flag to True
            self.is_maximized = True

            # Maximize the window
            self.main_window.showMaximized()

            # Set the contents margins to 0
            self.user_interface.horizontalLayout.setContentsMargins(0, 0, 0, 0)

            # Set the maximize/restore button tooltip to 'Restore'
            self.user_interface.maximize_restore_button.setToolTip("Restore")

            # Set the maximize/restore button icon to the restore icon
            self.user_interface.maximize_restore_button.setIcon(
                QIcon(
                    u":/16x16/icons/16x16/cil-window-restore.png"
                )
            )

            # Set the top button frame background color to black
            self.user_interface.frame_top_btns.setStyleSheet(
                "background-color: rgb(27, 29, 35)"
            )

            # Hide the size grip
            self.user_interface.frame_size_grip.hide()
        else:
            # Restore the window to its previous geometry
            self.main_window.setGeometry(self.previous_geometry)

            # Set the is_maximized flag to False
            self.is_maximized = False

            # Show the window
            self.main_window.showNormal()

            # Resize the window by 1 pixel to fix the window size
            self.main_window.resize(
                self.main_window.width() + 1, self.main_window.height() + 1
            )

            # Set the contents margins to 10
            self.user_interface.horizontalLayout.setContentsMargins(
                10, 10, 10, 10
            )

            # Set the maximize/restore button tooltip to 'Maximize'
            self.user_interface.maximize_restore_button.setToolTip("Maximize")

            # Set the maximize/restore button icon to the maximize icon
            self.user_interface.maximize_restore_button.setIcon(
                QIcon(
                    u":/16x16/icons/16x16/cil-window-maximize.png"
                )
            )

            # Set the top button frame background color to black
            self.user_interface.frame_top_btns.setStyleSheet(
                "background-color: rgba(27, 29, 35, 200)"
            )

            # Show the size grip
            self.user_interface.frame_size_grip.show()

    def return_status(self) -> bool:
        """
        Returns the status of the window (maximized or restored).

        :return: The status of the window.
        """
        return self.is_maximized

    def remove_title_bar(self, status):
        """
        Remove the title bar from the window.
        :param status: Boolean value to remove the title bar.
        :return:
        """
        self.global_title_bar = status

    def label_title(self, text):
        """
        Set the title of the window.
        This method sets the text of the title label at the top of the window.
        :param text: The text to set as the title.
        """
        self.user_interface.label_title_bar_top.setText(text)

    def label_description(self, text):
        """
        Set the description of the window.
        This method sets the text of the description label at the top of the
        window.
        :param text: The text to set as the description.
        """
        self.user_interface.label_top_info_1.setText(text)

    def double_click_maximize_restore(self, event):
        """
        Maximize/Restore the window when the title bar is double-clicked.
        """
        # Check if the event type is MouseButtonDblClick
        if event.type() == QEvent.MouseButtonDblClick:
            # Maximize/Restore the window
            UIFunctions.maximize_restore(self)

    def user_interface_definitions(self):
        """
        Set the user interface definitions. This method sets the style of the
        window, the title bar, the size grip, and the buttons. It also connects
        the buttons to their respective functions.
        """

        # Check if the global title bar flag is True
        if self.global_title_bar:

            # Set the main window flags to FramelessWindowHint
            self.main_window.setAttribute(Qt.WA_TranslucentBackground)

            # Enable double-click to maximize/restore the window
            self.user_interface.frame_label_top_btns.mouseDoubleClickEvent = \
                self.double_click_maximize_restore
        else:
            # Set the margins of the horizontal layout to 0
            self.user_interface.horizontalLayout.setContentsMargins(0, 0, 0, 0)

            # Set the margins of the frame label top buttons to 8, 0, 0, 5
            self.user_interface.frame_label_top_btns.setContentsMargins(
                8, 0, 0, 5
            )

            # Set the minimum height of the frame label top buttons to 42
            self.user_interface.frame_label_top_btns.setMinimumHeight(42)

            # Hide the user icon, title bar, and buttons
            self.user_interface.frame_icon_top_bar.hide()
            self.user_interface.frame_btns_right.hide()
            self.user_interface.frame_size_grip.hide()

        # Set the style of the window
        self.shadow.setBlurRadius(17)
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(0)
        self.shadow.setColor(QColor(0, 0, 0, 150))
        self.user_interface.frame_main.setGraphicsEffect(self.shadow)

        # Minimize the window when the minimize button is clicked
        self.user_interface.minimize_button.clicked.connect(
            lambda: self.main_window.showMinimized()
        )

        # Maximize/Restore the window when the maximize/restore button
        # is clicked
        self.user_interface.maximize_restore_button.clicked.connect(
            self.main_window.user_interface_functions.maximize_restore
        )

        # Close the window when the close button is clicked
        self.user_interface.close_button.clicked.connect(
            lambda: self.main_window.close()
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    QtGui.QFontDatabase.addApplicationFont('fonts/segoeui.ttf')
    QtGui.QFontDatabase.addApplicationFont('fonts/segoeuib.ttf')
    window = MainWindow()
    app.exec()

#!/usr/bin/env python

"""
Graphical User Interface for PoreSippr. This script creates a GUI for the
PoreSippr, allowing users to start a run and view the summary as it is
processed in real-time. The GUI is created using PySide6 and Qt Designer.
"""
# Standard library imports
from glob import glob
import multiprocessing
import os
import signal
import sys
import time

# Third party imports
from PySide6 import QtCore, QtGui
from PySide6.QtCore import (
    QCoreApplication,
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
)
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QGraphicsDropShadowEffect,
    QMainWindow,
    QMessageBox,
    QSizeGrip,
    QSizePolicy,
    QTextBrowser,
    QVBoxLayout,
    QWidget
)

# Local imports
from methods import (
    main,
    parse_dataframe,
    read_csv_file,
    validate_data_dict,
    validate_headers
)

from ui_main import Ui_MainWindow


class Worker(QThread):
    """
    Worker thread class for running methods.main
    """
    finished = Signal()

    # Signal for errors
    error = Signal(str)

    def __init__(
            self, folder_path, output_folder, csv_path, complete, file_name):
        super().__init__()
        self.folder_path = folder_path
        self.output_folder = output_folder
        self.csv_path = csv_path
        self.complete = complete
        self.file_name = file_name

    def run(self):
        """
        Run the worker thread.
        """
        try:
            main(
                folder_path=self.folder_path,
                output_folder=self.output_folder,
                csv_path=self.csv_path,
                complete=self.complete,
                config_file=self.file_name
            )
        except Exception as exc:
            self.error.emit(str(exc))
        else:
            self.finished.emit()


class MainWindow(QMainWindow):
    """
    Main window class for the PoreSippr GUI application.
    """

    def __init__(self):

        # Set the base path and image path to None
        self.base_path = None
        self.image_path = None

        # Call the parent class constructor
        QMainWindow.__init__(self)
        self.setWindowFlags(Qt.FramelessWindowHint)

        # Create the user interface
        self.user_interface = Ui_MainWindow()
        self.user_interface.setupUi(self)
        self.user_interface_functions = UIFunctions(self)

        # Define class variables
        self.drag_pos = QPoint()

        # Disables the left and right buttons until images are added
        self.update_button_states()

        # Hide the error QLabel
        self.user_interface.run_label_error.hide()
        
        # Remove standard title bar
        self.user_interface_functions.remove_title_bar(True)

        # Set the window title
        self.setWindowTitle('PoreSippr')

        # Get the screen that contains the application window
        screen = QApplication.screenAt(self.geometry().topLeft())

        # If the application is not on any screen (for example, if it hasn't
        # been shown yet), use the primary screen
        if screen is None:
            screen = QApplication.primaryScreen()

        # Get the screen size
        screen_size = screen.availableGeometry()

        # Calculate 75% of the screen dimensions
        start_width = int(screen_size.width() * 0.45)
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
        self.user_interface.cancel_button.setEnabled(False)

        # Initialize the left and right buttons
        self.user_interface.left_button.clicked.connect(
            lambda: [
                self.user_interface.progress_widget.setCurrentIndex(
                    self.user_interface.progress_widget.currentIndex() - 1
                ),
                self.update_button_states()
            ]
        )

        # Disables the left button until images are added
        self.user_interface.left_button.setEnabled(False)

        self.user_interface.right_button.clicked.connect(
            lambda: [
                self.user_interface.progress_widget.setCurrentIndex(
                    self.user_interface.progress_widget.currentIndex() + 1
                ),
                self.update_button_states()
            ]
        )

        # Disable the right button until images are added
        self.user_interface.right_button.setEnabled(False)

        # Connect the 'select_file' method to the 'clicked' signal of the
        # 'file_selection_button'.
        self.user_interface.file_selection_button.clicked.connect(
            self.select_file
        )

        # Create a timer to show the elapsed time of the run
        self.timer = QTimer()

        # Initialize a flag to track if the signal is connected
        self.is_lcd_number_connected = False

        # Initialise the timer to 0:00:00
        self.time = QTime(0, 0)

        # Set number of LCD digits
        self.user_interface.lcd_display.setDigitCount(8)

        # Display the initial time on the LCD
        time_str = self.time.toString('hh:mm:ss')
        self.user_interface.lcd_display.display(time_str)

        # Create a timer to update the page label
        self.user_interface.page_label_timer = QTimer()

        # Connect the timeout signal to the update_page_label method
        self.user_interface.page_label_timer.timeout.connect(
            self.update_page_label
        )

        # Update the page label every second
        self.user_interface.page_label_timer.start(10)

        # Initialise the PoreSippr parsing process
        self.process = None

        # Set the complete flag to False
        self.complete = False

        # Initialise the HoldPlace instance
        self.hold_place = None

        # Initialise the Worker instance
        self.worker = None

        # Initialise the file name
        self.file_name = None

        # Initialise the data dictionary
        self.data_dict = {}

        # Show the main window
        self.show()

    def mousePressEvent(self, event):
        """
        Handles the event when the mouse button is pressed.

        Parameters:
        event (QMouseEvent): The mouse event triggered by the user.
        """
        # If the left mouse button is pressed, update the drag position
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.drag_pos = event.globalPosition().toPoint()
            event.accept()

    def select_file(self):
        """
        Opens a file dialog to select a file.
        :return:
        """
        # Set the options for the file dialog
        options = QFileDialog.Options()

        # Set the file dialog to read-only
        options |= QFileDialog.ReadOnly

        # Get the file name and directory from the file dialog
        self.file_name, _ = QFileDialog.getOpenFileName(
            self, caption="Select File",
            dir='.',
            filter="CSV Files (*.csv)",  # Filter for CSV files
            options=options
        )

        # Check if a file was selected
        if self.file_name:
            # Read the CSV file
            df = read_csv_file(self.file_name)

            # Parse the DataFrame
            self.data_dict = parse_dataframe(df)

            # Validate the headers
            missing_headers = validate_headers(self.data_dict)
            if missing_headers:

                # Update the QLabel text with the error message
                self.user_interface.run_label_error.setText(missing_headers)
                self.user_interface.run_label_error.show()  # Show the QLabel
                return

            # Validate the data
            errors = validate_data_dict(self.data_dict)
            if errors:
                # Update the QLabel text with the error message
                self.user_interface.run_label_error.setText(errors)
                self.user_interface.run_label_error.show()  # Show the QLabel
                return
            else:
                # Hide the error QLabel
                self.user_interface.run_label_error.hide()

            # Extract the base path from the output directory
            self.base_path = os.path.dirname(self.data_dict['output_dir'])

            # Set the image path
            self.image_path = os.path.join(self.base_path, 'images')

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
        images = self.get_images(path=self.image_path)

        # If there are no images, disable both buttons
        if not images:
            self.user_interface.left_button.setEnabled(False)
            self.user_interface.right_button.setEnabled(False)

        # Watches to see which page you are on to disable arrow buttons if
        # you are on one of the extreme pages
        elif self.user_interface.progress_widget.currentIndex() == 0:
            self.user_interface.left_button.setEnabled(False)
            # Enable the right button only if there are at least two images
            self.user_interface.right_button.setEnabled(len(images) >= 2)

        elif self.user_interface.progress_widget.currentIndex() == \
                self.user_interface.progress_widget.count() - 1:
            self.user_interface.right_button.setEnabled(False)
            self.user_interface.left_button.setEnabled(True)

        else:
            self.user_interface.left_button.setEnabled(True)
            self.user_interface.right_button.setEnabled(True)

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
            # Calculate the difference between the current mouse position and
            # the position where the drag started
            diff = event.globalPosition().toPoint() - self.drag_pos
            # Add the difference to the current position of the window
            self.move(self.pos() + diff)
            # Update the position where the drag started
            self.drag_pos = event.globalPosition().toPoint()
            event.accept()

    def lcd_number(self):
        """
        This method updates the LCD with the elapsed time.

        It increments the current time by one second, sets the LCD
        style to flat, sets the number of digits on the LCD to eight, and
        then displays the updated time on the LCD in the format
        'hh:mm:ss'.
        """
        self.time = self.time.addSecs(1)

        # Displays the time
        self.user_interface.lcd_display.display(self.time.toString('hh:mm:ss'))

    def on_worker_finished(self):
        """
        This method is called when the worker thread finishes.
        """
        self.user_interface.run_button.setChecked(False)
        self.user_interface.run_label_error.setText(
            "Your PoreSippr run has been successfully terminated")
        self.user_interface.run_label_error.show()
        self.timer.stop()

        # Rechecks the button to false; ensures we don't loop
        self.user_interface.cancel_button.setChecked(False)

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
        self.user_interface.pageLabel.setText(
            f"{current_page} / {total_pages}"
        )

    @staticmethod
    def get_images(path=None):
        """
        Gathers all available images in the current directory and puts them
        in a sorted list.

        :param path: The path to the directory containing the images.
        """
        # If the path is not provided, return None
        if path is None:
            return None

        return sorted(glob(os.path.join(path, '*.html')))

    def add_html_to_gui(self, html_path):
        """
        Adds HTML to the GUI.
        """

        # Wait for the image file to be fully written
        while True:
            try:
                size1 = os.path.getsize(html_path)
                time.sleep(1)
                size2 = os.path.getsize(html_path)
                if size1 == size2:
                    break
            except FileNotFoundError:
                time.sleep(1)

        # Create a new QWidget
        new_page = QWidget()

        # Add the new QWidget to the progress_widget
        self.user_interface.progress_widget.addWidget(new_page)

        # Set the new QWidget as the current widget
        self.user_interface.progress_widget.setCurrentWidget(new_page)

        # Update the page label and button states
        self.update_page_label()
        self.update_button_states()

        # Create a QTextBrowser to display the HTML
        text_browser = QTextBrowser(new_page)
        text_browser.setObjectName(u"textBrowser")
        text_browser.setAlignment(Qt.AlignCenter)

        # Load the HTML file into the QTextBrowser
        with open(html_path, 'r') as f:
            html_content = f.read()
        text_browser.setHtml(html_content)

        # Set the size policy of the QTextBrowser to allow it to expand freely
        text_browser.setSizePolicy(QSizePolicy.Expanding,
                                   QSizePolicy.Expanding)

        # Create a QVBoxLayout for the new QWidget
        vertical_layout = QVBoxLayout(new_page)
        vertical_layout.setObjectName(u"verticalLayout")

        # Set the contents margins and spacing of the QVBoxLayout
        vertical_layout.setContentsMargins(0, 0, 0, 0)
        vertical_layout.setSpacing(0)

        # Add the QTextBrowser to the QVBoxLayout
        vertical_layout.addWidget(text_browser)

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
            self.user_interface.file_selection_button.setEnabled(False)

            # Resets the error text to nothing
            self.user_interface.run_label_error.setText("")
            self.user_interface.run_label_error.hide()

            # Resets the time to 0:00:00
            self.time = QTime(0, 0, 0)

            # Disconnect the timeout signal from the lcd_number slot
            # Check the flag before disconnecting
            if self.is_lcd_number_connected:
                self.timer.timeout.disconnect(self.lcd_number)
                # Set the flag to False when the signal is disconnected
                self.is_lcd_number_connected = False

            # Reconnect the timeout signal to the lcd_number slot
            self.timer.timeout.connect(self.lcd_number)
            self.is_lcd_number_connected = True

            # Start the timer
            self.timer.start(1000)

            # Create a shared value for the complete flag
            complete = multiprocessing.Value('b', False)
            self.complete = False

            # Create variables for the folder path, output folder, and csv path
            folder_path = os.path.join(self.base_path, 'output')
            csv_path = os.path.join(self.data_dict['output_dir'])

            # Create a Worker instance and connect its finished signal to a
            # slot method
            self.worker = Worker(
                folder_path=folder_path,
                output_folder=self.image_path,
                csv_path=csv_path,
                complete=complete,
                file_name=self.file_name
            )
            self.worker.finished.connect(self.on_worker_finished)
            self.worker.start()

            # Allows the button to be toggleable
            self.user_interface.cancel_button.setCheckable(True)
            self.user_interface.cancel_button.setEnabled(True)

            # Remove all widgets from progress_widget
            for i in reversed(
                    range(self.user_interface.progress_widget.count())):
                self.user_interface.progress_widget.removeWidget(
                    self.user_interface.progress_widget.widget(i)
                )

            # Reset the page label
            self.user_interface.pageLabel.setText("0 / 0")

            # Initialise the number of images added to the GUI
            number_of_images = 0

            # While loop to constantly look for new images to add into the GUI.
            # Always adds the last image to the GUI
            while not self.complete:
                # Process events to keep the GUI responsive
                QtCore.QCoreApplication.processEvents()

                # Gets all the images in the current directory
                images = self.get_images(path=self.image_path)

                # Updates the state of the left and right buttons based on the
                # current page index
                # self.update_button_states()

                # If there are new images, add them to the GUI
                if len(images) > number_of_images:
                    for image_path in images[number_of_images:]:
                        self.add_html_to_gui(image_path)
                # Updates the number of images added
                number_of_images = len(images)

                # If the cancel button is checked, stop the run
                if self.user_interface.cancel_button.isChecked():

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
            self.user_interface.file_selection_button.setEnabled(True)

    def dialog_clicked(self, response):
        """
        Handles the event when a dialog button is clicked.

        If the "Yes" button is clicked, the run is stopped and the
        complete flag is set to True. The uncheck the run button, and display a
        message to the user indicating that the process has
        been terminated

        If the user clicks the "Cancel" button, display a message box to the
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
            self.user_interface.run_label_error.setText(
                "Your PoreSippr run has been successfully terminated")

            # Show the message
            self.user_interface.run_label_error.show()

            # Stop the timer
            self.timer.stop()

            # Uncheck the cancel button
            self.user_interface.cancel_button.setChecked(False)

            # Disable the cancel button
            self.user_interface.cancel_button.setEnabled(False)

            # Enable the file_selection_button
            self.user_interface.file_selection_button.setEnabled(True)

            # Terminate the worker thread
            self.worker.terminate()

            # Update the number of pages
            self.update_button_states()

            # Get the list of images after the dialog box is closed
            images = self.get_images(path=self.image_path)

            # If there are new images, add them to the GUI
            if len(images) > self.user_interface.progress_widget.count():
                for image_path in \
                        images[
                        self.user_interface.progress_widget.count():]:
                    self.add_html_to_gui(image_path)
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
            self.user_interface.cancel_button.setChecked(False)

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
    # Create a function to handle SIGINT
    def sigint_handler(_, __):
        """Handler for the SIGINT signal."""
        QCoreApplication.quit()

    # Register the signal handler
    signal.signal(signal.SIGINT, sigint_handler)

    app = QApplication(sys.argv)

    # Ensure that the event loop is interrupted by SIGINT
    timer = QTimer()
    timer.start(500)  # Every 500ms, the event loop will be interrupted
    timer.timeout.connect(lambda: None)

    QtGui.QFontDatabase.addApplicationFont('fonts/segoeui.ttf')
    QtGui.QFontDatabase.addApplicationFont('fonts/segoeuib.ttf')
    window = MainWindow()
    app.exec()

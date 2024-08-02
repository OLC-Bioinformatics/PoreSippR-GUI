#!/usr/bin/env python

"""
Graphical User Interface for PoreSippr. This script creates a GUI for the
PoreSippr, allowing users to start a run and view the summary as it is
processed in real-time. The GUI is created using PySide6 and Qt Designer.
"""
# Standard library imports
import csv
from glob import glob
import multiprocessing
import os
import re
import signal
import sys
import time

# Third party imports
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
    QFontDatabase,
    QIcon,
    QImageReader,
    QPixmap
)
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QComboBox,
    QDialog,
    QFileDialog,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSizeGrip,
    QSizePolicy,
    QSpacerItem,
    QStyledItemDelegate,
    QTableWidget,
    QTableWidgetItem,
    QTextBrowser,
    QVBoxLayout,
    QWidget
)

# Local imports
from methods import (
    determine_script_path,
    is_valid_fasta,
    main,
)
from ui_main import Ui_MainWindow
from version import __version__


class Worker(QThread):
    """
    Worker thread class for running the .main
    """
    finished = Signal()

    # Signal for errors
    error = Signal(str)

    def __init__(
            self, folder_path, output_folder, csv_path, complete,
            configuration_file, metadata_file, lab_name, run_name,
            pid_store=None):
        super().__init__()
        self.folder_path = folder_path
        self.output_folder = output_folder
        self.csv_path = csv_path
        self.complete = complete
        self.configuration_file = configuration_file
        self.metadata_file = metadata_file
        self.lab_name = lab_name
        self.run_name = run_name
        self.pid_store = pid_store
        self.error_message = str()

    def run(self):
        """
        Run the worker thread.
        """
        try:
            # Determine the script path
            script_path = os.path.abspath(__file__)

            # Enable test mode if the script is run by 'adamkoziol'
            test_mode = 'adamkoziol' in script_path

            print('folder_path', self.folder_path)
            print('output_folder', self.output_folder)
            print('csv_path', self.csv_path)
            print('complete', self.complete)
            print('configuration_file', self.configuration_file)
            print('metadata_file', self.metadata_file)
            print('lab_name', self.lab_name)
            print('run_name', self.run_name)
            print('pid_store', self.pid_store)
            print('test_mode', test_mode)

            main(
                folder_path=self.folder_path,
                output_folder=self.output_folder,
                csv_path=self.csv_path,
                complete=self.complete,
                config_file=self.configuration_file,
                metadata_file=self.metadata_file,
                lab_name=self.lab_name,
                run_name=self.run_name,
                test=test_mode,
                pid_store=self.pid_store
            )

        except Exception as exc:
            self.error_message = str(exc)
            self.error.emit(str(exc))
        else:
            self.finished.emit()


class CustomTableWidget(QTableWidget):
    """
    A subclass of QTableWidget that supports pasting multiple cells from the
    clipboard. It overrides the keyPressEvent to handle Ctrl+V (paste) action
    and inserts the clipboard content into the table starting from the current
    cell position.
    """

    def keyPressEvent(self, event):
        """
        Handles key press events. Specifically, it intercepts the Ctrl+V
        (paste) action to paste clipboard content into the table.

        Parameters:
            event (QKeyEvent): The event that triggered the keyPressEvent.
        """
        # Check if the pressed key is Ctrl+V (paste)
        if (event.key() == Qt.Key_V and
                event.modifiers() & Qt.ControlModifier):
            # Access the clipboard
            clipboard = QApplication.clipboard()
            text = clipboard.text()  # Get text from clipboard
            rows = text.split('\n')  # Split text into rows

            # Get the current cell's row and column
            currentRow = self.currentRow()
            currentColumn = self.currentColumn()

            # Iterate over each row in the clipboard content
            for r, row in enumerate(rows):
                if row:  # Check if row is not empty
                    columns = row.split('\t')  # Split row into columns
                    # Iterate over each column in the row
                    for c, column in enumerate(columns):
                        # Calculate where to insert the cell
                        row_index = currentRow + r
                        col_index = currentColumn + c

                        # Ensure the table has enough rows and columns
                        if row_index >= self.rowCount():
                            self.insertRow(row_index)
                        if col_index >= self.columnCount():
                            self.insertColumn(col_index)

                        # Insert the clipboard item into the table
                        self.setItem(
                            row_index, col_index, QTableWidgetItem(column)
                        )
        else:
            # Handle other key events normally
            super().keyPressEvent(event)


class CustomMessageBox(QMessageBox):
    """
    A custom QMessageBox class that applies a specific stylesheet to all
    instances of QMessageBox, giving it a modern/bootstrap look without icons.
    """
    def __init__(self, *args, **kwargs):
        """
        Initialize the CustomMessageBox with the specified stylesheet.

        :param args: Positional arguments passed to the parent QMessageBox.
        :param kwargs: Keyword arguments passed to the parent QMessageBox.
        """
        super().__init__(*args, **kwargs)
        self.setStyleSheet(
            """
            QPushButton {
                border: 1px solid #007bff;  /* Blue border */
                border-radius: 4px;         /* Rounded corners */
                background-color: #007bff;  /* Blue background */
                color: white;               /* White text */
                padding: 5px 10px;          /* Padding */
                font: bold;                 /* Bold font */
            }
            QPushButton:hover {
                background-color: #0056b3;  /* Darker blue on hover */
            }
            QPushButton:pressed {
                background-color: #003f7f;  /* Even darker blue on press */
            }
            QPushButton#Yes {
                background-color: #28a745;  /* Green for Yes */
                border: 1px solid #28a745;  /* Green border */
            }
            QPushButton#Yes:hover {
                background-color: #218838;  /* Darker green on hover */
            }
            QPushButton#Yes:pressed {
                background-color: #1e7e34;  /* Even darker green on press */
            }
            QPushButton#Cancel {
                background-color: #dc3545;  /* Red for Cancel */
                border: 1px solid #dc3545;  /* Red border */
            }
            QPushButton#Cancel:hover {
                background-color: #c82333;  /* Darker red on hover */
            }
            QPushButton#Cancel:pressed {
                background-color: #bd2130;  /* Even darker red on press */
            }
            """
        )


class LargeEditorDelegate(QStyledItemDelegate):
    """
    A custom delegate that modifies the editor's properties, such as height,
    for a better user experience.

    This delegate is particularly useful for ensuring that the QLineEdit editor
    within a QTableWidget has sufficient height to display text properly,
    especially for characters with descenders.
    """

    def createEditor(self, parent, option, index):
        """
        Overrides the default editor creation process to adjust the editor's
        properties, such as height.

        This method is called by the Qt framework when an item is edited. It
        creates a QLineEdit editor by default and adjusts its minimum height to
        ensure all characters are displayed correctly.

        Parameters:
            parent (QWidget): The parent widget for the editor.
            option (QStyleOptionViewItem): Provides style options for the item.
            index (QModelIndex): The index of the item in the model.

        Returns:
            QWidget: An editor widget with modified properties. Specifically,
            a QLineEdit with adjusted height.
        """
        # Create the default line edit editor
        editor = super().createEditor(parent, option, index)
        if isinstance(editor, QLineEdit):
            # Adjust the editor's height if necessary
            editor.setMinimumHeight(35)  # Adjust this value as needed
        return editor


class MainWindow(QMainWindow):
    """
    Main window class for the PoreSippr GUI application.
    """

    def __init__(self):

        # Set image path to None
        self.image_path = None

        # Call the parent class constructor
        QMainWindow.__init__(self)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)

        # Set up the signal handler for SIGINT (Ctrl+C)
        signal.signal(signal.SIGINT, self.signal_handler)

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
        self.screen_size = screen.availableGeometry()

        # Calculate 75% of the screen dimensions
        start_width = int(self.screen_size.width() * 0.45)
        start_height = int(self.screen_size.height() * 0.60)
        start_size = QSize(start_width, start_height)

        # Calculate the center position
        x = int((self.screen_size.width() - start_size.width()) / 2)
        y = int((self.screen_size.height() - start_size.height()) / 2)

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

        # Determine the base path of the current Python file
        script_path = determine_script_path()

        # Set the application icon for the system taskbar
        image_path = os.path.join(script_path, 'cfia.jpg')
        if os.path.exists(image_path):
            if QImageReader(image_path).canRead():
                app_icon = QIcon(image_path)
                self.setWindowIcon(app_icon)
                QApplication.setWindowIcon(app_icon)

        # Set the user icon for the label
        user_icon_path = os.path.join(
            script_path,
            'icons/24x24/olcConfindrLogo.png'
        )

        if os.path.exists(user_icon_path):
            self.user_interface.label_user_icon.setPixmap(
                QPixmap(user_icon_path)
            )
            self.user_interface.label_user_icon.setScaledContents(True)
            self.user_interface.label_user_icon.setAlignment(
                Qt.AlignmentFlag.AlignCenter
            )

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

        # Connect the 'configure_run' method to the 'clicked' signal of the
        # 'configuration_button'.
        self.user_interface.configuration_button.clicked.connect(
            self.configure_run
        )

        # Connect the 'open_dialog' method to the 'clicked' signal of the
        # 'sequence_info_button'.
        self.user_interface.sequence_info_button.clicked.connect(
            self.open_dialog
        )

        # Disable the sequence info button until a run is configured
        self.user_interface.sequence_info_button.setEnabled(False)

        # Set the version
        self.user_interface.label_version.setText(f"Version: {__version__}")

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

        # Initialise the lab name
        self.lab_name = None

        # Initialise the reference file name/path
        self.reference_file = None

        # Initialise the parent directory of the reference file
        self.working_dir = None

        # Initialise the run name
        self.run_name = None

        # Initialise the barcode kit
        self.barcode_kit = None

        # Initialise the selected barcodes
        self.selected_barcodes = []

        # Initialise the fast5 directory
        self.fast5_dir = None

        # Initialise the CSV path
        self.csv_path = None

        # Initialise the configuration file
        self.configuration_file = None

        # Initialise the metadata CSV file
        self.metadata_file = None

        # Initialise a list to store barcode: seqid: olnid information
        self.sequence_info = []

        # Initialise the list of external process PIDs
        self.pid_store = []

        # Show the main window
        self.setWindowTitle('PoreSippr')
        self.show()

    def signal_handler(self, _, __):
        """
        Handles the SIGINT signal (keyboard interrupt) and prompts the user
        to confirm application termination.
        """
        # Check if a run is in progress and prompt the user for confirmation
        if self.user_interface.run_button.isChecked():
            response = CustomMessageBox.question(
                self, "Warning",
                "A run is in progress. Are you sure you want to close the "
                "application?",
                QMessageBox.Yes | QMessageBox.Cancel
            )
            if response == QMessageBox.Yes:
                self.complete = True
                # Terminate the worker and any external processes
                self.worker.terminate()
                for pid in self.pid_store:
                    try:
                        os.kill(pid, signal.SIGTERM)
                    except ProcessLookupError:
                        pass
                sys.exit(0)  # Exit the application
            else:
                pass  # Do nothing, continue running
        else:
            sys.exit(0)  # Exit the application if no run is in progress

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

    def configure_run(self):
        """
        Configures and displays a dialog for user input.

        This method sets up a dialog with various widgets for user input,
        including a file selection button, a text input field, a combo box
        for selecting options, and a series of checkboxes. It also includes
        a validation button that, when clicked, checks the inputs and closes
        the dialog if everything is valid.
        """
        # Initialize the dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Enter PoreSippr Run Data")
        dialog.setStyleSheet(
            "QDialog { background-color: #f0f0f0; }"
            "QPushButton { border: 1px solid #007bff; "
            "border-radius: 4px; background-color: #007bff; "
            "color: white; padding: 5px 10px; }"
            "QLineEdit, QComboBox, QCheckBox { "
            "border: 1px solid #ced4da; border-radius: 4px; "
            "padding: 5px; }"
            "QLabel { font-weight: bold; }"
        )

        # Set up the main layout
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Lab name input section
        layout.addWidget(QLabel("Lab Name"))
        lab_name_dropdown = QComboBox(dialog)
        lab_name_dropdown.addItems(
            ["BUR", "CAL", "DAR", "FFFM", "GTA", "OLC", "STH"])
        lab_name_dropdown.setStyleSheet(
            "QComboBox { border: 1px solid #007bff; border-radius: 4px; "
            "padding: 5px; }"
            "QComboBox::drop-down { border: 0px; }"
            "QComboBox::down-arrow { image: "
            "url(icons/20x20/cil-chevron-bottom.png); }"
            "QComboBox::down-arrow { width: 14px; height: 14px; }"
            "QComboBox::down-arrow { subcontrol-origin: padding; "
            "subcontrol-position: center right; right: 5px; }"
            "QComboBox QAbstractItemView::item { height: 25px; }"
            "QComboBox QAbstractItemView::item:selected { background-color: "
            "#007bff; color: white; }"
            "QComboBox QAbstractItemView::item:hover { background-color: "
            "#007bff; color: white; }"
            "QComboBox QAbstractItemView { selection-background-color: "
            "#007bff; selection-color: white; }"
        )
        layout.addWidget(lab_name_dropdown)

        # Reference file selection section
        layout.addWidget(QLabel("Reference File"))
        reference_button = QPushButton("Select Reference File", dialog)
        reference_button.setStyleSheet(
            """
            QPushButton {
                border: 1px solid #007bff;  /* Blue border */
                border-radius: 4px;         /* Rounded corners */
                background-color: #007bff;  /* Blue background */
                color: white;               /* White text */
                padding: 5px 10px;          /* Padding */
            }
            QPushButton:hover {
                background-color: #0056b3;  /* Darker blue on hover */
            }
            QPushButton:pressed {
                background-color: #003f7f;  /* Even darker blue on press */
            }
            """
        )
        reference_button.clicked.connect(
            lambda: self.select_reference_file(dialog, reference_button)
        )
        layout.addWidget(reference_button)

        # Run name input section
        layout.addWidget(QLabel("Run Name"))
        run_name_input = QLineEdit(dialog)

        # Set the placeholder text
        run_name_input.setPlaceholderText("Enter run name e.g. MIN-YYYYMMDD")

        layout.addWidget(run_name_input)

        # Barcode kit selection section
        layout.addWidget(QLabel("Barcode Kit"))
        barcode_kit_input = QLineEdit(dialog)

        # Set the placeholder text
        barcode_kit_input.setPlaceholderText(
            "Enter barcode kit e.g. SQK-RBK114-24")

        layout.addWidget(barcode_kit_input)

        # Enhanced barcode selection section with custom styling and tooltips
        # Create the QLabel for "Barcodes" and set its tooltip
        barcode_label = QLabel("Barcodes")
        barcode_label.setToolTip("Select one or more barcodes")

        # Add the QLabel to the layout
        layout.addWidget(barcode_label)

        # Continue with the QListWidget setup
        barcode_list_widget = QListWidget(dialog)
        barcode_list_widget.setSelectionMode(QAbstractItemView.MultiSelection)

        barcode_list_widget.setStyleSheet("""
            QListWidget {
                border: 1px solid #007bff;
                border-radius: 4px;
                background-color: #f0f0f0;
                color: #333;
            }
            QListWidget::item {
                height: 15px; /* Increase item height */
                padding: 5px; /* Add some padding for text */
            }
            QListWidget::item:selected {
                background-color: #007bff;
                color: white;
            }
        """)

        # Add items to the list widget
        for i in range(1, 25):
            barcode_list_widget.addItem(f"{i:02}")

        layout.addWidget(barcode_list_widget)

        # Validate button section
        validate_button = QPushButton("Validate", dialog)
        validate_button.setStyleSheet(
            "QPushButton { border: 1px solid #007bff; "
            "border-radius: 4px; background-color: #007bff; "
            "color: white; padding: 5px 10px; }"
            "QPushButton:hover { background-color: #0056b3; }"
            "QPushButton:pressed { background-color: #003f7f; }"
        )
        validate_button.clicked.connect(
            lambda: self.validate_and_close(
                window_dialog=dialog,
                run_name_input=run_name_input,
                barcode_kit_input=barcode_kit_input,
                barcode_list_widget=barcode_list_widget,
                lab_name_dropdown=lab_name_dropdown
            )
        )
        layout.addWidget(validate_button)

        # Adjust the dialog size to fit its contents
        dialog.adjustSize()

        # Execute the dialog
        dialog.exec()

    def select_reference_file(self, window_dialog, button):
        """
        Opens a file dialog to select a reference file and updates the button
        with the selected file's name and green styling.

        :param window_dialog: The dialog window to open the file dialog.
        :param button: The button to update with the selected file's name
        and style.
        """
        self.reference_file, _ = QFileDialog.getOpenFileName(
            window_dialog,
            caption="Select Reference File",
            dir="",
            filter="All Files (*)"
        )
        if self.reference_file:
            # Extract the file name from the path
            file_name = os.path.basename(self.reference_file)

            # Update the button text and style
            button.setText(file_name)
            button.setStyleSheet(
                """
                QPushButton {
                    border: 1px solid #28a745;  /* Green border */
                    border-radius: 4px;         /* Rounded corners */
                    background-color: #28a745;  /* Green background */
                    color: white;               /* White text */
                    padding: 5px 10px;          /* Padding */
                }
                QPushButton:hover {
                    background-color: #218838;  /* Darker green on hover */
                }
                QPushButton:pressed {
                    background-color: #1e7e34;  /* Darker still on press */
                }
                """
            )

    def validate_and_close(
            self, window_dialog, run_name_input, barcode_kit_input,
            barcode_list_widget, lab_name_dropdown):
        """
        Validates the user inputs and closes the dialog if successful.

        :param window_dialog: The dialog window to close.
        :param run_name_input: The QLineEdit for the run name.
        :param barcode_kit_input: The QLineEdit for the barcode kit.
        :param barcode_list_widget: The QListWidget for the selected barcodes.
        :param lab_name_dropdown: The QComboBox for the lab name.
        """
        # Capture inputs
        self.lab_name = lab_name_dropdown.currentText().rstrip()
        self.run_name = run_name_input.text().rstrip()
        self.barcode_kit = barcode_kit_input.text().rstrip()
        self.selected_barcodes = sorted([
            item.text() for item in barcode_list_widget.selectedItems()
        ])

        # Initialize a list to store messages for invalid inputs
        invalid_messages = []

        # Validate Lab Name
        if not self.lab_name:
            invalid_messages.append("Lab Name cannot be blank.")

        # Ensure a reference file is selected
        if not self.reference_file:
            invalid_messages.append("Reference file is required.")
        else:
            # Validate the reference file
            if not is_valid_fasta(self.reference_file):
                invalid_messages.append(
                    "Reference file is not a valid FASTA file."
                )
            else:
                # Extract the parent directory of the reference file
                self.working_dir = os.path.dirname(self.reference_file)

        # Validate Run Name
        if not self.run_name:
            invalid_messages.append("Run Name cannot be blank.")
        else:
            run_name_pattern = re.compile(r"MIN-\d{8}")
            if not run_name_pattern.match(self.run_name):
                invalid_messages.append(
                    "Run Name must be in the format MIN-YYYYMMDD.")

        # Validate Barcode Kit
        if not self.barcode_kit:
            invalid_messages.append("Barcode Kit cannot be blank.")

        # Validate Selected Barcodes
        if not self.selected_barcodes:
            invalid_messages.append("At least one barcode must be selected.")

        # Validate if fast5 directory exists
        fast5_dir = os.path.join(
            '/var/lib/minknow/data/', self.run_name, 'no_sample'
        )

        if not os.path.exists(fast5_dir):
            invalid_messages.append(
                f"Run directory {fast5_dir} does not exist. Please ensure "
                f"that you supplied the correct run name, and that the run "
                f"has started"
            )
        else:
            # Check if the run-specific output folder exists
            fast5_dirs = glob(os.path.join(fast5_dir, '*/'))
            if not fast5_dirs:
                invalid_messages.append(
                    "No fast5 files found in the directory. Please wait for "
                    "files to be produced. This can take up to 45 minutes "
                    "after starting a run"
                )

            # Add 'fast5' to self.fast5_dir
            self.fast5_dir = os.path.join(
                fast5_dirs[0], 'fast5'
            )

        # Display warning message if there are invalid inputs
        if invalid_messages:
            CustomMessageBox.warning(
                window_dialog, "Invalid Input(s)",
                "Please correct the following issues before proceeding:\n" +
                "\n".join(invalid_messages)
            )
        else:
            # Assuming validation is successful
            msg_box = CustomMessageBox(window_dialog)
            msg_box.setText("Validation Successful\nAll entries are valid.")
            msg_box.exec()

            # Write the run configuration information to a CSV file
            self.create_input_csv()

            # Update the path of the image directory
            self.image_path = os.path.join(
                self.working_dir, 'images'
            )

            # Enable the sequence info button
            self.user_interface.sequence_info_button.setEnabled(True)

            # Close the dialog
            window_dialog.accept()

    def create_input_csv(self):
        """
        Creates an input CSV file with the user inputs.
        """
        # Define the header and rows
        header = ['reference', 'fast5_dir', 'output_dir', 'config', 'barcode',
                  'barcode_values']
        # Step 1: Sort the list of selected barcodes
        sorted_barcodes = sorted(self.selected_barcodes)

        # Step 2: Join the sorted list into a string, separated by commas
        barcode_values_str = ",".join(sorted_barcodes)

        # Step 3: Enclose the string in quotes
        barcode_values_literal = f'"{barcode_values_str}"'

        # Define the csv_path
        self.csv_path = os.path.join(self.working_dir, self.run_name)

        # Step 4: Create the row for the CSV file
        row = [
            self.reference_file,
            self.fast5_dir,
            self.csv_path,
            'dna_r10.4.1_e8.2_260bps_fast.cfg',
            self.barcode_kit,
            barcode_values_literal
        ]

        # Set the name and path of the CSV file
        self.configuration_file = os.path.join(
            self.working_dir, 'input.csv'
        )

        # Create the CSV file
        with open(
                self.configuration_file,
                'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(header)
            writer.writerow(row)

    def open_dialog(self):
        """
        Opens a dialog window with a QTableWidget for user data entry.

        This method creates and displays a QDialog containing a QTableWidget.
        The table is populated with predefined barcode values in the first
        column, allowing the user to enter corresponding SEQID and OLNID values
        in the subsequent columns. The dialog is modal, meaning it will block
        input to the main window until it is closed.
        """
        # Check if barcodes are populated
        if not self.selected_barcodes:
            CustomMessageBox.warning(
                self, "No Barcodes",
                "No barcode values are available to populate the table."
            )
            return

        # Create a QDialog instance as a child of the main window
        dialog = QDialog(self)
        dialog.setWindowTitle("Enter Data")

        # Create a QVBoxLayout for the dialog's layout
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(10, 10, 10, 10)  # Adjust margins if needed
        layout.setSpacing(5)  # Adjust spacing if needed

        # Initialize the QTableWidget within the dialog
        table = CustomTableWidget(dialog)
        table.setColumnCount(3)

        # Define the headers for the table columns
        table.setHorizontalHeaderLabels(["Barcode", "SEQID", "OLNID"])
        table.setRowCount(len(self.selected_barcodes))

        # Apply the custom delegate to the SEQID and OLNID columns
        delegate = LargeEditorDelegate(table)
        table.setItemDelegateForColumn(1, delegate)
        table.setItemDelegateForColumn(2, delegate)

        # Populate the first column of the table with barcode values
        for i, barcode in enumerate(self.selected_barcodes):
            table.setItem(i, 0, QTableWidgetItem(barcode))

            #  SEQID column as empty
            table.setItem(i, 1, QTableWidgetItem(""))

            # OLNID column as empty
            table.setItem(i, 2, QTableWidgetItem(""))

        # Set initial widths for SEQID and OLNID columns
        table.setColumnWidth(1, 150)
        table.setColumnWidth(2, 150)

        # After setting up the table and populating it with items
        for i in range(table.rowCount()):
            table.setRowHeight(
                i, 30
            )

        table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #ddd;
                font-family: Arial, sans-serif;
                font-size: 14px;
                color: #333;
            }
            QTableWidget::item {
                border: 1px solid #ddd;
                padding: 8px;
                selection-background-color: #f5f5f5;
            }
            QTableWidget::item:selected {
                background-color: #0275d8;
                color: white;
            }
            QHeaderView::section {
                background-color: #f7f7f7;
                padding: 8px;
                border: 1px solid #ddd;
                font-size: 14px;
                font-weight: bold;
            }
            QTableWidget::item:hover {
                background-color: #f9f9f9;
            }
        """)

        # Set the size policy of the table to Expanding
        table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # Add the table to the dialog's layout
        layout.addWidget(table, 1)
        table.resizeColumnsToContents()

        # Create the "Validate" button
        validate_button = QPushButton("Validate", dialog)

        def validate_and_close():
            """
            Validates SEQID entries and closes the dialog if
            validation is successful, showing a success message.
            """
            if self.validate_seqid_entries(table):
                # Show a success message
                msg_box = CustomMessageBox(dialog)
                msg_box.setText(
                    "Validation Successful\nAll entries are valid.")
                msg_box.exec()
                # Write the metadata to the CSV file
                self.write_metadata_table()

                # Enable the run button and make it checkable
                self.user_interface.run_button.setEnabled(True)
                self.user_interface.run_button.setCheckable(True)

                # Close the dialog
                dialog.accept()

        validate_button.clicked.connect(validate_and_close)

        validate_button.setStyleSheet("""
            QPushButton {
                border: 1px solid #007bff; /* Blue border */
                border-radius: 4px; /* Rounded corners */
                background-color: #007bff; /* Blue background */
                color: white; /* White text */
                padding: 5px 10px; /* Padding */
                font-weight: bold; /* Bold font */
                text-align: center; /* Centered text */
            }
            QPushButton:hover {
                background-color: #0056b3; /* Darker blue on hover */
            }
            QPushButton:pressed {
                background-color: #003f7f; /* Even darker blue on press */
            }
        """)

        # Create a QHBoxLayout for the button
        button_layout = QHBoxLayout()

        # Add a spacer to the left side
        button_layout.addItem(
            QSpacerItem(
                40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        )

        # Add the validate button to the layout
        button_layout.addWidget(validate_button)

        # Add a spacer to the right side
        button_layout.addItem(
            QSpacerItem(
                40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        )

        # Add the button layout to the main dialog layout
        layout.addLayout(button_layout)

        # Adjust the minimum size of the dialog
        dialog.setMinimumSize(
            int(self.screen_size.width() * 0.3),
            int(self.screen_size.height() * 0.45)
        )

        # Display the dialog and block input to the main window until closed
        dialog.exec()

    def validate_seqid_entries(self, table):
        """
        Validates SEQID entries in the QTableWidget.

        Ensures each SEQID entry matches the specified format and is unique.
        The format is defined as four digits, followed by '-MIN-', and ending
        with four digits. Displays a message box if any entry is invalid or
        not unique, including if the SEQID is empty.

        Parameters:
            table (QTableWidget): The table containing SEQID entries.

        Returns:
            bool: True if all entries are valid and unique, False otherwise.
        """

        # Compile regex pattern for SEQID validation
        seqid_pattern = re.compile(r"^\d{4}-MIN-\d{4}$")

        # Initialize a dictionary to track SEQIDs and associated barcodes
        seqid_to_barcodes = {}

        # List to store messages for invalid SEQIDs
        invalid_messages = []

        # Reset sequence_info to avoid duplicates
        self.sequence_info = []

        for row in range(table.rowCount()):
            # Retrieve SEQID, barcode, and OLNID from the table
            seqid = table.item(row, 1).text().rstrip()
            barcode = table.item(row, 0).text().rstrip()
            olnid = table.item(row, 2).text().rstrip()

            # Check if SEQID is empty
            if seqid == "":
                invalid_messages.append(
                    f"SEQID for barcode '{barcode}' is missing.")
            elif not seqid_pattern.match(seqid):
                # Add message for invalid SEQID format
                invalid_messages.append(
                    f"SEQID '{seqid}' for barcode '{barcode}' is invalid.")
            else:
                # Handle non-unique SEQIDs
                if seqid in seqid_to_barcodes:
                    seqid_to_barcodes[seqid].append(barcode)
                else:
                    seqid_to_barcodes[seqid] = [barcode]
                    self.sequence_info.append(
                        {'barcode': barcode, 'SEQID': seqid, 'OLNID': olnid})

        # Generate messages for non-unique SEQIDs
        for seqid, barcodes in seqid_to_barcodes.items():
            if len(barcodes) > 1:
                invalid_messages.append(
                    f"SEQID '{seqid}' is not unique, found in barcodes: "
                    f"{', '.join(barcodes)}.")

        # Display warning message if there are invalid SEQIDs
        if invalid_messages:
            CustomMessageBox.warning(
                self, "Invalid SEQID(s)",
                "The following SEQID(s) are invalid, not unique, or missing. "
                "Please correct them:\n" +
                "\n".join(invalid_messages) +
                "\n\nRequired format for SEQID: ####-MIN-#### "
                "(where # is a digit)."
            )
            return False
        return True

    def write_metadata_table(self):
        """
        Creates a metadata CSV file with the barcode, SEQID, and OLNID values.
        """
        # Define the header
        header = ['Barcode', 'SEQID', 'OLNID']

        # Define the rows
        rows = []
        for entry in self.sequence_info:
            rows.append([entry['barcode'], entry['SEQID'], entry['OLNID']])

        # Update the metadata file path
        self.metadata_file = os.path.join(self.working_dir, 'metadata.csv')

        # Write the metadata to the CSV file
        with open(self.metadata_file, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(header)
            for row in rows:
                writer.writerow(row)

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

    def update_error_label(self, message):
        """
        Updates the QLabel with the provided error message.

        Parameters:
        message (str): The error message to display.
        """
        # Set the error message
        self.user_interface.run_label_error.setText(message)

        # Make sure the QLabel is visible
        self.user_interface.run_label_error.show()

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
        self.timer.stop()

        # Rechecks the button to false; ensures we don't loop
        self.user_interface.cancel_button.setChecked(False)

        # Enables the run button again after the run is finished or cancelled
        self.user_interface.run_button.setEnabled(True)

        # Check if there was an error and display the appropriate message
        if self.worker.error_message:
            self.update_error_label(self.worker.error_message)
        else:
            self.user_interface.run_label_error.setText(
                "Your PoreSippr run has been successfully terminated")
            self.user_interface.run_label_error.show()

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
        text_browser.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding
        )

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
                message = CustomMessageBox()
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

            # Disable the configuration_button
            self.user_interface.configuration_button.setEnabled(False)

            # Disable the sequence_info_button
            self.user_interface.sequence_info_button.setEnabled(False)

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

            # Create variable for the folder path
            folder_path = os.path.join(self.working_dir, 'output')

            # Create a Worker instance and connect its finished signal to a
            # slot method
            self.worker = Worker(
                folder_path=folder_path,
                output_folder=self.image_path,
                csv_path=self.csv_path,
                complete=complete,
                configuration_file=self.configuration_file,
                metadata_file=self.metadata_file,
                lab_name=self.lab_name,
                run_name=self.run_name,
                pid_store=self.pid_store
            )
            self.worker.finished.connect(self.on_worker_finished)
            self.worker.start()

            # Connect the Worker's error signal to the update_error_label slot
            self.worker.error.connect(self.update_error_label)

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
                QCoreApplication.processEvents()

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
                    message = CustomMessageBox()
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
                    QCoreApplication.processEvents()

            # Enable the run button again after the run is finished or
            # cancelled
            self.user_interface.run_button.setEnabled(True)

            # Enable the configuration_button
            self.user_interface.configuration_button.setEnabled(True)

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

            # Apply the CSS to the button
            self.user_interface.run_button.setStyleSheet(
                "QPushButton { border: 1px solid #007bff; "
                "border-radius: 4px; background-color: #007bff; "
                "color: white; padding: 5px 10px; }"
                "QPushButton:hover { background-color: #0056b3; }"
                "QPushButton:pressed { background-color: #003f7f; }"
            )

            # Show the message
            self.user_interface.run_label_error.show()

            # Stop the timer
            self.timer.stop()

            # Uncheck the cancel button
            self.user_interface.cancel_button.setChecked(False)

            # Disable the cancel button
            self.user_interface.cancel_button.setEnabled(False)

            # Enable the configuration_button
            self.user_interface.configuration_button.setEnabled(True)

            # Terminate the worker thread
            self.worker.terminate()

            # Terminate any external processes
            for pid in self.pid_store:
                try:
                    os.kill(pid, signal.SIGTERM)
                except ProcessLookupError:
                    pass  # Process might have already terminated

            # Update the number of pages
            self.update_button_states()

            # Get the list of images after the dialog box is closed
            images = self.get_images(path=self.image_path)

            # If there are new images, add them to the GUI
            if len(images) > self.user_interface.progress_widget.count():
                for image_path in images[
                                  self.user_interface.progress_widget
                                  .count():]:
                    self.add_html_to_gui(image_path)

        # Check if the "Cancel" button was clicked
        elif response == QMessageBox.Cancel:
            # Create a new message box
            message = CustomMessageBox()

            # Set the title of the message box
            message.setWindowTitle("Not cancelled")

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
            message = CustomMessageBox()
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
                # Additionally, terminate any external processes
                for pid in self.pid_store:
                    try:
                        os.kill(pid, signal.SIGTERM)
                    except ProcessLookupError:
                        pass  # Process might have already terminated
                event.accept()
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

    # # Print the $PATH environment variable
    # print("Current $PATH:", os.environ['PATH'])
    #
    # # Determine the base path of the current Python file
    base_path = determine_script_path()

    # os.environ['PATH'] = base_path + os.pathsep + os.environ['PATH']
    #
    # print("Updated $PATH:", os.environ['PATH'])

    # Create the application
    app = QApplication(sys.argv)

    # Ensure that the event loop is interrupted by SIGINT
    timer = QTimer()
    timer.start(500)  # Every 500ms, the event loop will be interrupted
    timer.timeout.connect(lambda: None)

    QFontDatabase.addApplicationFont(os.path.join(
        base_path, 'fonts', 'segoeui.ttf'))
    QFontDatabase.addApplicationFont(
        os.path.join(base_path, 'fonts', 'segoeuib.ttf'))
    window = MainWindow()
    app.exec()

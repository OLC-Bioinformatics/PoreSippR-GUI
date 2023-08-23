# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'GUI_BASEdCtgNC.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

import files_rc

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1000, 720)
        MainWindow.setMinimumSize(QSize(1000, 720))
        palette = QPalette()
        brush = QBrush(QColor(255, 255, 255, 255))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.WindowText, brush)
        brush1 = QBrush(QColor(0, 0, 0, 0))
        brush1.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Button, brush1)
        brush2 = QBrush(QColor(66, 73, 90, 255))
        brush2.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Light, brush2)
        brush3 = QBrush(QColor(55, 61, 75, 255))
        brush3.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Midlight, brush3)
        brush4 = QBrush(QColor(22, 24, 30, 255))
        brush4.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Dark, brush4)
        brush5 = QBrush(QColor(29, 32, 40, 255))
        brush5.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Mid, brush5)
        brush6 = QBrush(QColor(210, 210, 210, 255))
        brush6.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Text, brush6)
        palette.setBrush(QPalette.Active, QPalette.BrightText, brush)
        palette.setBrush(QPalette.Active, QPalette.ButtonText, brush)
        palette.setBrush(QPalette.Active, QPalette.Base, brush1)
        palette.setBrush(QPalette.Active, QPalette.Window, brush1)
        brush7 = QBrush(QColor(0, 0, 0, 255))
        brush7.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Shadow, brush7)
        brush8 = QBrush(QColor(85, 170, 255, 255))
        brush8.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Highlight, brush8)
        palette.setBrush(QPalette.Active, QPalette.Link, brush8)
        brush9 = QBrush(QColor(255, 0, 127, 255))
        brush9.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.LinkVisited, brush9)
        palette.setBrush(QPalette.Active, QPalette.AlternateBase, brush4)
        brush10 = QBrush(QColor(44, 49, 60, 255))
        brush10.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.ToolTipBase, brush10)
        palette.setBrush(QPalette.Active, QPalette.ToolTipText, brush6)
        brush11 = QBrush(QColor(210, 210, 210, 128))
        brush11.setStyle(Qt.NoBrush)
#if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette.setBrush(QPalette.Active, QPalette.PlaceholderText, brush11)
#endif
        palette.setBrush(QPalette.Inactive, QPalette.WindowText, brush)
        palette.setBrush(QPalette.Inactive, QPalette.Button, brush1)
        palette.setBrush(QPalette.Inactive, QPalette.Light, brush2)
        palette.setBrush(QPalette.Inactive, QPalette.Midlight, brush3)
        palette.setBrush(QPalette.Inactive, QPalette.Dark, brush4)
        palette.setBrush(QPalette.Inactive, QPalette.Mid, brush5)
        palette.setBrush(QPalette.Inactive, QPalette.Text, brush6)
        palette.setBrush(QPalette.Inactive, QPalette.BrightText, brush)
        palette.setBrush(QPalette.Inactive, QPalette.ButtonText, brush)
        palette.setBrush(QPalette.Inactive, QPalette.Base, brush1)
        palette.setBrush(QPalette.Inactive, QPalette.Window, brush1)
        palette.setBrush(QPalette.Inactive, QPalette.Shadow, brush7)
        palette.setBrush(QPalette.Inactive, QPalette.Highlight, brush8)
        palette.setBrush(QPalette.Inactive, QPalette.Link, brush8)
        palette.setBrush(QPalette.Inactive, QPalette.LinkVisited, brush9)
        palette.setBrush(QPalette.Inactive, QPalette.AlternateBase, brush4)
        palette.setBrush(QPalette.Inactive, QPalette.ToolTipBase, brush10)
        palette.setBrush(QPalette.Inactive, QPalette.ToolTipText, brush6)
        brush12 = QBrush(QColor(210, 210, 210, 128))
        brush12.setStyle(Qt.NoBrush)
#if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette.setBrush(QPalette.Inactive, QPalette.PlaceholderText, brush12)
#endif
        palette.setBrush(QPalette.Disabled, QPalette.WindowText, brush4)
        palette.setBrush(QPalette.Disabled, QPalette.Button, brush1)
        palette.setBrush(QPalette.Disabled, QPalette.Light, brush2)
        palette.setBrush(QPalette.Disabled, QPalette.Midlight, brush3)
        palette.setBrush(QPalette.Disabled, QPalette.Dark, brush4)
        palette.setBrush(QPalette.Disabled, QPalette.Mid, brush5)
        palette.setBrush(QPalette.Disabled, QPalette.Text, brush4)
        palette.setBrush(QPalette.Disabled, QPalette.BrightText, brush)
        palette.setBrush(QPalette.Disabled, QPalette.ButtonText, brush4)
        palette.setBrush(QPalette.Disabled, QPalette.Base, brush1)
        palette.setBrush(QPalette.Disabled, QPalette.Window, brush1)
        palette.setBrush(QPalette.Disabled, QPalette.Shadow, brush7)
        brush13 = QBrush(QColor(51, 153, 255, 255))
        brush13.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Disabled, QPalette.Highlight, brush13)
        palette.setBrush(QPalette.Disabled, QPalette.Link, brush8)
        palette.setBrush(QPalette.Disabled, QPalette.LinkVisited, brush9)
        palette.setBrush(QPalette.Disabled, QPalette.AlternateBase, brush10)
        palette.setBrush(QPalette.Disabled, QPalette.ToolTipBase, brush10)
        palette.setBrush(QPalette.Disabled, QPalette.ToolTipText, brush6)
        brush14 = QBrush(QColor(210, 210, 210, 128))
        brush14.setStyle(Qt.NoBrush)
#if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette.setBrush(QPalette.Disabled, QPalette.PlaceholderText, brush14)
#endif
        MainWindow.setPalette(palette)
        font = QFont()
        font.setFamily(u"Segoe UI")
        font.setPointSize(10)
        MainWindow.setFont(font)
        MainWindow.setStyleSheet(u"QMainWindow {background: transparent; }\n"
"QToolTip {\n"
"	color: #ffffff;\n"
"	background-color: rgba(27, 29, 35, 160);\n"
"	border: 1px solid rgb(40, 40, 40);\n"
"	border-radius: 2px;\n"
"}")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.centralwidget.setStyleSheet(u"background: transparent;\n"
"color: rgb(210, 210, 210);")
        self.horizontalLayout = QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(10, 10, 10, 10)
        self.frame_main = QFrame(self.centralwidget)
        self.frame_main.setObjectName(u"frame_main")
        self.frame_main.setStyleSheet(u"/* LINE EDIT */\n"
"QLineEdit {\n"
"	background-color: rgb(27, 29, 35);\n"
"	border-radius: 5px;\n"
"	border: 2px solid rgb(27, 29, 35);\n"
"	padding-left: 10px;\n"
"}\n"
"QLineEdit:hover {\n"
"	border: 2px solid rgb(64, 71, 88);\n"
"}\n"
"QLineEdit:focus {\n"
"	border: 2px solid rgb(91, 101, 124);\n"
"}\n"
"\n"
"/* SCROLL BARS */\n"
"QScrollBar:horizontal {\n"
"    border: none;\n"
"    background: rgb(52, 59, 72);\n"
"    height: 14px;\n"
"    margin: 0px 21px 0 21px;\n"
"	border-radius: 0px;\n"
"}\n"
"QScrollBar::handle:horizontal {\n"
"    background: rgb(85, 170, 255);\n"
"    min-width: 25px;\n"
"	border-radius: 7px\n"
"}\n"
"QScrollBar::add-line:horizontal {\n"
"    border: none;\n"
"    background: rgb(55, 63, 77);\n"
"    width: 20px;\n"
"	border-top-right-radius: 7px;\n"
"    border-bottom-right-radius: 7px;\n"
"    subcontrol-position: right;\n"
"    subcontrol-origin: margin;\n"
"}\n"
"QScrollBar::sub-line:horizontal {\n"
"    border: none;\n"
"    background: rgb(55, 63, 77);\n"
"    width: 20px;\n"
""
                        "	border-top-left-radius: 7px;\n"
"    border-bottom-left-radius: 7px;\n"
"    subcontrol-position: left;\n"
"    subcontrol-origin: margin;\n"
"}\n"
"QScrollBar::up-arrow:horizontal, QScrollBar::down-arrow:horizontal\n"
"{\n"
"     background: none;\n"
"}\n"
"QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal\n"
"{\n"
"     background: none;\n"
"}\n"
" QScrollBar:vertical {\n"
"	border: none;\n"
"    background: rgb(52, 59, 72);\n"
"    width: 14px;\n"
"    margin: 21px 0 21px 0;\n"
"	border-radius: 0px;\n"
" }\n"
" QScrollBar::handle:vertical {	\n"
"	background: rgb(85, 170, 255);\n"
"    min-height: 25px;\n"
"	border-radius: 7px\n"
" }\n"
" QScrollBar::add-line:vertical {\n"
"     border: none;\n"
"    background: rgb(55, 63, 77);\n"
"     height: 20px;\n"
"	border-bottom-left-radius: 7px;\n"
"    border-bottom-right-radius: 7px;\n"
"     subcontrol-position: bottom;\n"
"     subcontrol-origin: margin;\n"
" }\n"
" QScrollBar::sub-line:vertical {\n"
"	border: none;\n"
"    background: rgb(55, 63"
                        ", 77);\n"
"     height: 20px;\n"
"	border-top-left-radius: 7px;\n"
"    border-top-right-radius: 7px;\n"
"     subcontrol-position: top;\n"
"     subcontrol-origin: margin;\n"
" }\n"
" QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {\n"
"     background: none;\n"
" }\n"
"\n"
" QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {\n"
"     background: none;\n"
" }\n"
"\n"
"/* CHECKBOX */\n"
"QCheckBox::indicator {\n"
"    border: 3px solid rgb(52, 59, 72);\n"
"	width: 15px;\n"
"	height: 15px;\n"
"	border-radius: 10px;\n"
"    background: rgb(44, 49, 60);\n"
"}\n"
"QCheckBox::indicator:hover {\n"
"    border: 3px solid rgb(58, 66, 81);\n"
"}\n"
"QCheckBox::indicator:checked {\n"
"    background: 3px solid rgb(52, 59, 72);\n"
"	border: 3px solid rgb(52, 59, 72);	\n"
"	background-image: url(:/16x16/icons/16x16/cil-check-alt.png);\n"
"}\n"
"\n"
"/* RADIO BUTTON */\n"
"QRadioButton::indicator {\n"
"    border: 3px solid rgb(52, 59, 72);\n"
"	width: 15px;\n"
"	height: 15px;\n"
"	border-radius"
                        ": 10px;\n"
"    background: rgb(44, 49, 60);\n"
"}\n"
"QRadioButton::indicator:hover {\n"
"    border: 3px solid rgb(58, 66, 81);\n"
"}\n"
"QRadioButton::indicator:checked {\n"
"    background: 3px solid rgb(94, 106, 130);\n"
"	border: 3px solid rgb(52, 59, 72);	\n"
"}\n"
"\n"
"/* COMBOBOX */\n"
"QComboBox{\n"
"	background-color: rgb(27, 29, 35);\n"
"	border-radius: 5px;\n"
"	border: 2px solid rgb(27, 29, 35);\n"
"	padding: 5px;\n"
"	padding-left: 10px;\n"
"}\n"
"QComboBox:hover{\n"
"	border: 2px solid rgb(64, 71, 88);\n"
"}\n"
"QComboBox::drop-down {\n"
"	subcontrol-origin: padding;\n"
"	subcontrol-position: top right;\n"
"	width: 25px; \n"
"	border-left-width: 3px;\n"
"	border-left-color: rgba(39, 44, 54, 150);\n"
"	border-left-style: solid;\n"
"	border-top-right-radius: 3px;\n"
"	border-bottom-right-radius: 3px;	\n"
"	background-image: url(:/16x16/icons/16x16/cil-arrow-bottom.png);\n"
"	background-position: center;\n"
"	background-repeat: no-reperat;\n"
" }\n"
"QComboBox QAbstractItemView {\n"
"	color: rgb("
                        "85, 170, 255);	\n"
"	background-color: rgb(27, 29, 35);\n"
"	padding: 10px;\n"
"	selection-background-color: rgb(39, 44, 54);\n"
"}\n"
"\n"
"/* SLIDERS */\n"
"QSlider::groove:horizontal {\n"
"    border-radius: 9px;\n"
"    height: 18px;\n"
"	margin: 0px;\n"
"	background-color: rgb(52, 59, 72);\n"
"}\n"
"QSlider::groove:horizontal:hover {\n"
"	background-color: rgb(55, 62, 76);\n"
"}\n"
"QSlider::handle:horizontal {\n"
"    background-color: rgb(85, 170, 255);\n"
"    border: none;\n"
"    height: 18px;\n"
"    width: 18px;\n"
"    margin: 0px;\n"
"	border-radius: 9px;\n"
"}\n"
"QSlider::handle:horizontal:hover {\n"
"    background-color: rgb(105, 180, 255);\n"
"}\n"
"QSlider::handle:horizontal:pressed {\n"
"    background-color: rgb(65, 130, 195);\n"
"}\n"
"\n"
"QSlider::groove:vertical {\n"
"    border-radius: 9px;\n"
"    width: 18px;\n"
"    margin: 0px;\n"
"	background-color: rgb(52, 59, 72);\n"
"}\n"
"QSlider::groove:vertical:hover {\n"
"	background-color: rgb(55, 62, 76);\n"
"}\n"
"QSlider::handle:verti"
                        "cal {\n"
"    background-color: rgb(85, 170, 255);\n"
"	border: none;\n"
"    height: 18px;\n"
"    width: 18px;\n"
"    margin: 0px;\n"
"	border-radius: 9px;\n"
"}\n"
"QSlider::handle:vertical:hover {\n"
"    background-color: rgb(105, 180, 255);\n"
"}\n"
"QSlider::handle:vertical:pressed {\n"
"    background-color: rgb(65, 130, 195);\n"
"}\n"
"\n"
"")
        self.frame_main.setFrameShape(QFrame.NoFrame)
        self.frame_main.setFrameShadow(QFrame.Raised)
        self.verticalLayout = QVBoxLayout(self.frame_main)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.frame_top = QFrame(self.frame_main)
        self.frame_top.setObjectName(u"frame_top")
        self.frame_top.setMinimumSize(QSize(0, 65))
        self.frame_top.setMaximumSize(QSize(16777215, 65))
        self.frame_top.setStyleSheet(u"background-color: transparent;")
        self.frame_top.setFrameShape(QFrame.NoFrame)
        self.frame_top.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_3 = QHBoxLayout(self.frame_top)
        self.horizontalLayout_3.setSpacing(0)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.frame_toggle = QFrame(self.frame_top)
        self.frame_toggle.setObjectName(u"frame_toggle")
        self.frame_toggle.setMaximumSize(QSize(70, 16777215))
        self.frame_toggle.setStyleSheet(u"background-color: rgb(27, 29, 35);")
        self.frame_toggle.setFrameShape(QFrame.NoFrame)
        self.frame_toggle.setFrameShadow(QFrame.Raised)
        self.verticalLayout_3 = QVBoxLayout(self.frame_toggle)
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.btn_toggle_menu = QPushButton(self.frame_toggle)
        self.btn_toggle_menu.setObjectName(u"btn_toggle_menu")
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btn_toggle_menu.sizePolicy().hasHeightForWidth())
        self.btn_toggle_menu.setSizePolicy(sizePolicy)
        self.btn_toggle_menu.setStyleSheet(u"QPushButton {\n"
"	background-image: url(:/24x24/icons/24x24/cil-menu.png);\n"
"	background-position: center;\n"
"	background-repeat: no-reperat;\n"
"	border: none;\n"
"	background-color: rgb(27, 29, 35);\n"
"}\n"
"QPushButton:hover {\n"
"	background-color: rgb(33, 37, 43);\n"
"}\n"
"QPushButton:pressed {	\n"
"	background-color: rgb(85, 170, 255);\n"
"}")

        self.verticalLayout_3.addWidget(self.btn_toggle_menu)


        self.horizontalLayout_3.addWidget(self.frame_toggle)

        self.frame_top_right = QFrame(self.frame_top)
        self.frame_top_right.setObjectName(u"frame_top_right")
        self.frame_top_right.setStyleSheet(u"background: transparent;")
        self.frame_top_right.setFrameShape(QFrame.NoFrame)
        self.frame_top_right.setFrameShadow(QFrame.Raised)
        self.verticalLayout_2 = QVBoxLayout(self.frame_top_right)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.frame_top_btns = QFrame(self.frame_top_right)
        self.frame_top_btns.setObjectName(u"frame_top_btns")
        self.frame_top_btns.setMaximumSize(QSize(16777215, 42))
        self.frame_top_btns.setStyleSheet(u"background-color: rgba(27, 29, 35, 200)")
        self.frame_top_btns.setFrameShape(QFrame.NoFrame)
        self.frame_top_btns.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_4 = QHBoxLayout(self.frame_top_btns)
        self.horizontalLayout_4.setSpacing(0)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.frame_label_top_btns = QFrame(self.frame_top_btns)
        self.frame_label_top_btns.setObjectName(u"frame_label_top_btns")
        sizePolicy1 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.frame_label_top_btns.sizePolicy().hasHeightForWidth())
        self.frame_label_top_btns.setSizePolicy(sizePolicy1)
        self.frame_label_top_btns.setFrameShape(QFrame.NoFrame)
        self.frame_label_top_btns.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_10 = QHBoxLayout(self.frame_label_top_btns)
        self.horizontalLayout_10.setSpacing(0)
        self.horizontalLayout_10.setObjectName(u"horizontalLayout_10")
        self.horizontalLayout_10.setContentsMargins(5, 0, 10, 0)
        self.frame_icon_top_bar = QFrame(self.frame_label_top_btns)
        self.frame_icon_top_bar.setObjectName(u"frame_icon_top_bar")
        self.frame_icon_top_bar.setMaximumSize(QSize(30, 30))
        self.frame_icon_top_bar.setStyleSheet(u"background: transparent;\n"
"background-image: url(:/16x16/icons/16x16/cil-chevron-right.png);\n"
"background-position: center;\n"
"background-repeat: no-repeat;\n"
"")
        self.frame_icon_top_bar.setFrameShape(QFrame.StyledPanel)
        self.frame_icon_top_bar.setFrameShadow(QFrame.Raised)

        self.horizontalLayout_10.addWidget(self.frame_icon_top_bar)

        self.label_title_bar_top = QLabel(self.frame_label_top_btns)
        self.label_title_bar_top.setObjectName(u"label_title_bar_top")
        font1 = QFont()
        font1.setFamily(u"Segoe UI")
        font1.setPointSize(10)
        font1.setBold(True)
        font1.setWeight(75)
        self.label_title_bar_top.setFont(font1)
        self.label_title_bar_top.setStyleSheet(u"background: transparent;\n"
"")

        self.horizontalLayout_10.addWidget(self.label_title_bar_top)


        self.horizontalLayout_4.addWidget(self.frame_label_top_btns)

        self.frame_btns_right = QFrame(self.frame_top_btns)
        self.frame_btns_right.setObjectName(u"frame_btns_right")
        sizePolicy1.setHeightForWidth(self.frame_btns_right.sizePolicy().hasHeightForWidth())
        self.frame_btns_right.setSizePolicy(sizePolicy1)
        self.frame_btns_right.setMaximumSize(QSize(120, 16777215))
        self.frame_btns_right.setFrameShape(QFrame.NoFrame)
        self.frame_btns_right.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_5 = QHBoxLayout(self.frame_btns_right)
        self.horizontalLayout_5.setSpacing(0)
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.horizontalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.btn_minimize = QPushButton(self.frame_btns_right)
        self.btn_minimize.setObjectName(u"btn_minimize")
        sizePolicy2 = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.btn_minimize.sizePolicy().hasHeightForWidth())
        self.btn_minimize.setSizePolicy(sizePolicy2)
        self.btn_minimize.setMinimumSize(QSize(40, 0))
        self.btn_minimize.setMaximumSize(QSize(40, 16777215))
        self.btn_minimize.setStyleSheet(u"QPushButton {	\n"
"	border: none;\n"
"	background-color: transparent;\n"
"}\n"
"QPushButton:hover {\n"
"	background-color: rgb(52, 59, 72);\n"
"}\n"
"QPushButton:pressed {	\n"
"	background-color: rgb(85, 170, 255);\n"
"}")
        icon = QIcon()
        icon.addFile(u":/16x16/icons/16x16/cil-window-minimize.png", QSize(), QIcon.Normal, QIcon.Off)
        self.btn_minimize.setIcon(icon)

        self.horizontalLayout_5.addWidget(self.btn_minimize)

        self.btn_maximize_restore = QPushButton(self.frame_btns_right)
        self.btn_maximize_restore.setObjectName(u"btn_maximize_restore")
        sizePolicy2.setHeightForWidth(self.btn_maximize_restore.sizePolicy().hasHeightForWidth())
        self.btn_maximize_restore.setSizePolicy(sizePolicy2)
        self.btn_maximize_restore.setMinimumSize(QSize(40, 0))
        self.btn_maximize_restore.setMaximumSize(QSize(40, 16777215))
        self.btn_maximize_restore.setStyleSheet(u"QPushButton {	\n"
"	border: none;\n"
"	background-color: transparent;\n"
"}\n"
"QPushButton:hover {\n"
"	background-color: rgb(52, 59, 72);\n"
"}\n"
"QPushButton:pressed {	\n"
"	background-color: rgb(85, 170, 255);\n"
"}")
        icon1 = QIcon()
        icon1.addFile(u":/16x16/icons/16x16/cil-window-maximize.png", QSize(), QIcon.Normal, QIcon.Off)
        self.btn_maximize_restore.setIcon(icon1)

        self.horizontalLayout_5.addWidget(self.btn_maximize_restore)

        self.btn_close = QPushButton(self.frame_btns_right)
        self.btn_close.setObjectName(u"btn_close")
        sizePolicy2.setHeightForWidth(self.btn_close.sizePolicy().hasHeightForWidth())
        self.btn_close.setSizePolicy(sizePolicy2)
        self.btn_close.setMinimumSize(QSize(40, 0))
        self.btn_close.setMaximumSize(QSize(40, 16777215))
        self.btn_close.setStyleSheet(u"QPushButton {	\n"
"	border: none;\n"
"	background-color: transparent;\n"
"}\n"
"QPushButton:hover {\n"
"	background-color: rgb(52, 59, 72);\n"
"}\n"
"QPushButton:pressed {	\n"
"	background-color: rgb(85, 170, 255);\n"
"}")
        icon2 = QIcon()
        icon2.addFile(u":/16x16/icons/16x16/cil-x.png", QSize(), QIcon.Normal, QIcon.Off)
        self.btn_close.setIcon(icon2)

        self.horizontalLayout_5.addWidget(self.btn_close)


        self.horizontalLayout_4.addWidget(self.frame_btns_right, 0, Qt.AlignRight)


        self.verticalLayout_2.addWidget(self.frame_top_btns)

        self.frame_top_info = QFrame(self.frame_top_right)
        self.frame_top_info.setObjectName(u"frame_top_info")
        self.frame_top_info.setMaximumSize(QSize(16777215, 65))
        self.frame_top_info.setStyleSheet(u"background-color: rgb(39, 44, 54);")
        self.frame_top_info.setFrameShape(QFrame.NoFrame)
        self.frame_top_info.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_8 = QHBoxLayout(self.frame_top_info)
        self.horizontalLayout_8.setSpacing(0)
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.horizontalLayout_8.setContentsMargins(10, 0, 10, 0)
        self.label_top_info_1 = QLabel(self.frame_top_info)
        self.label_top_info_1.setObjectName(u"label_top_info_1")
        self.label_top_info_1.setMaximumSize(QSize(16777215, 15))
        font2 = QFont()
        font2.setFamily(u"Segoe UI")
        self.label_top_info_1.setFont(font2)
        self.label_top_info_1.setStyleSheet(u"color: rgb(98, 103, 111); ")

        self.horizontalLayout_8.addWidget(self.label_top_info_1)

        self.label_top_info_2 = QLabel(self.frame_top_info)
        self.label_top_info_2.setObjectName(u"label_top_info_2")
        self.label_top_info_2.setMinimumSize(QSize(0, 0))
        self.label_top_info_2.setMaximumSize(QSize(250, 20))
        font3 = QFont()
        font3.setFamily(u"Segoe UI")
        font3.setBold(True)
        font3.setWeight(75)
        self.label_top_info_2.setFont(font3)
        self.label_top_info_2.setStyleSheet(u"color: rgb(98, 103, 111);")
        self.label_top_info_2.setAlignment(Qt.AlignCenter)

        self.horizontalLayout_8.addWidget(self.label_top_info_2)


        self.verticalLayout_2.addWidget(self.frame_top_info)


        self.horizontalLayout_3.addWidget(self.frame_top_right)


        self.verticalLayout.addWidget(self.frame_top)

        self.frame_center = QFrame(self.frame_main)
        self.frame_center.setObjectName(u"frame_center")
        sizePolicy.setHeightForWidth(self.frame_center.sizePolicy().hasHeightForWidth())
        self.frame_center.setSizePolicy(sizePolicy)
        self.frame_center.setStyleSheet(u"background-color: rgb(40, 44, 52);")
        self.frame_center.setFrameShape(QFrame.NoFrame)
        self.frame_center.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_2 = QHBoxLayout(self.frame_center)
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.frame_left_menu = QFrame(self.frame_center)
        self.frame_left_menu.setObjectName(u"frame_left_menu")
        sizePolicy3 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.frame_left_menu.sizePolicy().hasHeightForWidth())
        self.frame_left_menu.setSizePolicy(sizePolicy3)
        self.frame_left_menu.setMinimumSize(QSize(70, 0))
        self.frame_left_menu.setMaximumSize(QSize(70, 16777215))
        self.frame_left_menu.setLayoutDirection(Qt.LeftToRight)
        self.frame_left_menu.setStyleSheet(u"background-color: rgb(27, 29, 35);")
        self.frame_left_menu.setFrameShape(QFrame.NoFrame)
        self.frame_left_menu.setFrameShadow(QFrame.Raised)
        self.verticalLayout_5 = QVBoxLayout(self.frame_left_menu)
        self.verticalLayout_5.setSpacing(1)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.verticalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.frame_menus = QFrame(self.frame_left_menu)
        self.frame_menus.setObjectName(u"frame_menus")
        self.frame_menus.setFrameShape(QFrame.NoFrame)
        self.frame_menus.setFrameShadow(QFrame.Raised)
        self.layout_menus = QVBoxLayout(self.frame_menus)
        self.layout_menus.setSpacing(0)
        self.layout_menus.setObjectName(u"layout_menus")
        self.layout_menus.setContentsMargins(0, 0, 0, 0)

        self.verticalLayout_5.addWidget(self.frame_menus, 0, Qt.AlignTop)

        self.frame_extra_menus = QFrame(self.frame_left_menu)
        self.frame_extra_menus.setObjectName(u"frame_extra_menus")
        sizePolicy3.setHeightForWidth(self.frame_extra_menus.sizePolicy().hasHeightForWidth())
        self.frame_extra_menus.setSizePolicy(sizePolicy3)
        self.frame_extra_menus.setFrameShape(QFrame.NoFrame)
        self.frame_extra_menus.setFrameShadow(QFrame.Raised)
        self.layout_menu_bottom = QVBoxLayout(self.frame_extra_menus)
        self.layout_menu_bottom.setSpacing(10)
        self.layout_menu_bottom.setObjectName(u"layout_menu_bottom")
        self.layout_menu_bottom.setContentsMargins(0, 0, 0, 25)
        self.label_user_icon = QLabel(self.frame_extra_menus)
        self.label_user_icon.setObjectName(u"label_user_icon")
        sizePolicy4 = QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.label_user_icon.sizePolicy().hasHeightForWidth())
        self.label_user_icon.setSizePolicy(sizePolicy4)
        self.label_user_icon.setMinimumSize(QSize(60, 60))
        self.label_user_icon.setMaximumSize(QSize(60, 60))
        font4 = QFont()
        font4.setFamily(u"Segoe UI")
        font4.setPointSize(12)
        self.label_user_icon.setFont(font4)
        self.label_user_icon.setStyleSheet(u"QLabel {\n"
"	border-radius: 30px;\n"
"	background-color: rgb(44, 49, 60);\n"
"	border: 5px solid rgb(39, 44, 54);\n"
"	background-position: center;\n"
"	background-repeat: no-repeat;\n"
"}")
        self.label_user_icon.setPixmap(QPixmap(u"icons/24x24/olcConfindrLogo.png"))
        self.label_user_icon.setScaledContents(True)
        self.label_user_icon.setAlignment(Qt.AlignCenter)

        self.layout_menu_bottom.addWidget(self.label_user_icon, 0, Qt.AlignHCenter)


        self.verticalLayout_5.addWidget(self.frame_extra_menus, 0, Qt.AlignBottom)


        self.horizontalLayout_2.addWidget(self.frame_left_menu)

        self.frame_content_right = QFrame(self.frame_center)
        self.frame_content_right.setObjectName(u"frame_content_right")
        self.frame_content_right.setStyleSheet(u"background-color: rgb(44, 49, 60);")
        self.frame_content_right.setFrameShape(QFrame.NoFrame)
        self.frame_content_right.setFrameShadow(QFrame.Raised)
        self.verticalLayout_4 = QVBoxLayout(self.frame_content_right)
        self.verticalLayout_4.setSpacing(0)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.frame_content = QFrame(self.frame_content_right)
        self.frame_content.setObjectName(u"frame_content")
        self.frame_content.setFrameShape(QFrame.NoFrame)
        self.frame_content.setFrameShadow(QFrame.Raised)
        self.verticalLayout_9 = QVBoxLayout(self.frame_content)
        self.verticalLayout_9.setSpacing(0)
        self.verticalLayout_9.setObjectName(u"verticalLayout_9")
        self.verticalLayout_9.setContentsMargins(5, 5, 5, 5)
        self.stackedWidget = QStackedWidget(self.frame_content)
        self.stackedWidget.setObjectName(u"stackedWidget")
        font5 = QFont()
        font5.setPointSize(7)
        self.stackedWidget.setFont(font5)
        self.stackedWidget.setStyleSheet(u"background: transparent;")
        self.page_home = QWidget()
        self.page_home.setObjectName(u"page_home")
        self.verticalLayout_10 = QVBoxLayout(self.page_home)
        self.verticalLayout_10.setObjectName(u"verticalLayout_10")
        self.label_6 = QLabel(self.page_home)
        self.label_6.setObjectName(u"label_6")
        font6 = QFont()
        font6.setFamily(u"Segoe UI")
        font6.setPointSize(40)
        self.label_6.setFont(font6)
        self.label_6.setStyleSheet(u"")
        self.label_6.setAlignment(Qt.AlignCenter)

        self.verticalLayout_10.addWidget(self.label_6)

        self.label = QLabel(self.page_home)
        self.label.setObjectName(u"label")
        font7 = QFont()
        font7.setFamily(u"Segoe UI")
        font7.setPointSize(14)
        self.label.setFont(font7)
        self.label.setAlignment(Qt.AlignCenter)

        self.verticalLayout_10.addWidget(self.label)

        self.label_7 = QLabel(self.page_home)
        self.label_7.setObjectName(u"label_7")
        font8 = QFont()
        font8.setFamily(u"Segoe UI")
        font8.setPointSize(15)
        self.label_7.setFont(font8)
        self.label_7.setAlignment(Qt.AlignCenter)

        self.verticalLayout_10.addWidget(self.label_7)

        self.stackedWidget.addWidget(self.page_home)
        self.page_analysis = QWidget()
        self.page_analysis.setObjectName(u"page_analysis")
        self.verticalLayout_16 = QVBoxLayout(self.page_analysis)
        self.verticalLayout_16.setObjectName(u"verticalLayout_16")
        self.frame_div_content_2 = QFrame(self.page_analysis)
        self.frame_div_content_2.setObjectName(u"frame_div_content_2")
        self.frame_div_content_2.setMinimumSize(QSize(0, 110))
        self.frame_div_content_2.setMaximumSize(QSize(16777215, 110))
        self.frame_div_content_2.setStyleSheet(u"background-color: rgb(41, 45, 56);\n"
"border-radius: 5px;\n"
"")
        self.frame_div_content_2.setFrameShape(QFrame.NoFrame)
        self.frame_div_content_2.setFrameShadow(QFrame.Raised)
        self.verticalLayout_17 = QVBoxLayout(self.frame_div_content_2)
        self.verticalLayout_17.setSpacing(0)
        self.verticalLayout_17.setObjectName(u"verticalLayout_17")
        self.verticalLayout_17.setContentsMargins(0, 0, 0, 0)
        self.label_2 = QLabel(self.frame_div_content_2)
        self.label_2.setObjectName(u"label_2")
        font9 = QFont()
        font9.setFamily(u"Segoe UI")
        font9.setPointSize(26)
        self.label_2.setFont(font9)
        self.label_2.setAlignment(Qt.AlignCenter)

        self.verticalLayout_17.addWidget(self.label_2)

        self.label_3 = QLabel(self.frame_div_content_2)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setFont(font7)
        self.label_3.setAlignment(Qt.AlignCenter)

        self.verticalLayout_17.addWidget(self.label_3)


        self.verticalLayout_16.addWidget(self.frame_div_content_2)

        self.frame_5 = QFrame(self.page_analysis)
        self.frame_5.setObjectName(u"frame_5")
        self.frame_5.setFrameShape(QFrame.StyledPanel)
        self.frame_5.setFrameShadow(QFrame.Raised)
        self.verticalLayout_14 = QVBoxLayout(self.frame_5)
        self.verticalLayout_14.setObjectName(u"verticalLayout_14")
        self.sequenceBtn = QPushButton(self.frame_5)
        self.sequenceBtn.setObjectName(u"sequenceBtn")
        self.sequenceBtn.setMinimumSize(QSize(150, 30))
        font10 = QFont()
        font10.setFamily(u"Segoe UI")
        font10.setPointSize(9)
        self.sequenceBtn.setFont(font10)
        self.sequenceBtn.setStyleSheet(u"QPushButton {\n"
"	border: 2px solid rgb(52, 59, 72);\n"
"	border-radius: 5px;	\n"
"	background-color: rgb(52, 59, 72);\n"
"}\n"
"QPushButton:hover {\n"
"	background-color: rgb(57, 65, 80);\n"
"	border: 2px solid rgb(61, 70, 86);\n"
"}\n"
"QPushButton:pressed {	\n"
"	background-color: rgb(35, 40, 49);\n"
"	border: 2px solid rgb(43, 50, 61);\n"
"}")
        icon3 = QIcon()
        icon3.addFile(u":/16x16/icons/16x16/cil-folder-open.png", QSize(), QIcon.Normal, QIcon.Off)
        self.sequenceBtn.setIcon(icon3)

        self.verticalLayout_14.addWidget(self.sequenceBtn)

        self.analyzeLabelError = QLabel(self.frame_5)
        self.analyzeLabelError.setObjectName(u"analyzeLabelError")
        palette1 = QPalette()
        brush15 = QBrush(QColor(190, 9, 9, 255))
        brush15.setStyle(Qt.SolidPattern)
        palette1.setBrush(QPalette.Active, QPalette.WindowText, brush15)
        palette1.setBrush(QPalette.Active, QPalette.Button, brush1)
        palette1.setBrush(QPalette.Active, QPalette.Text, brush15)
        palette1.setBrush(QPalette.Active, QPalette.ButtonText, brush15)
        palette1.setBrush(QPalette.Active, QPalette.Base, brush1)
        palette1.setBrush(QPalette.Active, QPalette.Window, brush1)
        brush16 = QBrush(QColor(190, 9, 9, 128))
        brush16.setStyle(Qt.NoBrush)
#if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette1.setBrush(QPalette.Active, QPalette.PlaceholderText, brush16)
#endif
        palette1.setBrush(QPalette.Inactive, QPalette.WindowText, brush15)
        palette1.setBrush(QPalette.Inactive, QPalette.Button, brush1)
        palette1.setBrush(QPalette.Inactive, QPalette.Text, brush15)
        palette1.setBrush(QPalette.Inactive, QPalette.ButtonText, brush15)
        palette1.setBrush(QPalette.Inactive, QPalette.Base, brush1)
        palette1.setBrush(QPalette.Inactive, QPalette.Window, brush1)
        brush17 = QBrush(QColor(190, 9, 9, 128))
        brush17.setStyle(Qt.NoBrush)
#if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette1.setBrush(QPalette.Inactive, QPalette.PlaceholderText, brush17)
#endif
        palette1.setBrush(QPalette.Disabled, QPalette.WindowText, brush15)
        palette1.setBrush(QPalette.Disabled, QPalette.Button, brush1)
        palette1.setBrush(QPalette.Disabled, QPalette.Text, brush15)
        palette1.setBrush(QPalette.Disabled, QPalette.ButtonText, brush15)
        palette1.setBrush(QPalette.Disabled, QPalette.Base, brush1)
        palette1.setBrush(QPalette.Disabled, QPalette.Window, brush1)
        brush18 = QBrush(QColor(190, 9, 9, 128))
        brush18.setStyle(Qt.NoBrush)
#if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette1.setBrush(QPalette.Disabled, QPalette.PlaceholderText, brush18)
#endif
        self.analyzeLabelError.setPalette(palette1)
        self.analyzeLabelError.setFont(font10)
        self.analyzeLabelError.setStyleSheet(u"color:rgb(190, 9, 9);")
        self.analyzeLabelError.setAlignment(Qt.AlignCenter)

        self.verticalLayout_14.addWidget(self.analyzeLabelError)

        self.verticalLayout_14.setStretch(0, 1)

        self.verticalLayout_16.addWidget(self.frame_5, 0, Qt.AlignVCenter)

        self.frame_div_content_3 = QFrame(self.page_analysis)
        self.frame_div_content_3.setObjectName(u"frame_div_content_3")
        self.frame_div_content_3.setMinimumSize(QSize(0, 110))
        self.frame_div_content_3.setMaximumSize(QSize(16777215, 180))
        self.frame_div_content_3.setStyleSheet(u"background-color: rgb(41, 45, 56);\n"
"border-radius: 5px;\n"
"")
        self.frame_div_content_3.setFrameShape(QFrame.NoFrame)
        self.frame_div_content_3.setFrameShadow(QFrame.Raised)
        self.gridLayout_5 = QGridLayout(self.frame_div_content_3)
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.gridLayout_5.setContentsMargins(-1, 9, -1, -1)
        self.baseCutoffInput = QLineEdit(self.frame_div_content_3)
        self.baseCutoffInput.setObjectName(u"baseCutoffInput")
        self.baseCutoffInput.setMinimumSize(QSize(0, 30))
        self.baseCutoffInput.setStyleSheet(u"QLineEdit {\n"
"	background-color: rgb(27, 29, 35);\n"
"	border-radius: 5px;\n"
"	border: 2px solid rgb(27, 29, 35);\n"
"	padding-left: 10px;\n"
"}\n"
"QLineEdit:hover {\n"
"	border: 2px solid rgb(64, 71, 88);\n"
"}\n"
"QLineEdit:focus {\n"
"	border: 2px solid rgb(91, 101, 124);\n"
"}")

        self.gridLayout_5.addWidget(self.baseCutoffInput, 1, 2, 1, 1)

        self.FASTAcheckBox = QCheckBox(self.frame_div_content_3)
        self.FASTAcheckBox.setObjectName(u"FASTAcheckBox")
        self.FASTAcheckBox.setAutoFillBackground(False)
        self.FASTAcheckBox.setStyleSheet(u"")

        self.gridLayout_5.addWidget(self.FASTAcheckBox, 1, 1, 1, 1)

        self.dataDropdownMenu = QComboBox(self.frame_div_content_3)
        self.dataDropdownMenu.addItem("")
        self.dataDropdownMenu.addItem("")
        self.dataDropdownMenu.setObjectName(u"dataDropdownMenu")
        self.dataDropdownMenu.setFont(font10)
        self.dataDropdownMenu.setAutoFillBackground(False)
        self.dataDropdownMenu.setStyleSheet(u"QComboBox{\n"
"	background-color: rgb(27, 29, 35);\n"
"	border-radius: 5px;\n"
"	border: 2px solid rgb(27, 29, 35);\n"
"	padding: 5px;\n"
"	padding-left: 10px;\n"
"}\n"
"QComboBox:hover{\n"
"	border: 2px solid rgb(64, 71, 88);\n"
"}\n"
"QComboBox QAbstractItemView {\n"
"	color: rgb(85, 170, 255);	\n"
"	background-color: rgb(27, 29, 35);\n"
"	padding: 10px;\n"
"	selection-background-color: rgb(39, 44, 54);\n"
"}")
        self.dataDropdownMenu.setIconSize(QSize(16, 16))
        self.dataDropdownMenu.setFrame(True)

        self.gridLayout_5.addWidget(self.dataDropdownMenu, 1, 3, 1, 1)

        self.labelBoxMainArguements = QLabel(self.frame_div_content_3)
        self.labelBoxMainArguements.setObjectName(u"labelBoxMainArguements")
        self.labelBoxMainArguements.setFont(font1)
        self.labelBoxMainArguements.setStyleSheet(u"")

        self.gridLayout_5.addWidget(self.labelBoxMainArguements, 0, 0, 1, 4, Qt.AlignBottom)

        self.RMLSTcheckBox = QCheckBox(self.frame_div_content_3)
        self.RMLSTcheckBox.setObjectName(u"RMLSTcheckBox")
        self.RMLSTcheckBox.setAutoFillBackground(False)
        self.RMLSTcheckBox.setStyleSheet(u"")

        self.gridLayout_5.addWidget(self.RMLSTcheckBox, 1, 0, 1, 1)

        self.gridLayout_5.setRowStretch(1, 3)

        self.verticalLayout_16.addWidget(self.frame_div_content_3)

        self.frame_div_content_4 = QFrame(self.page_analysis)
        self.frame_div_content_4.setObjectName(u"frame_div_content_4")
        self.frame_div_content_4.setMinimumSize(QSize(0, 110))
        self.frame_div_content_4.setMaximumSize(QSize(16777215, 250))
        self.frame_div_content_4.setStyleSheet(u"background-color: rgb(41, 45, 56);\n"
"border-radius: 5px;\n"
"")
        self.frame_div_content_4.setFrameShape(QFrame.NoFrame)
        self.frame_div_content_4.setFrameShadow(QFrame.Raised)
        self.gridLayout_4 = QGridLayout(self.frame_div_content_4)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.frame_div_content_6 = QFrame(self.frame_div_content_4)
        self.frame_div_content_6.setObjectName(u"frame_div_content_6")
        self.frame_div_content_6.setMinimumSize(QSize(0, 110))
        self.frame_div_content_6.setMaximumSize(QSize(16777215, 250))
        self.frame_div_content_6.setStyleSheet(u"background-color:rgb(67, 73, 91);\n"
"border-radius: 5px;\n"
"")
        self.frame_div_content_6.setFrameShape(QFrame.NoFrame)
        self.frame_div_content_6.setFrameShadow(QFrame.Raised)
        self.verticalLayout_13 = QVBoxLayout(self.frame_div_content_6)
        self.verticalLayout_13.setObjectName(u"verticalLayout_13")
        self.verbosityDropdownMenu = QComboBox(self.frame_div_content_6)
        self.verbosityDropdownMenu.addItem("")
        self.verbosityDropdownMenu.addItem("")
        self.verbosityDropdownMenu.addItem("")
        self.verbosityDropdownMenu.setObjectName(u"verbosityDropdownMenu")
        self.verbosityDropdownMenu.setFont(font10)
        self.verbosityDropdownMenu.setAutoFillBackground(False)
        self.verbosityDropdownMenu.setStyleSheet(u"QComboBox{\n"
"	background-color: rgb(27, 29, 35);\n"
"	border-radius: 5px;\n"
"	border: 2px solid rgb(27, 29, 35);\n"
"	padding: 5px;\n"
"	padding-left: 10px;\n"
"}\n"
"QComboBox:hover{\n"
"	border: 2px solid rgb(64, 71, 88);\n"
"}\n"
"QComboBox QAbstractItemView {\n"
"	color: rgb(85, 170, 255);	\n"
"	background-color: rgb(27, 29, 35);\n"
"	padding: 10px;\n"
"	selection-background-color: rgb(39, 44, 54);\n"
"}")
        self.verbosityDropdownMenu.setIconSize(QSize(16, 16))
        self.verbosityDropdownMenu.setFrame(True)

        self.verticalLayout_13.addWidget(self.verbosityDropdownMenu)


        self.gridLayout_4.addWidget(self.frame_div_content_6, 1, 1, 1, 1)

        self.frame_div_content_5 = QFrame(self.frame_div_content_4)
        self.frame_div_content_5.setObjectName(u"frame_div_content_5")
        self.frame_div_content_5.setMinimumSize(QSize(0, 110))
        self.frame_div_content_5.setMaximumSize(QSize(16777215, 250))
        self.frame_div_content_5.setStyleSheet(u"background-color:rgb(67, 73, 91);\n"
"border-radius: 5px;\n"
"")
        self.frame_div_content_5.setFrameShape(QFrame.NoFrame)
        self.frame_div_content_5.setFrameShadow(QFrame.Raised)
        self.verticalLayout_12 = QVBoxLayout(self.frame_div_content_5)
        self.verticalLayout_12.setObjectName(u"verticalLayout_12")
        self.keepCheckBox = QCheckBox(self.frame_div_content_5)
        self.keepCheckBox.setObjectName(u"keepCheckBox")
        self.keepCheckBox.setAutoFillBackground(False)
        self.keepCheckBox.setStyleSheet(u"")

        self.verticalLayout_12.addWidget(self.keepCheckBox)

        self.versionCheckBox = QCheckBox(self.frame_div_content_5)
        self.versionCheckBox.setObjectName(u"versionCheckBox")
        self.versionCheckBox.setAutoFillBackground(False)
        self.versionCheckBox.setStyleSheet(u"")

        self.verticalLayout_12.addWidget(self.versionCheckBox)

        self.crossDetailsCheckBox = QCheckBox(self.frame_div_content_5)
        self.crossDetailsCheckBox.setObjectName(u"crossDetailsCheckBox")
        self.crossDetailsCheckBox.setAutoFillBackground(False)
        self.crossDetailsCheckBox.setStyleSheet(u"")

        self.verticalLayout_12.addWidget(self.crossDetailsCheckBox)


        self.gridLayout_4.addWidget(self.frame_div_content_5, 1, 0, 1, 1)

        self.frame_div_content_7 = QFrame(self.frame_div_content_4)
        self.frame_div_content_7.setObjectName(u"frame_div_content_7")
        self.frame_div_content_7.setMinimumSize(QSize(0, 110))
        self.frame_div_content_7.setMaximumSize(QSize(16777215, 250))
        self.frame_div_content_7.setStyleSheet(u"background-color:rgb(67, 73, 91);\n"
"border-radius: 5px;\n"
"")
        self.frame_div_content_7.setFrameShape(QFrame.NoFrame)
        self.frame_div_content_7.setFrameShadow(QFrame.Raised)
        self.gridLayout_3 = QGridLayout(self.frame_div_content_7)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.threadsInput = QLineEdit(self.frame_div_content_7)
        self.threadsInput.setObjectName(u"threadsInput")
        self.threadsInput.setMinimumSize(QSize(0, 30))
        self.threadsInput.setStyleSheet(u"QLineEdit {\n"
"	background-color: rgb(27, 29, 35);\n"
"	border-radius: 5px;\n"
"	border: 2px solid rgb(27, 29, 35);\n"
"	padding-left: 10px;\n"
"}\n"
"QLineEdit:hover {\n"
"	border: 2px solid rgb(64, 71, 88);\n"
"}\n"
"QLineEdit:focus {\n"
"	border: 2px solid rgb(91, 101, 124);\n"
"}")

        self.gridLayout_3.addWidget(self.threadsInput, 1, 0, 1, 1)

        self.reverseInput = QLineEdit(self.frame_div_content_7)
        self.reverseInput.setObjectName(u"reverseInput")
        self.reverseInput.setMinimumSize(QSize(0, 30))
        self.reverseInput.setStyleSheet(u"QLineEdit {\n"
"	background-color: rgb(27, 29, 35);\n"
"	border-radius: 5px;\n"
"	border: 2px solid rgb(27, 29, 35);\n"
"	padding-left: 10px;\n"
"}\n"
"QLineEdit:hover {\n"
"	border: 2px solid rgb(64, 71, 88);\n"
"}\n"
"QLineEdit:focus {\n"
"	border: 2px solid rgb(91, 101, 124);\n"
"}")

        self.gridLayout_3.addWidget(self.reverseInput, 2, 1, 1, 1)

        self.MMHInput = QLineEdit(self.frame_div_content_7)
        self.MMHInput.setObjectName(u"MMHInput")
        self.MMHInput.setMinimumSize(QSize(0, 30))
        self.MMHInput.setStyleSheet(u"QLineEdit {\n"
"	background-color: rgb(27, 29, 35);\n"
"	border-radius: 5px;\n"
"	border: 2px solid rgb(27, 29, 35);\n"
"	padding-left: 10px;\n"
"}\n"
"QLineEdit:hover {\n"
"	border: 2px solid rgb(64, 71, 88);\n"
"}\n"
"QLineEdit:focus {\n"
"	border: 2px solid rgb(91, 101, 124);\n"
"}")

        self.gridLayout_3.addWidget(self.MMHInput, 2, 2, 1, 1)

        self.baseFractionInput = QLineEdit(self.frame_div_content_7)
        self.baseFractionInput.setObjectName(u"baseFractionInput")
        self.baseFractionInput.setMinimumSize(QSize(0, 30))
        self.baseFractionInput.setStyleSheet(u"QLineEdit {\n"
"	background-color: rgb(27, 29, 35);\n"
"	border-radius: 5px;\n"
"	border: 2px solid rgb(27, 29, 35);\n"
"	padding-left: 10px;\n"
"}\n"
"QLineEdit:hover {\n"
"	border: 2px solid rgb(64, 71, 88);\n"
"}\n"
"QLineEdit:focus {\n"
"	border: 2px solid rgb(91, 101, 124);\n"
"}")

        self.gridLayout_3.addWidget(self.baseFractionInput, 0, 2, 1, 1)

        self.forwardInput = QLineEdit(self.frame_div_content_7)
        self.forwardInput.setObjectName(u"forwardInput")
        self.forwardInput.setMinimumSize(QSize(0, 30))
        self.forwardInput.setStyleSheet(u"QLineEdit {\n"
"	background-color: rgb(27, 29, 35);\n"
"	border-radius: 5px;\n"
"	border: 2px solid rgb(27, 29, 35);\n"
"	padding-left: 10px;\n"
"}\n"
"QLineEdit:hover {\n"
"	border: 2px solid rgb(64, 71, 88);\n"
"}\n"
"QLineEdit:focus {\n"
"	border: 2px solid rgb(91, 101, 124);\n"
"}")

        self.gridLayout_3.addWidget(self.forwardInput, 2, 0, 1, 1)

        self.TMPInput = QLineEdit(self.frame_div_content_7)
        self.TMPInput.setObjectName(u"TMPInput")
        self.TMPInput.setMinimumSize(QSize(0, 30))
        self.TMPInput.setStyleSheet(u"QLineEdit {\n"
"	background-color: rgb(27, 29, 35);\n"
"	border-radius: 5px;\n"
"	border: 2px solid rgb(27, 29, 35);\n"
"	padding-left: 10px;\n"
"}\n"
"QLineEdit:hover {\n"
"	border: 2px solid rgb(64, 71, 88);\n"
"}\n"
"QLineEdit:focus {\n"
"	border: 2px solid rgb(91, 101, 124);\n"
"}")

        self.gridLayout_3.addWidget(self.TMPInput, 0, 1, 1, 1)

        self.qualityInput = QLineEdit(self.frame_div_content_7)
        self.qualityInput.setObjectName(u"qualityInput")
        self.qualityInput.setMinimumSize(QSize(0, 30))
        self.qualityInput.setStyleSheet(u"QLineEdit {\n"
"	background-color: rgb(27, 29, 35);\n"
"	border-radius: 5px;\n"
"	border: 2px solid rgb(27, 29, 35);\n"
"	padding-left: 10px;\n"
"}\n"
"QLineEdit:hover {\n"
"	border: 2px solid rgb(64, 71, 88);\n"
"}\n"
"QLineEdit:focus {\n"
"	border: 2px solid rgb(91, 101, 124);\n"
"}")

        self.gridLayout_3.addWidget(self.qualityInput, 1, 1, 1, 1)

        self.databaseInput = QLineEdit(self.frame_div_content_7)
        self.databaseInput.setObjectName(u"databaseInput")
        self.databaseInput.setMinimumSize(QSize(0, 30))
        self.databaseInput.setStyleSheet(u"QLineEdit {\n"
"	background-color: rgb(27, 29, 35);\n"
"	border-radius: 5px;\n"
"	border: 2px solid rgb(27, 29, 35);\n"
"	padding-left: 10px;\n"
"}\n"
"QLineEdit:hover {\n"
"	border: 2px solid rgb(64, 71, 88);\n"
"}\n"
"QLineEdit:focus {\n"
"	border: 2px solid rgb(91, 101, 124);\n"
"}")

        self.gridLayout_3.addWidget(self.databaseInput, 0, 0, 1, 1)

        self.cgmlstInput = QLineEdit(self.frame_div_content_7)
        self.cgmlstInput.setObjectName(u"cgmlstInput")
        self.cgmlstInput.setMinimumSize(QSize(0, 30))
        self.cgmlstInput.setStyleSheet(u"QLineEdit {\n"
"	background-color: rgb(27, 29, 35);\n"
"	border-radius: 5px;\n"
"	border: 2px solid rgb(27, 29, 35);\n"
"	padding-left: 10px;\n"
"}\n"
"QLineEdit:hover {\n"
"	border: 2px solid rgb(64, 71, 88);\n"
"}\n"
"QLineEdit:focus {\n"
"	border: 2px solid rgb(91, 101, 124);\n"
"}")

        self.gridLayout_3.addWidget(self.cgmlstInput, 1, 2, 1, 1)


        self.gridLayout_4.addWidget(self.frame_div_content_7, 1, 2, 1, 1)

        self.labelBoxAdvancedArguements = QLabel(self.frame_div_content_4)
        self.labelBoxAdvancedArguements.setObjectName(u"labelBoxAdvancedArguements")
        self.labelBoxAdvancedArguements.setFont(font1)
        self.labelBoxAdvancedArguements.setStyleSheet(u"")

        self.gridLayout_4.addWidget(self.labelBoxAdvancedArguements, 0, 0, 1, 3, Qt.AlignBottom)

        self.gridLayout_4.setRowStretch(1, 3)

        self.verticalLayout_16.addWidget(self.frame_div_content_4)

        self.verticalLayout_16.setStretch(0, 3)
        self.verticalLayout_16.setStretch(1, 1)
        self.verticalLayout_16.setStretch(2, 1)
        self.verticalLayout_16.setStretch(3, 4)
        self.stackedWidget.addWidget(self.page_analysis)
        self.page_table = QWidget()
        self.page_table.setObjectName(u"page_table")
        self.verticalLayout_20 = QVBoxLayout(self.page_table)
        self.verticalLayout_20.setObjectName(u"verticalLayout_20")
        self.frame_div_content_8 = QFrame(self.page_table)
        self.frame_div_content_8.setObjectName(u"frame_div_content_8")
        self.frame_div_content_8.setMinimumSize(QSize(0, 110))
        self.frame_div_content_8.setMaximumSize(QSize(16777215, 110))
        self.frame_div_content_8.setStyleSheet(u"background-color: rgb(41, 45, 56);\n"
"border-radius: 5px;\n"
"")
        self.frame_div_content_8.setFrameShape(QFrame.NoFrame)
        self.frame_div_content_8.setFrameShadow(QFrame.Raised)
        self.verticalLayout_18 = QVBoxLayout(self.frame_div_content_8)
        self.verticalLayout_18.setSpacing(0)
        self.verticalLayout_18.setObjectName(u"verticalLayout_18")
        self.verticalLayout_18.setContentsMargins(0, 0, 0, 0)
        self.label_5 = QLabel(self.frame_div_content_8)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setFont(font9)
        self.label_5.setAlignment(Qt.AlignCenter)

        self.verticalLayout_18.addWidget(self.label_5)

        self.label_8 = QLabel(self.frame_div_content_8)
        self.label_8.setObjectName(u"label_8")
        self.label_8.setFont(font7)
        self.label_8.setAlignment(Qt.AlignCenter)

        self.verticalLayout_18.addWidget(self.label_8)


        self.verticalLayout_20.addWidget(self.frame_div_content_8)

        self.frame_6 = QFrame(self.page_table)
        self.frame_6.setObjectName(u"frame_6")
        self.frame_6.setFrameShape(QFrame.StyledPanel)
        self.frame_6.setFrameShadow(QFrame.Raised)
        self.verticalLayout_19 = QVBoxLayout(self.frame_6)
        self.verticalLayout_19.setObjectName(u"verticalLayout_19")
        self.resultsBtn = QPushButton(self.frame_6)
        self.resultsBtn.setObjectName(u"resultsBtn")
        self.resultsBtn.setMinimumSize(QSize(150, 30))
        self.resultsBtn.setFont(font10)
        self.resultsBtn.setStyleSheet(u"QPushButton {\n"
"	border: 2px solid rgb(52, 59, 72);\n"
"	border-radius: 5px;	\n"
"	background-color: rgb(52, 59, 72);\n"
"}\n"
"QPushButton:hover {\n"
"	background-color: rgb(57, 65, 80);\n"
"	border: 2px solid rgb(61, 70, 86);\n"
"}\n"
"QPushButton:pressed {	\n"
"	background-color: rgb(35, 40, 49);\n"
"	border: 2px solid rgb(43, 50, 61);\n"
"}")
        self.resultsBtn.setIcon(icon3)

        self.verticalLayout_19.addWidget(self.resultsBtn, 0, Qt.AlignHCenter)

        self.tableLabelError = QLabel(self.frame_6)
        self.tableLabelError.setObjectName(u"tableLabelError")
        palette2 = QPalette()
        brush19 = QBrush(QColor(147, 0, 0, 255))
        brush19.setStyle(Qt.SolidPattern)
        palette2.setBrush(QPalette.Active, QPalette.WindowText, brush19)
        palette2.setBrush(QPalette.Active, QPalette.Button, brush1)
        palette2.setBrush(QPalette.Active, QPalette.Text, brush19)
        palette2.setBrush(QPalette.Active, QPalette.ButtonText, brush19)
        palette2.setBrush(QPalette.Active, QPalette.Base, brush1)
        palette2.setBrush(QPalette.Active, QPalette.Window, brush1)
        brush20 = QBrush(QColor(147, 0, 0, 128))
        brush20.setStyle(Qt.NoBrush)
#if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette2.setBrush(QPalette.Active, QPalette.PlaceholderText, brush20)
#endif
        palette2.setBrush(QPalette.Inactive, QPalette.WindowText, brush19)
        palette2.setBrush(QPalette.Inactive, QPalette.Button, brush1)
        palette2.setBrush(QPalette.Inactive, QPalette.Text, brush19)
        palette2.setBrush(QPalette.Inactive, QPalette.ButtonText, brush19)
        palette2.setBrush(QPalette.Inactive, QPalette.Base, brush1)
        palette2.setBrush(QPalette.Inactive, QPalette.Window, brush1)
        brush21 = QBrush(QColor(147, 0, 0, 128))
        brush21.setStyle(Qt.NoBrush)
#if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette2.setBrush(QPalette.Inactive, QPalette.PlaceholderText, brush21)
#endif
        palette2.setBrush(QPalette.Disabled, QPalette.WindowText, brush19)
        palette2.setBrush(QPalette.Disabled, QPalette.Button, brush1)
        palette2.setBrush(QPalette.Disabled, QPalette.Text, brush19)
        palette2.setBrush(QPalette.Disabled, QPalette.ButtonText, brush19)
        palette2.setBrush(QPalette.Disabled, QPalette.Base, brush1)
        palette2.setBrush(QPalette.Disabled, QPalette.Window, brush1)
        brush22 = QBrush(QColor(147, 0, 0, 128))
        brush22.setStyle(Qt.NoBrush)
#if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette2.setBrush(QPalette.Disabled, QPalette.PlaceholderText, brush22)
#endif
        self.tableLabelError.setPalette(palette2)
        self.tableLabelError.setFont(font10)
        self.tableLabelError.setStyleSheet(u"color:#930000;")
        self.tableLabelError.setAlignment(Qt.AlignCenter)

        self.verticalLayout_19.addWidget(self.tableLabelError)

        self.verticalLayout_19.setStretch(0, 1)

        self.verticalLayout_20.addWidget(self.frame_6)

        self.frame_4 = QFrame(self.page_table)
        self.frame_4.setObjectName(u"frame_4")
        self.frame_4.setMinimumSize(QSize(0, 150))
        self.frame_4.setFrameShape(QFrame.StyledPanel)
        self.frame_4.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_13 = QHBoxLayout(self.frame_4)
        self.horizontalLayout_13.setSpacing(0)
        self.horizontalLayout_13.setObjectName(u"horizontalLayout_13")
        self.horizontalLayout_13.setContentsMargins(0, 0, 0, 0)
        self.resultsTableWidget = QTableWidget(self.frame_4)
        if (self.resultsTableWidget.columnCount() < 8):
            self.resultsTableWidget.setColumnCount(8)
        __qtablewidgetitem = QTableWidgetItem()
        self.resultsTableWidget.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.resultsTableWidget.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        __qtablewidgetitem2 = QTableWidgetItem()
        self.resultsTableWidget.setHorizontalHeaderItem(2, __qtablewidgetitem2)
        __qtablewidgetitem3 = QTableWidgetItem()
        self.resultsTableWidget.setHorizontalHeaderItem(3, __qtablewidgetitem3)
        __qtablewidgetitem4 = QTableWidgetItem()
        self.resultsTableWidget.setHorizontalHeaderItem(4, __qtablewidgetitem4)
        __qtablewidgetitem5 = QTableWidgetItem()
        self.resultsTableWidget.setHorizontalHeaderItem(5, __qtablewidgetitem5)
        __qtablewidgetitem6 = QTableWidgetItem()
        self.resultsTableWidget.setHorizontalHeaderItem(6, __qtablewidgetitem6)
        __qtablewidgetitem7 = QTableWidgetItem()
        self.resultsTableWidget.setHorizontalHeaderItem(7, __qtablewidgetitem7)
        if (self.resultsTableWidget.rowCount() < 16):
            self.resultsTableWidget.setRowCount(16)
        __qtablewidgetitem8 = QTableWidgetItem()
        __qtablewidgetitem8.setFont(font2);
        self.resultsTableWidget.setVerticalHeaderItem(0, __qtablewidgetitem8)
        __qtablewidgetitem9 = QTableWidgetItem()
        self.resultsTableWidget.setVerticalHeaderItem(1, __qtablewidgetitem9)
        __qtablewidgetitem10 = QTableWidgetItem()
        self.resultsTableWidget.setVerticalHeaderItem(2, __qtablewidgetitem10)
        __qtablewidgetitem11 = QTableWidgetItem()
        self.resultsTableWidget.setVerticalHeaderItem(3, __qtablewidgetitem11)
        __qtablewidgetitem12 = QTableWidgetItem()
        self.resultsTableWidget.setVerticalHeaderItem(4, __qtablewidgetitem12)
        __qtablewidgetitem13 = QTableWidgetItem()
        self.resultsTableWidget.setVerticalHeaderItem(5, __qtablewidgetitem13)
        __qtablewidgetitem14 = QTableWidgetItem()
        self.resultsTableWidget.setVerticalHeaderItem(6, __qtablewidgetitem14)
        __qtablewidgetitem15 = QTableWidgetItem()
        self.resultsTableWidget.setVerticalHeaderItem(7, __qtablewidgetitem15)
        __qtablewidgetitem16 = QTableWidgetItem()
        self.resultsTableWidget.setVerticalHeaderItem(8, __qtablewidgetitem16)
        __qtablewidgetitem17 = QTableWidgetItem()
        self.resultsTableWidget.setVerticalHeaderItem(9, __qtablewidgetitem17)
        __qtablewidgetitem18 = QTableWidgetItem()
        self.resultsTableWidget.setVerticalHeaderItem(10, __qtablewidgetitem18)
        __qtablewidgetitem19 = QTableWidgetItem()
        self.resultsTableWidget.setVerticalHeaderItem(11, __qtablewidgetitem19)
        __qtablewidgetitem20 = QTableWidgetItem()
        self.resultsTableWidget.setVerticalHeaderItem(12, __qtablewidgetitem20)
        __qtablewidgetitem21 = QTableWidgetItem()
        self.resultsTableWidget.setVerticalHeaderItem(13, __qtablewidgetitem21)
        __qtablewidgetitem22 = QTableWidgetItem()
        self.resultsTableWidget.setVerticalHeaderItem(14, __qtablewidgetitem22)
        __qtablewidgetitem23 = QTableWidgetItem()
        self.resultsTableWidget.setVerticalHeaderItem(15, __qtablewidgetitem23)
        __qtablewidgetitem24 = QTableWidgetItem()
        self.resultsTableWidget.setItem(0, 0, __qtablewidgetitem24)
        __qtablewidgetitem25 = QTableWidgetItem()
        self.resultsTableWidget.setItem(0, 1, __qtablewidgetitem25)
        __qtablewidgetitem26 = QTableWidgetItem()
        self.resultsTableWidget.setItem(0, 2, __qtablewidgetitem26)
        __qtablewidgetitem27 = QTableWidgetItem()
        self.resultsTableWidget.setItem(0, 3, __qtablewidgetitem27)
        __qtablewidgetitem28 = QTableWidgetItem()
        self.resultsTableWidget.setItem(0, 4, __qtablewidgetitem28)
        __qtablewidgetitem29 = QTableWidgetItem()
        self.resultsTableWidget.setItem(0, 5, __qtablewidgetitem29)
        __qtablewidgetitem30 = QTableWidgetItem()
        self.resultsTableWidget.setItem(0, 6, __qtablewidgetitem30)
        __qtablewidgetitem31 = QTableWidgetItem()
        self.resultsTableWidget.setItem(0, 7, __qtablewidgetitem31)
        self.resultsTableWidget.setObjectName(u"resultsTableWidget")
        sizePolicy.setHeightForWidth(self.resultsTableWidget.sizePolicy().hasHeightForWidth())
        self.resultsTableWidget.setSizePolicy(sizePolicy)
        palette3 = QPalette()
        palette3.setBrush(QPalette.Active, QPalette.WindowText, brush6)
        brush23 = QBrush(QColor(39, 44, 54, 255))
        brush23.setStyle(Qt.SolidPattern)
        palette3.setBrush(QPalette.Active, QPalette.Button, brush23)
        palette3.setBrush(QPalette.Active, QPalette.Text, brush6)
        palette3.setBrush(QPalette.Active, QPalette.ButtonText, brush6)
        palette3.setBrush(QPalette.Active, QPalette.Base, brush23)
        palette3.setBrush(QPalette.Active, QPalette.Window, brush23)
        brush24 = QBrush(QColor(210, 210, 210, 128))
        brush24.setStyle(Qt.NoBrush)
#if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette3.setBrush(QPalette.Active, QPalette.PlaceholderText, brush24)
#endif
        palette3.setBrush(QPalette.Inactive, QPalette.WindowText, brush6)
        palette3.setBrush(QPalette.Inactive, QPalette.Button, brush23)
        palette3.setBrush(QPalette.Inactive, QPalette.Text, brush6)
        palette3.setBrush(QPalette.Inactive, QPalette.ButtonText, brush6)
        palette3.setBrush(QPalette.Inactive, QPalette.Base, brush23)
        palette3.setBrush(QPalette.Inactive, QPalette.Window, brush23)
        brush25 = QBrush(QColor(210, 210, 210, 128))
        brush25.setStyle(Qt.NoBrush)
#if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette3.setBrush(QPalette.Inactive, QPalette.PlaceholderText, brush25)
#endif
        palette3.setBrush(QPalette.Disabled, QPalette.WindowText, brush6)
        palette3.setBrush(QPalette.Disabled, QPalette.Button, brush23)
        palette3.setBrush(QPalette.Disabled, QPalette.Text, brush6)
        palette3.setBrush(QPalette.Disabled, QPalette.ButtonText, brush6)
        palette3.setBrush(QPalette.Disabled, QPalette.Base, brush23)
        palette3.setBrush(QPalette.Disabled, QPalette.Window, brush23)
        brush26 = QBrush(QColor(210, 210, 210, 128))
        brush26.setStyle(Qt.NoBrush)
#if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette3.setBrush(QPalette.Disabled, QPalette.PlaceholderText, brush26)
#endif
        self.resultsTableWidget.setPalette(palette3)
        self.resultsTableWidget.setStyleSheet(u"QTableWidget {	\n"
"	background-color: rgb(39, 44, 54);\n"
"	padding: 10px;\n"
"	border-radius: 5px;\n"
"	gridline-color: rgb(44, 49, 60);\n"
"	border-bottom: 1px solid rgb(44, 49, 60);\n"
"}\n"
"QTableWidget::item{\n"
"	border-color: rgb(44, 49, 60);\n"
"	padding-left: 5px;\n"
"	padding-right: 5px;\n"
"	gridline-color: rgb(44, 49, 60);\n"
"}\n"
"QTableWidget::item:selected{\n"
"	background-color: rgb(85, 170, 255);\n"
"}\n"
"QScrollBar:horizontal {\n"
"    border: none;\n"
"    background: rgb(52, 59, 72);\n"
"    height: 14px;\n"
"    margin: 0px 21px 0 21px;\n"
"	border-radius: 0px;\n"
"}\n"
" QScrollBar:vertical {\n"
"	border: none;\n"
"    background: rgb(52, 59, 72);\n"
"    width: 14px;\n"
"    margin: 21px 0 21px 0;\n"
"	border-radius: 0px;\n"
" }\n"
"QHeaderView::section{\n"
"	Background-color: rgb(39, 44, 54);\n"
"	max-width: 30px;\n"
"	border: 1px solid rgb(44, 49, 60);\n"
"	border-style: none;\n"
"    border-bottom: 1px solid rgb(44, 49, 60);\n"
"    border-right: 1px solid rgb(44, 49, 60);\n"
"}\n"
""
                        "QTableWidget::horizontalHeader {	\n"
"	background-color: rgb(81, 255, 0);\n"
"}\n"
"QHeaderView::section:horizontal\n"
"{\n"
"    border: 1px solid rgb(32, 34, 42);\n"
"	background-color: rgb(27, 29, 35);\n"
"	padding: 3px;\n"
"	border-top-left-radius: 7px;\n"
"    border-top-right-radius: 7px;\n"
"}\n"
"QHeaderView::section:vertical\n"
"{\n"
"    border: 1px solid rgb(44, 49, 60);\n"
"}\n"
"")
        self.resultsTableWidget.setFrameShape(QFrame.NoFrame)
        self.resultsTableWidget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.resultsTableWidget.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.resultsTableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.resultsTableWidget.setAlternatingRowColors(False)
        self.resultsTableWidget.setSelectionMode(QAbstractItemView.SingleSelection)
        self.resultsTableWidget.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.resultsTableWidget.setShowGrid(True)
        self.resultsTableWidget.setGridStyle(Qt.SolidLine)
        self.resultsTableWidget.setSortingEnabled(False)
        self.resultsTableWidget.horizontalHeader().setVisible(False)
        self.resultsTableWidget.horizontalHeader().setCascadingSectionResizes(True)
        self.resultsTableWidget.horizontalHeader().setDefaultSectionSize(200)
        self.resultsTableWidget.horizontalHeader().setStretchLastSection(True)
        self.resultsTableWidget.verticalHeader().setVisible(False)
        self.resultsTableWidget.verticalHeader().setCascadingSectionResizes(False)
        self.resultsTableWidget.verticalHeader().setHighlightSections(False)
        self.resultsTableWidget.verticalHeader().setStretchLastSection(True)

        self.horizontalLayout_13.addWidget(self.resultsTableWidget)


        self.verticalLayout_20.addWidget(self.frame_4)

        self.stackedWidget.addWidget(self.page_table)
        self.page_widgets = QWidget()
        self.page_widgets.setObjectName(u"page_widgets")
        self.verticalLayout_6 = QVBoxLayout(self.page_widgets)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.frame = QFrame(self.page_widgets)
        self.frame.setObjectName(u"frame")
        self.frame.setStyleSheet(u"border-radius: 5px;")
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Raised)
        self.verticalLayout_32 = QVBoxLayout(self.frame)
        self.verticalLayout_32.setObjectName(u"verticalLayout_32")
        self.frame_2 = QFrame(self.frame)
        self.frame_2.setObjectName(u"frame_2")
        self.frame_2.setStyleSheet(u"border-radius: 5px;")
        self.frame_2.setFrameShape(QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QFrame.Raised)
        self.verticalLayout_15 = QVBoxLayout(self.frame_2)
        self.verticalLayout_15.setSpacing(0)
        self.verticalLayout_15.setObjectName(u"verticalLayout_15")
        self.verticalLayout_15.setContentsMargins(0, 0, 0, 0)
        self.frame_div_content_9 = QFrame(self.frame_2)
        self.frame_div_content_9.setObjectName(u"frame_div_content_9")
        self.frame_div_content_9.setMinimumSize(QSize(0, 110))
        self.frame_div_content_9.setMaximumSize(QSize(16777215, 16777215))
        self.frame_div_content_9.setStyleSheet(u"background-color: rgb(41, 45, 56);\n"
"border-radius: 5px;\n"
"")
        self.frame_div_content_9.setFrameShape(QFrame.NoFrame)
        self.frame_div_content_9.setFrameShadow(QFrame.Raised)
        self.verticalLayout_11 = QVBoxLayout(self.frame_div_content_9)
        self.verticalLayout_11.setSpacing(0)
        self.verticalLayout_11.setObjectName(u"verticalLayout_11")
        self.verticalLayout_11.setContentsMargins(0, 0, 0, 0)
        self.frame_title_wid_2 = QFrame(self.frame_div_content_9)
        self.frame_title_wid_2.setObjectName(u"frame_title_wid_2")
        self.frame_title_wid_2.setMaximumSize(QSize(16777215, 35))
        self.frame_title_wid_2.setStyleSheet(u"background-color: rgb(39, 44, 54);")
        self.frame_title_wid_2.setFrameShape(QFrame.StyledPanel)
        self.frame_title_wid_2.setFrameShadow(QFrame.Raised)
        self.verticalLayout_21 = QVBoxLayout(self.frame_title_wid_2)
        self.verticalLayout_21.setObjectName(u"verticalLayout_21")
        self.labelBoxBlenderInstalation_2 = QLabel(self.frame_title_wid_2)
        self.labelBoxBlenderInstalation_2.setObjectName(u"labelBoxBlenderInstalation_2")
        self.labelBoxBlenderInstalation_2.setFont(font1)
        self.labelBoxBlenderInstalation_2.setStyleSheet(u"")

        self.verticalLayout_21.addWidget(self.labelBoxBlenderInstalation_2)


        self.verticalLayout_11.addWidget(self.frame_title_wid_2)

        self.frame_content_wid_2 = QFrame(self.frame_div_content_9)
        self.frame_content_wid_2.setObjectName(u"frame_content_wid_2")
        self.frame_content_wid_2.setFrameShape(QFrame.NoFrame)
        self.frame_content_wid_2.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_11 = QHBoxLayout(self.frame_content_wid_2)
        self.horizontalLayout_11.setObjectName(u"horizontalLayout_11")
        self.label_9 = QLabel(self.frame_content_wid_2)
        self.label_9.setObjectName(u"label_9")
        font11 = QFont()
        font11.setFamily(u"Sans Serif")
        font11.setPointSize(8)
        self.label_9.setFont(font11)
        self.label_9.setTextFormat(Qt.AutoText)
        self.label_9.setScaledContents(False)
        self.label_9.setWordWrap(True)

        self.horizontalLayout_11.addWidget(self.label_9)


        self.verticalLayout_11.addWidget(self.frame_content_wid_2)


        self.verticalLayout_15.addWidget(self.frame_div_content_9)


        self.verticalLayout_32.addWidget(self.frame_2)

        self.frame_3 = QFrame(self.frame)
        self.frame_3.setObjectName(u"frame_3")
        self.frame_3.setStyleSheet(u"border-radius: 5px;")
        self.frame_3.setFrameShape(QFrame.StyledPanel)
        self.frame_3.setFrameShadow(QFrame.Raised)
        self.verticalLayout_28 = QVBoxLayout(self.frame_3)
        self.verticalLayout_28.setSpacing(0)
        self.verticalLayout_28.setObjectName(u"verticalLayout_28")
        self.verticalLayout_28.setContentsMargins(0, 0, 0, 0)
        self.frame_div_content_12 = QFrame(self.frame_3)
        self.frame_div_content_12.setObjectName(u"frame_div_content_12")
        self.frame_div_content_12.setMinimumSize(QSize(0, 110))
        self.frame_div_content_12.setMaximumSize(QSize(16777215, 16777215))
        self.frame_div_content_12.setStyleSheet(u"background-color: rgb(41, 45, 56);\n"
"border-radius: 5px;\n"
"")
        self.frame_div_content_12.setFrameShape(QFrame.NoFrame)
        self.frame_div_content_12.setFrameShadow(QFrame.Raised)
        self.verticalLayout_29 = QVBoxLayout(self.frame_div_content_12)
        self.verticalLayout_29.setSpacing(0)
        self.verticalLayout_29.setObjectName(u"verticalLayout_29")
        self.verticalLayout_29.setContentsMargins(0, 0, 0, 0)
        self.frame_title_wid_5 = QFrame(self.frame_div_content_12)
        self.frame_title_wid_5.setObjectName(u"frame_title_wid_5")
        self.frame_title_wid_5.setMaximumSize(QSize(16777215, 35))
        self.frame_title_wid_5.setStyleSheet(u"background-color: rgb(39, 44, 54);")
        self.frame_title_wid_5.setFrameShape(QFrame.StyledPanel)
        self.frame_title_wid_5.setFrameShadow(QFrame.Raised)
        self.verticalLayout_30 = QVBoxLayout(self.frame_title_wid_5)
        self.verticalLayout_30.setObjectName(u"verticalLayout_30")
        self.labelBoxBlenderInstalation_5 = QLabel(self.frame_title_wid_5)
        self.labelBoxBlenderInstalation_5.setObjectName(u"labelBoxBlenderInstalation_5")
        self.labelBoxBlenderInstalation_5.setFont(font1)
        self.labelBoxBlenderInstalation_5.setStyleSheet(u"")

        self.verticalLayout_30.addWidget(self.labelBoxBlenderInstalation_5)


        self.verticalLayout_29.addWidget(self.frame_title_wid_5)

        self.frame_content_wid_5 = QFrame(self.frame_div_content_12)
        self.frame_content_wid_5.setObjectName(u"frame_content_wid_5")
        self.frame_content_wid_5.setFrameShape(QFrame.NoFrame)
        self.frame_content_wid_5.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_15 = QHBoxLayout(self.frame_content_wid_5)
        self.horizontalLayout_15.setObjectName(u"horizontalLayout_15")
        self.label_12 = QLabel(self.frame_content_wid_5)
        self.label_12.setObjectName(u"label_12")
        font12 = QFont()
        font12.setFamily(u"Segoe UI")
        font12.setPointSize(8)
        self.label_12.setFont(font12)
        self.label_12.setTextFormat(Qt.AutoText)
        self.label_12.setScaledContents(False)
        self.label_12.setWordWrap(True)

        self.horizontalLayout_15.addWidget(self.label_12)


        self.verticalLayout_29.addWidget(self.frame_content_wid_5)


        self.verticalLayout_28.addWidget(self.frame_div_content_12)


        self.verticalLayout_32.addWidget(self.frame_3)


        self.verticalLayout_6.addWidget(self.frame)

        self.stackedWidget.addWidget(self.page_widgets)

        self.verticalLayout_9.addWidget(self.stackedWidget)


        self.verticalLayout_4.addWidget(self.frame_content)

        self.frame_grip = QFrame(self.frame_content_right)
        self.frame_grip.setObjectName(u"frame_grip")
        self.frame_grip.setMinimumSize(QSize(0, 25))
        self.frame_grip.setMaximumSize(QSize(16777215, 25))
        self.frame_grip.setStyleSheet(u"background-color: rgb(33, 37, 43);")
        self.frame_grip.setFrameShape(QFrame.NoFrame)
        self.frame_grip.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_6 = QHBoxLayout(self.frame_grip)
        self.horizontalLayout_6.setSpacing(0)
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.horizontalLayout_6.setContentsMargins(0, 0, 2, 0)
        self.frame_label_bottom = QFrame(self.frame_grip)
        self.frame_label_bottom.setObjectName(u"frame_label_bottom")
        self.frame_label_bottom.setFrameShape(QFrame.NoFrame)
        self.frame_label_bottom.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_7 = QHBoxLayout(self.frame_label_bottom)
        self.horizontalLayout_7.setSpacing(0)
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.horizontalLayout_7.setContentsMargins(10, 0, 10, 0)
        self.label_credits = QLabel(self.frame_label_bottom)
        self.label_credits.setObjectName(u"label_credits")
        self.label_credits.setFont(font2)
        self.label_credits.setStyleSheet(u"color: rgb(98, 103, 111);")

        self.horizontalLayout_7.addWidget(self.label_credits)

        self.label_version = QLabel(self.frame_label_bottom)
        self.label_version.setObjectName(u"label_version")
        self.label_version.setMaximumSize(QSize(100, 16777215))
        self.label_version.setFont(font2)
        self.label_version.setStyleSheet(u"color: rgb(98, 103, 111);")
        self.label_version.setAlignment(Qt.AlignCenter)

        self.horizontalLayout_7.addWidget(self.label_version)


        self.horizontalLayout_6.addWidget(self.frame_label_bottom)

        self.frame_size_grip = QFrame(self.frame_grip)
        self.frame_size_grip.setObjectName(u"frame_size_grip")
        self.frame_size_grip.setMaximumSize(QSize(20, 20))
        self.frame_size_grip.setStyleSheet(u"QSizeGrip {\n"
"	background-image: url(:/16x16/icons/16x16/cil-size-grip.png);\n"
"	background-position: center;\n"
"	background-repeat: no-reperat;\n"
"}")
        self.frame_size_grip.setFrameShape(QFrame.NoFrame)
        self.frame_size_grip.setFrameShadow(QFrame.Raised)

        self.horizontalLayout_6.addWidget(self.frame_size_grip)


        self.verticalLayout_4.addWidget(self.frame_grip)


        self.horizontalLayout_2.addWidget(self.frame_content_right)


        self.verticalLayout.addWidget(self.frame_center)


        self.horizontalLayout.addWidget(self.frame_main)

        MainWindow.setCentralWidget(self.centralwidget)
        QWidget.setTabOrder(self.btn_minimize, self.btn_maximize_restore)
        QWidget.setTabOrder(self.btn_maximize_restore, self.btn_close)
        QWidget.setTabOrder(self.btn_close, self.btn_toggle_menu)

        self.retranslateUi(MainWindow)

        self.stackedWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.btn_toggle_menu.setText("")
        self.label_title_bar_top.setText(QCoreApplication.translate("MainWindow", u"Main Window", None))
#if QT_CONFIG(tooltip)
        self.btn_minimize.setToolTip(QCoreApplication.translate("MainWindow", u"Minimize", None))
#endif // QT_CONFIG(tooltip)
        self.btn_minimize.setText("")
#if QT_CONFIG(tooltip)
        self.btn_maximize_restore.setToolTip(QCoreApplication.translate("MainWindow", u"Maximize", None))
#endif // QT_CONFIG(tooltip)
        self.btn_maximize_restore.setText("")
#if QT_CONFIG(tooltip)
        self.btn_close.setToolTip(QCoreApplication.translate("MainWindow", u"Close", None))
#endif // QT_CONFIG(tooltip)
        self.btn_close.setText("")
        self.label_top_info_1.setText(QCoreApplication.translate("MainWindow", u"C:\\Program Files\\Blender Foundation\\Blender 2.82", None))
        self.label_top_info_2.setText(QCoreApplication.translate("MainWindow", u"| HOME", None))
        self.label_user_icon.setText("")
        self.label_6.setText(QCoreApplication.translate("MainWindow", u"WELCOME TO CONFINDR", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>This program is designed to find bacterial intra-species </p><p>contamination in raw Illumina data. It does this by looking </p><p>for multiple alleles of core, single copy genes.</p><p>Confindr must be installed for this app to work</p></body></html>", None))
        self.label_7.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>For complete instructions on installation,</p><p>please visit: https://olc-bioinformatics.github.io/ConFindr/</p></body></html>", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"ANALYZATION STATION", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"Please select your folder of sequences you would like to analyze", None))
        self.sequenceBtn.setText(QCoreApplication.translate("MainWindow", u"Open Sequence Files", None))
        self.analyzeLabelError.setText("")
        self.baseCutoffInput.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Base Cutoff", None))
        self.FASTAcheckBox.setText(QCoreApplication.translate("MainWindow", u"FASTA", None))
        self.dataDropdownMenu.setItemText(0, QCoreApplication.translate("MainWindow", u"Illumina", None))
        self.dataDropdownMenu.setItemText(1, QCoreApplication.translate("MainWindow", u"Nanopore", None))

        self.labelBoxMainArguements.setText(QCoreApplication.translate("MainWindow", u"MAIN ARGUEMENTS", None))
        self.RMLSTcheckBox.setText(QCoreApplication.translate("MainWindow", u"RMLST", None))
        self.verbosityDropdownMenu.setItemText(0, QCoreApplication.translate("MainWindow", u"Info", None))
        self.verbosityDropdownMenu.setItemText(1, QCoreApplication.translate("MainWindow", u"Debug", None))
        self.verbosityDropdownMenu.setItemText(2, QCoreApplication.translate("MainWindow", u"Warning", None))

        self.keepCheckBox.setText(QCoreApplication.translate("MainWindow", u"Keep Files", None))
        self.versionCheckBox.setText(QCoreApplication.translate("MainWindow", u"Version Display", None))
        self.crossDetailsCheckBox.setText(QCoreApplication.translate("MainWindow", u"Cross Details", None))
        self.threadsInput.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Threads", None))
        self.reverseInput.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Reverse ID", None))
        self.MMHInput.setPlaceholderText(QCoreApplication.translate("MainWindow", u"MMH", None))
        self.baseFractionInput.setPlaceholderText(QCoreApplication.translate("MainWindow", u"BFC", None))
        self.forwardInput.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Forward ID", None))
        self.TMPInput.setPlaceholderText(QCoreApplication.translate("MainWindow", u"TMP", None))
        self.qualityInput.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Quality Cutoff", None))
        self.databaseInput.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Databases", None))
        self.cgmlstInput.setPlaceholderText(QCoreApplication.translate("MainWindow", u"CGMLST", None))
        self.labelBoxAdvancedArguements.setText(QCoreApplication.translate("MainWindow", u"ADVANCED ARGUEMENTS", None))
        self.label_5.setText(QCoreApplication.translate("MainWindow", u"TABLE RESULTS", None))
        self.label_8.setText(QCoreApplication.translate("MainWindow", u"Results appear in the table below once you've selected a .csv or .xlsx file", None))
        self.resultsBtn.setText(QCoreApplication.translate("MainWindow", u"Open Table", None))
        self.tableLabelError.setText("")
        ___qtablewidgetitem = self.resultsTableWidget.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("MainWindow", u"0", None));
        ___qtablewidgetitem1 = self.resultsTableWidget.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("MainWindow", u"1", None));
        ___qtablewidgetitem2 = self.resultsTableWidget.horizontalHeaderItem(2)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("MainWindow", u"2", None));
        ___qtablewidgetitem3 = self.resultsTableWidget.horizontalHeaderItem(3)
        ___qtablewidgetitem3.setText(QCoreApplication.translate("MainWindow", u"3", None));
        ___qtablewidgetitem4 = self.resultsTableWidget.horizontalHeaderItem(5)
        ___qtablewidgetitem4.setText(QCoreApplication.translate("MainWindow", u"4", None));
        ___qtablewidgetitem5 = self.resultsTableWidget.horizontalHeaderItem(6)
        ___qtablewidgetitem5.setText(QCoreApplication.translate("MainWindow", u"5", None));
        ___qtablewidgetitem6 = self.resultsTableWidget.horizontalHeaderItem(7)
        ___qtablewidgetitem6.setText(QCoreApplication.translate("MainWindow", u"7", None));
        ___qtablewidgetitem7 = self.resultsTableWidget.verticalHeaderItem(0)
        ___qtablewidgetitem7.setText(QCoreApplication.translate("MainWindow", u"New Row", None));
        ___qtablewidgetitem8 = self.resultsTableWidget.verticalHeaderItem(1)
        ___qtablewidgetitem8.setText(QCoreApplication.translate("MainWindow", u"New Row", None));
        ___qtablewidgetitem9 = self.resultsTableWidget.verticalHeaderItem(2)
        ___qtablewidgetitem9.setText(QCoreApplication.translate("MainWindow", u"New Row", None));
        ___qtablewidgetitem10 = self.resultsTableWidget.verticalHeaderItem(3)
        ___qtablewidgetitem10.setText(QCoreApplication.translate("MainWindow", u"New Row", None));
        ___qtablewidgetitem11 = self.resultsTableWidget.verticalHeaderItem(4)
        ___qtablewidgetitem11.setText(QCoreApplication.translate("MainWindow", u"New Row", None));
        ___qtablewidgetitem12 = self.resultsTableWidget.verticalHeaderItem(5)
        ___qtablewidgetitem12.setText(QCoreApplication.translate("MainWindow", u"New Row", None));
        ___qtablewidgetitem13 = self.resultsTableWidget.verticalHeaderItem(6)
        ___qtablewidgetitem13.setText(QCoreApplication.translate("MainWindow", u"New Row", None));
        ___qtablewidgetitem14 = self.resultsTableWidget.verticalHeaderItem(7)
        ___qtablewidgetitem14.setText(QCoreApplication.translate("MainWindow", u"New Row", None));
        ___qtablewidgetitem15 = self.resultsTableWidget.verticalHeaderItem(8)
        ___qtablewidgetitem15.setText(QCoreApplication.translate("MainWindow", u"New Row", None));
        ___qtablewidgetitem16 = self.resultsTableWidget.verticalHeaderItem(9)
        ___qtablewidgetitem16.setText(QCoreApplication.translate("MainWindow", u"New Row", None));
        ___qtablewidgetitem17 = self.resultsTableWidget.verticalHeaderItem(10)
        ___qtablewidgetitem17.setText(QCoreApplication.translate("MainWindow", u"New Row", None));
        ___qtablewidgetitem18 = self.resultsTableWidget.verticalHeaderItem(11)
        ___qtablewidgetitem18.setText(QCoreApplication.translate("MainWindow", u"New Row", None));
        ___qtablewidgetitem19 = self.resultsTableWidget.verticalHeaderItem(12)
        ___qtablewidgetitem19.setText(QCoreApplication.translate("MainWindow", u"New Row", None));
        ___qtablewidgetitem20 = self.resultsTableWidget.verticalHeaderItem(13)
        ___qtablewidgetitem20.setText(QCoreApplication.translate("MainWindow", u"New Row", None));
        ___qtablewidgetitem21 = self.resultsTableWidget.verticalHeaderItem(14)
        ___qtablewidgetitem21.setText(QCoreApplication.translate("MainWindow", u"New Row", None));
        ___qtablewidgetitem22 = self.resultsTableWidget.verticalHeaderItem(15)
        ___qtablewidgetitem22.setText(QCoreApplication.translate("MainWindow", u"New Row", None));

        __sortingEnabled = self.resultsTableWidget.isSortingEnabled()
        self.resultsTableWidget.setSortingEnabled(False)
        ___qtablewidgetitem23 = self.resultsTableWidget.item(0, 0)
        ___qtablewidgetitem23.setText(QCoreApplication.translate("MainWindow", u"Sample", None));
        ___qtablewidgetitem24 = self.resultsTableWidget.item(0, 1)
        ___qtablewidgetitem24.setText(QCoreApplication.translate("MainWindow", u"Genus", None));
        ___qtablewidgetitem25 = self.resultsTableWidget.item(0, 2)
        ___qtablewidgetitem25.setText(QCoreApplication.translate("MainWindow", u"NumContamSNVs", None));
        ___qtablewidgetitem26 = self.resultsTableWidget.item(0, 3)
        ___qtablewidgetitem26.setText(QCoreApplication.translate("MainWindow", u"ContamStatus", None));
        ___qtablewidgetitem27 = self.resultsTableWidget.item(0, 4)
        ___qtablewidgetitem27.setText(QCoreApplication.translate("MainWindow", u"PercentContam", None));
        ___qtablewidgetitem28 = self.resultsTableWidget.item(0, 5)
        ___qtablewidgetitem28.setText(QCoreApplication.translate("MainWindow", u"PercentContamStandardDeviation", None));
        ___qtablewidgetitem29 = self.resultsTableWidget.item(0, 6)
        ___qtablewidgetitem29.setText(QCoreApplication.translate("MainWindow", u"BasesExamined", None));
        ___qtablewidgetitem30 = self.resultsTableWidget.item(0, 7)
        ___qtablewidgetitem30.setText(QCoreApplication.translate("MainWindow", u"DatabaseDownloadDate", None));
        self.resultsTableWidget.setSortingEnabled(__sortingEnabled)

        self.labelBoxBlenderInstalation_2.setText(QCoreApplication.translate("MainWindow", u"How Does ConFindr Work?", None))
        self.label_9.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>ConFindr is a pipeline that can detect contamination in bacterial NGS data, both between and within species. It can do this with pretty darn good sensitivity - two samples mixed together with as few as 500 SNPs between them (&gt; 99.9 percent identity!) can be identified. This allows for stringent quality control of NGS samples.</p><p>ConFindr works by looking at conserved core genes - either using rMLST genes (53 genes are known to be single copy and conserved across all bacteria with some known exceptions, which ConFindr handles), or custom sets of genes derived from core-genome schemes. As the genes ConFindr looks at are single copy, any sample that has multiple alleles of one or more gene is likely to be contaminated. To identify the presence of multiple alleles in a sample, the following workflow is followed:</p><p>1. Use Mash to determine the genus of each sample so that genus-specific databases can be constructed and check for interspecies contamination.</p><p>2. Perform stringent "
                        "quality trimming and bait out reads that contain rMLST gene sequence, using BBDuk.</p><p>3. Align reads back to the rMLST genes.</p><p>4. Look at the alignment to find Contaminating SNVs - those that have sites where more than one base is present, indicating that multiple alleles are present, indicating contamination.</p></body></html>", None))
        self.labelBoxBlenderInstalation_5.setText(QCoreApplication.translate("MainWindow", u"Limits of Detection", None))
        self.label_12.setText(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:'Segoe UI'; font-size:8pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">The limit of detection for ConFindr is going to be a function of several factors, so it's hard to give exact information on what can and can't be detected. However, here are a few guidelines:</p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">- Two strains with identical rMLST genes won't ever have contamination detected between them.</p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">- ConFindr has a cuto"
                        "ff of finding 3 Contaminating SNVs found for calling a sample as contaminated, as there will occasionally be 1 false positive, and very rarely 2 false positive sites. In practice, this still lets you detect contamination essentially whenever two strains have different rMLST types, as &gt;99 percent of types have at least 3 SNPs between them in E. coli, S. enterica, and L. monocytogenes. I haven't looked at other species in detail, but this very likely holds true for them too.</p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">- The degree of contamination matters: things with very low levels of contamination (around 1 percent) probably won't ever be picked up under default parameters. Once you hit 5 percent contamination, whether or not it gets detected is a function of sequencing depth and distance between species.</p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-"
                        "indent:0px;\">- Sequencing depth matters: Contaminating SNVs are found more reliably the more depth you have. ConFindr seems to work pretty well once you hit 40X or 50X, but trying to run it on a sample with only 10X coverage is unlikely to ever find anything (unless default parameters get changed)</p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">- Relatedness of the contaminant strain is the the final major factor - with something very closely related to the strain you actually want, picking up contamination at 5 percent will be pretty difficult.</p></body></html>", None))
        self.label_credits.setText(QCoreApplication.translate("MainWindow", u"Developed for OLC Bioinformaticians", None))
        self.label_version.setText(QCoreApplication.translate("MainWindow", u"v0.8.1", None))
    # retranslateUi


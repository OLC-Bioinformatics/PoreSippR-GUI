#!/usr/env/python 3

"""
A placeholder script for the PoreSippr. This script clears out any images in the current working directory, and
periodically copies a mock-up image into the current working directory. This gives comparable functionality to what I
imagine the final PoreSippr will have
"""

from glob import glob
import os
import shutil
from time import sleep
from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtCore import (QCoreApplication, QPropertyAnimation, QDate, QDateTime, QMetaObject, QObject, QPoint, QRect, QSize, QTime, QUrl, Qt, QEvent)
from PySide2.QtGui import (QBrush, QColor, QConicalGradient, QCursor, QFont, QFontDatabase, QIcon, QKeySequence, QLinearGradient, QPalette, QPainter, QPixmap, QRadialGradient)


class HoldPlace():

    def main(self):
        """
        Run the appropriate methods in the correct order
        """

        HoldPlace.clear_folder(
            working_dir=self.current_working_dir
        )
        complete = False
        while not complete:
            self.image_list, complete = HoldPlace.locate_image(
                image_dir=self.image_dir,
                image_list=self.image_list,
                complete=complete
            )
            HoldPlace.copy_image(
                working_dir=self.current_working_dir,
                image=self.image_list[-1]
            )
            # Sleep for 15 seconds
            sleep(3)

    @staticmethod
    def clear_folder(working_dir, extension='.png'):
        """
        Delete any image files from a previous iteration of the script
        :param working_dir: Name and absolute path of current working directory
        :param extension: String of the file extension of the image files. Default is .png
        """
        # Create a list of all the images with the desired extension in the current working directory
        images = glob(os.path.join(working_dir, f'*{extension}'))
        # Iterate over all the images, and delete them
        for image in images:
            os.remove(image)

    @staticmethod
    def locate_image(image_dir, image_list, complete, extension='.png'):
        """
        Locate the next image to use in the image directory
        :param image_dir: Name and absolute path of folder containing mock-up images
        :param image_list: List of images already copied to the current working directory
        :param complete: Boolean of whether the analyses are complete
        :param extension: String of the file extension of the image files. Default is .png
        :return: image_list: The list of images with the latest file appended
        """
        # Create a sorted list of all the images with the desired extension in the image folder
        images = sorted(glob(os.path.join(image_dir, f'*{extension}')))
        # If the list of all the images is equivalent to the list of all the processed images, the analyses are compete
        if images == image_list:
            # Set complete to True
            complete = True
            return image_list, complete
        # Iterate over all the images in the folder
        for image in images:
            # Check if the image is already in the list of processed images
            if image not in image_list:
                # Add the image to the list
                image_list.append(image)
                return image_list, complete

    @staticmethod
    def copy_image(working_dir, image):
        """
        Copy the image to the working directory
        :param working_dir: Name and absolute path of current working directory
        :param image: Name and path of the source image to copy to the current working directory
        """
        # Copy the image from the image directory to the current working directory
        # os.path.basename(image)
        shutil.copyfile(
            src=image,
            dst=os.path.join(working_dir, os.path.basename(image))
            #dst=os.path.join(working_dir, 'test_image.png')
        )

    def __init__(self):
        self.current_working_dir = os.getcwd()
        self.image_dir = os.path.join(self.current_working_dir, 'images')
        self.image_list = []


def cli():
    """
    Run the HoldPlace class
    """
    place_holder = HoldPlace()
    place_holder.main()


if __name__ == '__main__':
    cli()

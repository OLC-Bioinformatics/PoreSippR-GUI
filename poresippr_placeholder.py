#!/usr/env/python 3
"""
A placeholder script for the PoreSippr. This script clears out any images in
the current working directory, and periodically copies a mock-up image into the
current working directory. This gives comparable functionality to what I
imagine the final PoreSippr will have
"""

from glob import glob
import multiprocessing
import os
import shutil
import signal
from time import sleep


class HoldPlace:
    """
    A class used to manage the placeholder functionality for the PoreSippr.

    This class is responsible for clearing out any images in the current
    working directory and periodically copying a mock-up image into the current
    working directory. This gives comparable functionality to what the final
    PoreSippr will have.

    Attributes:
    current_working_dir : str
        The current working directory where the images are managed.
    image_dir : str
        The directory where the mock-up images are stored.
    image_list : list
        The list of images that have been processed.
    complete : bool
        A flag indicating whether the process is complete.

    Methods:
    main():
        Runs the appropriate methods in the correct order.
    clear_folder(working_dir, extension='.png'):
        Deletes any image files from a previous iteration of the script.
    locate_image(image_dir, image_list, complete, extension='.png'):
        Locates the next image to use in the image directory.
    copy_image(working_dir, image):
        Copies the image to the working directory.
    """

    def main(self):
        """
        Run the appropriate methods in the correct order
        """

        # Define a signal handler
        def signal_handler(_, __):
            """
            Handles termination signals sent to the process.

            This function is designed to be used as a signal handler for the
            SIGINT (Ctrl+C) and SIGTERM signals. When either of these signals
            is received, it raises a SystemExit exception
            Parameters:
            _ : int
                The signal number that was sent to the process. This argument
                is ignored in this function, hence the underscore.
            __ : frame
                The current stack frame at the time the signal was received.
                This argument is ignored in this function, hence the double
                underscore.
                """
            print('Signal received, stopping...')
            raise SystemExit

        # Register the signal handler for SIGINT (Ctrl+C) and SIGTERM
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        # Create a subprocess for the main loop
        p = multiprocessing.Process(target=self.main_loop)
        p.start()

        # Wait for the subprocess to finish
        while p.is_alive():
            try:
                p.join(timeout=1)
            except SystemExit:
                print('Terminating subprocess...')
                p.terminate()
                p.join()

    def main_loop(self):
        """
        The main loop that is run in a subprocess
        """

        HoldPlace.clear_folder(
            working_dir=self.current_working_dir
        )
        while not self.complete.value:
            self.image_list, complete = HoldPlace.locate_image(
                image_dir=self.image_dir,
                image_list=self.image_list,
                complete=self.complete
            )
            HoldPlace.copy_image(
                working_dir=self.current_working_dir,
                image=self.image_list[-1]
            )
            # Sleep for 5 seconds, checking for signals every second
            for _ in range(5):
                if self.complete.value:
                    break
                sleep(1)

    def terminate(self):
        """
        Terminate the main loop.
        """
        self.complete.value = True

    @staticmethod
    def clear_folder(working_dir, extension='.png'):
        """
        Delete any image files from a previous iteration of the script
        :param working_dir: Name and absolute path of current working directory
        :param extension: String of the file extension of the image files.
            Default is .png
        """
        # Create a list of all the images with the desired extension in the
        # current working directory
        images = glob(os.path.join(working_dir, f'*{extension}'))
        # Iterate over all the images, and delete them
        for image in images:
            os.remove(image)

    @staticmethod
    def locate_image(image_dir, image_list, complete, extension='.png'):
        """
        Locate the next image to use in the image directory
        :param image_dir: Name and absolute path of folder containing mock-up
            images
        :param image_list: List of images already copied to the current working
            directory
        :param complete: Boolean of whether the analyses are complete
        :param extension: String of the file extension of the image files.
            Default is .png
        :return: image_list: The list of images with the latest file appended
        """
        # Create a sorted list of all the images with the desired extension
        # in the image folder
        images = sorted(glob(os.path.join(image_dir, f'*{extension}')))
        # If the list of all the images is equivalent to the list of all the
        # processed images, the analyses are compete
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
        :param image: Name and path of the source image to copy to the current
        working directory
        """
        # Copy the image from the image directory to the current
        # working directory
        shutil.copyfile(
            src=image,
            dst=os.path.join(working_dir, os.path.basename(image))
        )

    def __init__(self, complete):
        self.current_working_dir = os.getcwd()
        self.image_dir = os.path.join(self.current_working_dir, 'images')
        self.image_list = []
        self.complete = complete


def cli():
    """
    Run the HoldPlace class
    """
    complete = multiprocessing.Value('b', False)  # 'b' stands for boolean
    place_holder = HoldPlace(complete=complete)
    place_holder.main()

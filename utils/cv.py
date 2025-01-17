#cv.py

import cv2
import tempfile
import shutil
import os
import numpy as np
from datetime import datetime

class ImageManager:
    def __init__(self):
        self.temp_file_path = None

    def _save_temp_image(self, image):
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
            self.temp_file_path = temp_file.name
            cv2.imwrite(self.temp_file_path, image)
        print(f"Temporary image saved to: {self.temp_file_path}")

    def set_cropped(self, supported_files, current_index, settings, load_image_callback):
        input_file = supported_files[current_index]
        frame = cv2.imread(input_file)

        s_x, s_y, e_x, e_y = settings
        if not (0 <= s_x < e_x <= frame.shape[1] and 0 <= s_y < e_y <= frame.shape[0]):
            print(f"Invalid coordinates for cropping in {input_file}. Skipping cropping.")
            return

        cropped_frame = frame[s_y:e_y, s_x:e_x].copy()
        self._save_temp_image(cropped_frame)
        load_image_callback(self.temp_file_path)

    def set_resize(self, supported_files, current_index, settings, load_image_callback):
        input_file = supported_files[current_index]
        frame = cv2.imread(input_file)

        width, height = settings
        if width <= 0 or height <= 0:
            print(f"Invalid resize dimensions for {input_file}. Skipping resizing.")
            return

        resized_frame = cv2.resize(frame, (width, height))
        self._save_temp_image(resized_frame)
        load_image_callback(self.temp_file_path)

    def set_brightness(self, supported_files, current_index, settings, load_image_callback):
        input_file = supported_files[current_index]
        frame = cv2.imread(input_file)

        frame_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        factor = settings
        frame_hsv[:, :, 2] = np.clip(frame_hsv[:, :, 2] * factor, 0, 255)
        frame = cv2.cvtColor(frame_hsv, cv2.COLOR_HSV2BGR)

        self._save_temp_image(frame)
        load_image_callback(self.temp_file_path)

    def set_saturation(self, supported_files, current_index, settings, load_image_callback):
        input_file = supported_files[current_index]
        frame = cv2.imread(input_file)

        frame_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        factor = settings
        frame_hsv[:, :, 1] = np.clip(frame_hsv[:, :, 1] * factor, 0, 255)
        frame = cv2.cvtColor(frame_hsv, cv2.COLOR_HSV2BGR)

        self._save_temp_image(frame)
        load_image_callback(self.temp_file_path)

    def save_image(self, supported_files, current_index):
        if not supported_files:
            print("No images to process.")
            return

        if current_index >= len(supported_files):
            print("Invalid current index. Cannot find the image.")
            return

        if self.temp_file_path is None:
            print("No processed image available to save.")
            return

        current_image_path = supported_files[current_index]
        destination_path = (
            os.path.splitext(current_image_path)[0]
            + '_'
            + datetime.now().strftime("%Y%m%d_%H%M%S")
            + os.path.splitext(current_image_path)[1]
        )

        try:
            shutil.copyfile(self.temp_file_path, destination_path)
            print(f"Image successfully saved as: {destination_path}")
        except Exception as e:
            print(f"Error occurred while saving the image: {e}")

image_manager = ImageManager()

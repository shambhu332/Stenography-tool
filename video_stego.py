import os
import cv2
import numpy as np
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64

class VideoSteganography:
    @staticmethod
    def encrypt_message(key: str, message: str) -> str:
        cipher = AES.new(key.encode(), AES.MODE_ECB)
        encrypted_msg = cipher.encrypt(pad(message.encode(), AES.block_size))
        return base64.b64encode(encrypted_msg).decode()

    @staticmethod
    def decrypt_message(key: str, encrypted_msg: str) -> str:
        cipher = AES.new(key.encode(), AES.MODE_ECB)
        decrypted_msg = unpad(cipher.decrypt(base64.b64decode(encrypted_msg)), AES.block_size)
        return decrypted_msg.decode()

    @staticmethod
    def encode(video_path: str, message: str, output_path: str, key: str = None) -> None:
        if key:
            message = VideoSteganography.encrypt_message(key, message)

        # Check if the output file already exists and contains data
        existing_message = ""
        if os.path.exists(output_path):
            existing_message = VideoSteganography.decode(output_path, key)

        # Append or replace based on existing data
        if existing_message and existing_message != message:
            message = existing_message + "\n" + message  # Append new data
        # If existing_message == message, replace it (no change needed)

        binary_msg = ''.join(format(ord(c), '08b') for c in message)
        msg_length = format(len(binary_msg), '032b')  # 32-bit header
        full_msg = msg_length + binary_msg

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError("Could not open video file")

        fourcc = cv2.VideoWriter_fourcc(*'FFV1')
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_size = (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), 
                     int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))

        out = cv2.VideoWriter(output_path, fourcc, fps, frame_size, isColor=True)

        bit_index = 0
        while cap.isOpened() and bit_index < len(full_msg):
            ret, frame = cap.read()
            if not ret:
                break

            for row in frame:
                for pixel in row:
                    for channel in range(3):  # BGR channels
                        if bit_index < len(full_msg):
                            pixel[channel] = np.uint8((pixel[channel] & 0xFE) | int(full_msg[bit_index]))
                            bit_index += 1
            
            out.write(frame)

        cap.release()
        out.release()

    @staticmethod
    def decode(video_path: str, key: str = None) -> str:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError("Could not open video file")

        all_bits = []
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            for row in frame:
                for pixel in row:
                    for channel in range(3):
                        all_bits.append(str(pixel[channel] & 1))
        cap.release()

        if len(all_bits) < 32:
            return ""
        msg_length = int(''.join(all_bits[:32]), 2)
        message_bits = all_bits[32:32+msg_length]

        message = ''.join([chr(int(''.join(message_bits[i:i+8]), 2)) 
                          for i in range(0, len(message_bits), 8)])
        if key:
            message = VideoSteganography.decrypt_message(key, message)
        return message

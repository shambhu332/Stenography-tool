import os
import cv2
import numpy as np
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Hash import SHA256
import base64
import tempfile
import shutil

class VideoSteganography:
    @staticmethod
    def _process_key(key: str) -> bytes:
        """Generate 32-byte AES key from any input using SHA-256"""
        return SHA256.new(key.encode()).digest()[:32]

    @staticmethod
    def encrypt_message(key: str, message: str) -> str:
        """Encrypt message with AES-EAX mode and return base64 string"""
        cipher = AES.new(VideoSteganography._process_key(key), AES.MODE_EAX)
        ciphertext, tag = cipher.encrypt_and_digest(message.encode())
        combined = cipher.nonce + tag + ciphertext
        return base64.b64encode(combined).decode()

    @staticmethod
    def decrypt_message(key: str, encrypted_msg: str) -> str:
        """Decrypt message with proper padding and verification"""
        try:
            # Fix base64 padding if needed
            missing_padding = len(encrypted_msg) % 4
            if missing_padding:
                encrypted_msg += '=' * (4 - missing_padding)
            
            data = base64.b64decode(encrypted_msg)
            nonce, tag, ciphertext = data[:16], data[16:32], data[32:]
            cipher = AES.new(VideoSteganography._process_key(key), AES.MODE_EAX, nonce)
            return cipher.decrypt_and_verify(ciphertext, tag).decode()
        except Exception as e:
            raise ValueError(f"Decryption failed: {str(e)}")

    @staticmethod
    def _get_video_capacity(cap) -> int:
        """Calculate maximum storable bits in video"""
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        return frame_count * height * width * 3  # 3 channels per pixel

    @staticmethod
    def encode(video_path: str, message: str, output_path: str, key: str = None) -> None:
        """Encode message with cross-device safe file operations"""
        output_path = os.path.splitext(output_path)[0] + '.avi'
        temp_path = None
        temp_dir = os.path.dirname(output_path) or '.'  # Use output directory for temp files
        
        try:
            # Handle existing messages
            existing_message = ""
            if os.path.exists(output_path):
                try:
                    existing_message = VideoSteganography.decode(output_path, key)
                except Exception as e:
                    print(f"Warning: Could not read existing message - {str(e)}")

            # Prepare full message
            combined_message = f"{existing_message}\n{message}" if existing_message else message
            
            # Encrypt if needed
            if key:
                combined_message = VideoSteganography.encrypt_message(key, combined_message)

            # Convert to binary with header
            binary_msg = ''.join(f"{ord(c):08b}" for c in combined_message)
            full_msg = f"{len(binary_msg):064b}" + binary_msg

            # Open input video
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                raise ValueError("Could not open input video")

            # Verify capacity
            capacity = VideoSteganography._get_video_capacity(cap)
            if len(full_msg) > capacity:
                cap.release()
                raise ValueError(f"Message too large ({len(full_msg)}/{capacity} bits)")

            # Create temporary file in the same directory as output
            temp_fd, temp_path = tempfile.mkstemp(suffix='.avi', dir=temp_dir)
            os.close(temp_fd)  # Close the file descriptor as VideoWriter will open the file
            fourcc = cv2.VideoWriter_fourcc(*'FFV1')
            out = cv2.VideoWriter(temp_path, fourcc, cap.get(cv2.CAP_PROP_FPS),
                                (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                                 int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))),
                                isColor=True)

            # Embed message bits
            bit_idx = 0
            while cap.isOpened() and bit_idx < len(full_msg):
                ret, frame = cap.read()
                if not ret:
                    break

                # Embed in LSB of all color channels
                for row in frame:
                    for pixel in row:
                        for channel in range(3):
                            if bit_idx < len(full_msg):
                                pixel[channel] = (pixel[channel] & 0xFE) | int(full_msg[bit_idx])
                                bit_idx += 1
                out.write(frame)

            # Final checks
            if bit_idx < len(full_msg):
                raise ValueError("Insufficient video frames to store message")

            cap.release()
            out.release()

            # Cross-device safe file replacement
            if temp_path:
                if os.path.exists(output_path):
                    os.remove(output_path)
                shutil.move(temp_path, output_path)

        except Exception as e:
            # Cleanup temporary file on error
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)
            raise
        finally:
            if cap.isOpened():
                cap.release()
            if out and out.isOpened():
                out.release()

    @staticmethod
    def decode(video_path: str, key: str = None) -> str:
        """Decode message with proper error handling"""
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError("Could not open video file")

        bits = []
        try:
            # Extract all LSB bits
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break

                for row in frame:
                    for pixel in row:
                        for channel in range(3):
                            bits.append(str(pixel[channel] & 1))

            # Process extracted bits
            if len(bits) < 64:
                return ""

            msg_length = int(''.join(bits[:64]), 2)
            if len(bits) < 64 + msg_length:
                return ""

            message_bits = bits[64:64+msg_length]
            message = ''.join([chr(int(''.join(message_bits[i:i+8]), 2)) 
                             for i in range(0, len(message_bits), 8)])

            # Decrypt if needed
            if key:
                message = VideoSteganography.decrypt_message(key, message)

            return message

        except Exception as e:
            raise ValueError(f"Decoding failed: {str(e)}")
        finally:
            cap.release()

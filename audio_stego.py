import os
import wave
import struct
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64
from pydub import AudioSegment

class AudioSteganography:
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
    def encode(audio_path: str, message: str, output_path: str, key: str = None) -> None:
        if key:
            message = AudioSteganography.encrypt_message(key, message)

        # Check if the output file already exists and contains data
        existing_message = ""
        if os.path.exists(output_path):
            existing_message = AudioSteganography.decode(output_path, key)

        # Append or replace based on existing data
        if existing_message and existing_message != message:
            message = existing_message + "\n" + message  # Append new data
        # If existing_message == message, replace it (no change needed)

        binary_msg = ''.join(format(ord(c), '08b') for c in message) + '00000000'
        
        if audio_path.endswith('.mp3'):
            audio = AudioSegment.from_mp3(audio_path)
            audio.export("temp.wav", format="wav")
            audio_path = "temp.wav"

        audio = wave.open(audio_path, 'rb')
        params = audio.getparams()
        frames = bytearray(audio.readframes(audio.getnframes()))
        audio.close()

        if len(binary_msg) > len(frames):
            raise ValueError("Message too large for the audio.")

        for i in range(len(binary_msg)):
            frames[i] = (frames[i] & ~1) | int(binary_msg[i])

        with wave.open(output_path, 'wb') as encoded_audio:
            encoded_audio.setparams(params)
            encoded_audio.writeframes(frames)

    @staticmethod
    def decode(audio_path: str, key: str = None) -> str:
        if audio_path.endswith('.mp3'):
            audio = AudioSegment.from_mp3(audio_path)
            audio.export("temp.wav", format="wav")
            audio_path = "temp.wav"

        audio = wave.open(audio_path, 'rb')
        frames = audio.readframes(audio.getnframes())
        audio.close()

        binary_msg = ''.join(str(byte & 1) for byte in frames)
        message = ""
        for i in range(0, len(binary_msg), 8):
            byte = binary_msg[i:i+8]
            if byte == '00000000':
                break
            message += chr(int(byte, 2))
        if key:
            message = AudioSteganography.decrypt_message(key, message)
        return message

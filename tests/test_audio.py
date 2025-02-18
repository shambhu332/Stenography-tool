
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from audio_stego import AudioSteganography
import unittest

class TestAudioSteganography(unittest.TestCase):
    def setUp(self):
        self.test_audio = "tests/test_audio.wav"  # Path to test audio
        self.encoded_audio = "tests/encoded_audio.wav"
        self.message = "Secret Message"

    def test_encode_decode(self):
        # Test encoding to a new file
        AudioSteganography.encode(self.test_audio, self.message, self.encoded_audio)
        decoded_message = AudioSteganography.decode(self.encoded_audio)
        self.assertEqual(self.message, decoded_message)

    def test_append_data(self):
        # Test appending new data to an existing file
        existing_message = "Existing Message"
        AudioSteganography.encode(self.test_audio, existing_message, self.encoded_audio)
        
        # Encode again with a different message
        AudioSteganography.encode(self.encoded_audio, self.message, self.encoded_audio)
        decoded_message = AudioSteganography.decode(self.encoded_audio)
        self.assertEqual(f"{existing_message}\n{self.message}", decoded_message)

    def test_replace_data(self):
        # Test replacing existing data with the same message
        AudioSteganography.encode(self.test_audio, self.message, self.encoded_audio)
        
        # Encode again with the same message
        AudioSteganography.encode(self.encoded_audio, self.message, self.encoded_audio)
        decoded_message = AudioSteganography.decode(self.encoded_audio)
        self.assertEqual(self.message, decoded_message)

    def tearDown(self):
        if os.path.exists(self.encoded_audio):
            os.remove(self.encoded_audio)

if __name__ == "__main__":
    unittest.main()

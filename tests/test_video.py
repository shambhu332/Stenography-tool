import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from video_stego import VideoSteganography
import unittest

class TestVideoSteganography(unittest.TestCase):
    def setUp(self):
        self.test_video = "tests/test_video.avi"
        self.encoded_video = "tests/encoded_video.avi"
        self.message = "Secret Message"

    def test_encode_decode(self):
        # Test encoding to a new file
        VideoSteganography.encode(self.test_video, self.message, self.encoded_video)
        decoded_message = VideoSteganography.decode(self.encoded_video)
        self.assertEqual(self.message, decoded_message)

    def test_append_data(self):
        # Test appending new data to an existing file
        existing_message = "Existing Message"
        VideoSteganography.encode(self.test_video, existing_message, self.encoded_video)
        
        # Encode again with a different message
        VideoSteganography.encode(self.encoded_video, self.message, self.encoded_video)
        decoded_message = VideoSteganography.decode(self.encoded_video)
        self.assertEqual(f"{existing_message}\n{self.message}", decoded_message)

    def test_replace_data(self):
        # Test replacing existing data with the same message
        VideoSteganography.encode(self.test_video, self.message, self.encoded_video)
        
        # Encode again with the same message
        VideoSteganography.encode(self.encoded_video, self.message, self.encoded_video)
        decoded_message = VideoSteganography.decode(self.encoded_video)
        self.assertEqual(self.message, decoded_message)

    def tearDown(self):
        if os.path.exists(self.encoded_video):
            os.remove(self.encoded_video)

if __name__ == "__main__":
    unittest.main()

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from image_stego import ImageSteganography
import unittest

class TestImageSteganography(unittest.TestCase):
    def setUp(self):
        self.test_image = "tests/test_image.png"  # Path to test image
        self.encoded_image = "tests/encoded_image.png"
        self.message = "Secret Message"

    def test_encode_decode(self):
        # Test encoding to a new file
        ImageSteganography.encode(self.test_image, self.message, self.encoded_image)
        decoded_message = ImageSteganography.decode(self.encoded_image)
        self.assertEqual(self.message, decoded_message)

    def test_append_data(self):
        # Test appending new data to an existing file
        existing_message = "Existing Message"
        ImageSteganography.encode(self.test_image, existing_message, self.encoded_image)
        
        # Encode again with a different message
        ImageSteganography.encode(self.encoded_image, self.message, self.encoded_image)
        decoded_message = ImageSteganography.decode(self.encoded_image)
        self.assertEqual(f"{existing_message}\n{self.message}", decoded_message)

    def test_replace_data(self):
        # Test replacing existing data with the same message
        ImageSteganography.encode(self.test_image, self.message, self.encoded_image)
        
        # Encode again with the same message
        ImageSteganography.encode(self.encoded_image, self.message, self.encoded_image)
        decoded_message = ImageSteganography.decode(self.encoded_image)
        self.assertEqual(self.message, decoded_message)

    def tearDown(self):
        if os.path.exists(self.encoded_image):
            os.remove(self.encoded_image)

if __name__ == "__main__":
    unittest.main()

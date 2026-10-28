"""Small smoke tests for text/image preprocessing.

Run with: python -m unittest discover -s tests
These tests don't require Tesseract to be installed.
"""
import unittest
from PIL import Image

from extract_resume import ocr_image


class ExtractorSmokeTests(unittest.TestCase):
    def test_blank_image_returns_string(self):
        image = Image.new("RGB", (400, 120), "white")
        result = ocr_image(image)
        self.assertIsInstance(result, str)


if __name__ == "__main__":
    unittest.main()

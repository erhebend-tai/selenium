# Licensed to the Software Freedom Conservancy (SFC) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The SFC licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

"""
OCR (Optical Character Recognition) Module

Provides OCR capabilities for extracting text from screenshots and images.
"""

import logging
import os
from typing import Dict, List, Optional, Tuple

try:
    import pytesseract
    from PIL import Image
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False


class OCRProcessor:
    """
    OCR processor for extracting text from images and screenshots.
    """

    def __init__(self, tesseract_path: Optional[str] = None):
        """
        Initialize OCR processor.
        
        Args:
            tesseract_path: Optional path to tesseract executable
        """
        if not OCR_AVAILABLE:
            raise ImportError(
                "OCR dependencies not available. Install with: pip install pytesseract pillow"
            )
        
        if tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
        
        self.logger = self._setup_logging()

    def _setup_logging(self) -> logging.Logger:
        """Setup logging for OCR processor."""
        logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger

    def extract_text_from_image(self, image_path: str, language: str = "eng") -> str:
        """
        Extract text from an image file.
        
        Args:
            image_path: Path to the image file
            language: Language for OCR (default: "eng")
            
        Returns:
            Extracted text as string
        """
        try:
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"Image file not found: {image_path}")
            
            image = Image.open(image_path)
            text = pytesseract.image_to_string(image, lang=language)
            
            self.logger.info(f"Extracted {len(text)} characters from {image_path}")
            return text.strip()
            
        except Exception as e:
            self.logger.error(f"Error extracting text from {image_path}: {e}")
            return ""

    def extract_text_with_confidence(self, image_path: str, language: str = "eng") -> List[Dict]:
        """
        Extract text with confidence scores from an image file.
        
        Args:
            image_path: Path to the image file
            language: Language for OCR (default: "eng")
            
        Returns:
            List of dictionaries containing text and confidence information
        """
        try:
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"Image file not found: {image_path}")
            
            image = Image.open(image_path)
            data = pytesseract.image_to_data(image, lang=language, output_type=pytesseract.Output.DICT)
            
            results = []
            for i in range(len(data['text'])):
                if int(data['conf'][i]) > 0:  # Only include text with confidence > 0
                    results.append({
                        'text': data['text'][i],
                        'confidence': int(data['conf'][i]),
                        'left': int(data['left'][i]),
                        'top': int(data['top'][i]),
                        'width': int(data['width'][i]),
                        'height': int(data['height'][i])
                    })
            
            self.logger.info(f"Extracted {len(results)} text elements from {image_path}")
            return results
            
        except Exception as e:
            self.logger.error(f"Error extracting text with confidence from {image_path}: {e}")
            return []

    def detect_text_regions(self, image_path: str) -> List[Tuple[int, int, int, int]]:
        """
        Detect text regions in an image.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            List of tuples containing (left, top, width, height) for each text region
        """
        try:
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"Image file not found: {image_path}")
            
            image = Image.open(image_path)
            data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
            
            regions = []
            for i in range(len(data['text'])):
                if int(data['conf'][i]) > 30:  # Only include regions with confidence > 30
                    regions.append((
                        int(data['left'][i]),
                        int(data['top'][i]),
                        int(data['width'][i]),
                        int(data['height'][i])
                    ))
            
            self.logger.info(f"Detected {len(regions)} text regions in {image_path}")
            return regions
            
        except Exception as e:
            self.logger.error(f"Error detecting text regions in {image_path}: {e}")
            return []

    def get_supported_languages(self) -> List[str]:
        """
        Get list of supported languages for OCR.
        
        Returns:
            List of supported language codes
        """
        try:
            languages = pytesseract.get_languages(config='')
            self.logger.info(f"Found {len(languages)} supported languages")
            return languages
        except Exception as e:
            self.logger.error(f"Error getting supported languages: {e}")
            return ["eng"]  # Default to English

    def preprocess_image_for_ocr(self, image_path: str, output_path: str) -> str:
        """
        Preprocess an image to improve OCR accuracy.
        
        Args:
            image_path: Path to the input image
            output_path: Path to save the preprocessed image
            
        Returns:
            Path to the preprocessed image
        """
        try:
            from PIL import ImageEnhance, ImageFilter
            
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"Image file not found: {image_path}")
            
            image = Image.open(image_path)
            
            # Convert to grayscale
            image = image.convert('L')
            
            # Enhance contrast
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(2.0)
            
            # Sharpen the image
            image = image.filter(ImageFilter.SHARPEN)
            
            # Save preprocessed image
            image.save(output_path)
            
            self.logger.info(f"Preprocessed image saved to {output_path}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"Error preprocessing image {image_path}: {e}")
            return image_path  # Return original path if preprocessing fails

    def extract_text_from_region(self, image_path: str, region: Tuple[int, int, int, int], 
                                 language: str = "eng") -> str:
        """
        Extract text from a specific region of an image.
        
        Args:
            image_path: Path to the image file
            region: Tuple of (left, top, width, height) defining the region
            language: Language for OCR
            
        Returns:
            Extracted text from the region
        """
        try:
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"Image file not found: {image_path}")
            
            image = Image.open(image_path)
            left, top, width, height = region
            cropped_image = image.crop((left, top, left + width, top + height))
            
            text = pytesseract.image_to_string(cropped_image, lang=language)
            
            self.logger.info(f"Extracted text from region {region}: {len(text)} characters")
            return text.strip()
            
        except Exception as e:
            self.logger.error(f"Error extracting text from region {region}: {e}")
            return ""

    def validate_text_quality(self, text: str, min_confidence: int = 50) -> bool:
        """
        Validate the quality of extracted text based on various criteria.
        
        Args:
            text: Extracted text to validate
            min_confidence: Minimum confidence threshold
            
        Returns:
            True if text quality is acceptable, False otherwise
        """
        if not text or len(text.strip()) < 3:
            return False
        
        # Check for reasonable character distribution
        alpha_chars = sum(1 for c in text if c.isalpha())
        total_chars = len(text.replace(' ', ''))
        
        if total_chars == 0:
            return False
        
        alpha_ratio = alpha_chars / total_chars
        
        # Text should have at least 30% alphabetic characters
        if alpha_ratio < 0.3:
            return False
        
        # Check for excessive special characters (possible OCR errors)
        special_chars = sum(1 for c in text if not c.isalnum() and not c.isspace())
        special_ratio = special_chars / len(text) if len(text) > 0 else 0
        
        # Reject if more than 40% special characters
        if special_ratio > 0.4:
            return False
        
        return True

    @staticmethod
    def is_ocr_available() -> bool:
        """
        Check if OCR dependencies are available.
        
        Returns:
            True if OCR is available, False otherwise
        """
        return OCR_AVAILABLE
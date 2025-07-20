#!/usr/bin/env python
"""
Test script for slate detection functionality.

This script tests the slate detection capabilities without requiring DaVinci Resolve
to be running. Useful for development and debugging.
"""

import sys
import os
import tempfile
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# Add the parent directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from src.resolve_mcp.slate_detection import SlateDetector, SlateInfo
    print("Successfully imported slate detection module")
except ImportError as e:
    print(f"Failed to import slate detection module: {e}")
    print("Make sure all dependencies are installed:")
    print("pip install opencv-python pytesseract numpy Pillow")
    sys.exit(1)

def create_test_slate_image(width=1920, height=1080):
    """
    Create a test slate image for testing OCR functionality.
    
    Returns:
        PIL Image object containing a synthetic slate
    """
    # Create a white background
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)
    
    # Try to use a standard font, fall back to default if not available
    try:
        font_large = ImageFont.truetype("arial.ttf", 60)
        font_medium = ImageFont.truetype("arial.ttf", 40)
        font_small = ImageFont.truetype("arial.ttf", 30)
    except OSError:
        # Fall back to default font
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Draw slate border (black rectangle)
    border_margin = 100
    draw.rectangle([
        border_margin, border_margin, 
        width - border_margin, height - border_margin
    ], outline='black', width=5)
    
    # Draw slate content
    y_pos = border_margin + 50
    
    # Production name
    draw.text((border_margin + 50, y_pos), "MY AWESOME FILM", fill='black', font=font_large)
    y_pos += 100
    
    # Director
    draw.text((border_margin + 50, y_pos), "Director: John Smith", fill='black', font=font_medium)
    y_pos += 80
    
    # Scene and slate info
    draw.text((border_margin + 50, y_pos), "Scene: 5A", fill='black', font=font_medium)
    draw.text((border_margin + 400, y_pos), "Slate: 23", fill='black', font=font_medium)
    y_pos += 80
    
    # Take and camera
    draw.text((border_margin + 50, y_pos), "Take: 3", fill='black', font=font_medium)
    draw.text((border_margin + 400, y_pos), "Camera: A", fill='black', font=font_medium)
    y_pos += 80
    
    # Roll and date
    draw.text((border_margin + 50, y_pos), "Roll: 001", fill='black', font=font_medium)
    draw.text((border_margin + 400, y_pos), "Date: 12/15/2023", fill='black', font=font_medium)
    
    return img

def test_slate_detection():
    """Test the slate detection functionality with a synthetic image."""
    print("\n" + "="*50)
    print("Testing Slate Detection Functionality")
    print("="*50)
    
    # Create test slate image
    print("Creating test slate image...")
    test_image = create_test_slate_image()
    
    # Convert PIL image to numpy array (OpenCV format)
    frame = np.array(test_image)
    frame = frame[:, :, ::-1]  # Convert RGB to BGR for OpenCV
    
    # Initialize detector
    print("Initializing slate detector...")
    try:
        detector = SlateDetector()
        print("✓ Slate detector initialized successfully")
    except Exception as e:
        print(f"✗ Failed to initialize slate detector: {e}")
        return False
    
    # Analyze the frame
    print("Analyzing test slate...")
    try:
        slate_info = detector.analyze_frame(frame, 0)
        print("✓ Slate analysis completed")
    except Exception as e:
        print(f"✗ Failed to analyze slate: {e}")
        return False
    
    # Display results
    print("\n" + "-"*30)
    print("Detection Results:")
    print("-"*30)
    print(f"Confidence: {slate_info.confidence:.2f}")
    print(f"Production: {slate_info.production}")
    print(f"Slate Number: {slate_info.slate_number}")
    print(f"Scene: {slate_info.scene}")
    print(f"Take: {slate_info.take}")
    print(f"Roll: {slate_info.roll}")
    print(f"Camera: {slate_info.camera}")
    print(f"Director: {slate_info.director}")
    print(f"Date: {slate_info.date}")
    
    # Evaluate results
    success = True
    expected_values = {
        'slate_number': '23',
        'scene': '5a',
        'take': '3',
        'camera': 'a'
    }
    
    print("\n" + "-"*30)
    print("Validation:")
    print("-"*30)
    
    for field, expected in expected_values.items():
        actual = getattr(slate_info, field)
        if actual and actual.lower() == expected:
            print(f"✓ {field}: Expected '{expected}', got '{actual}'")
        else:
            print(f"✗ {field}: Expected '{expected}', got '{actual}'")
            success = False
    
    if slate_info.confidence > 0.5:
        print(f"✓ Confidence: {slate_info.confidence:.2f} (>= 0.5)")
    else:
        print(f"✗ Confidence: {slate_info.confidence:.2f} (< 0.5)")
        success = False
    
    return success

def test_clip_naming():
    """Test the clip naming functionality."""
    print("\n" + "="*50)
    print("Testing Clip Naming Functionality")
    print("="*50)
    
    # Mock ResolveAPI for testing
    class MockResolveAPI:
        pass
    
    try:
        from src.resolve_mcp.slate_detection import ClipRenamer
        
        mock_api = MockResolveAPI()
        renamer = ClipRenamer(mock_api)
        
        # Test with sample slate info
        slate_info = SlateInfo(
            production="My Film",
            slate_number="23A",
            scene="5",
            take="3",
            camera="A",
            confidence=0.85
        )
        
        original_name = "MVI_1234.mov"
        new_name = renamer.generate_clip_name(slate_info, original_name)
        
        print(f"Original name: {original_name}")
        print(f"Generated name: {new_name}")
        print(f"✓ Clip naming test completed")
        
        return True
        
    except Exception as e:
        print(f"✗ Clip naming test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("Slate Detection Test Suite")
    print("="*50)
    
    # Check dependencies
    print("Checking dependencies...")
    try:
        import cv2
        print("✓ OpenCV available")
    except ImportError:
        print("✗ OpenCV not available")
        return False
    
    try:
        import pytesseract
        print("✓ pytesseract available")
    except ImportError:
        print("✗ pytesseract not available")
        return False
    
    # Test Tesseract installation
    try:
        pytesseract.get_tesseract_version()
        print("✓ Tesseract OCR available")
    except Exception as e:
        print(f"✗ Tesseract OCR not available: {e}")
        print("Please install Tesseract OCR and ensure it's in your PATH")
        return False
    
    # Run tests
    slate_test_passed = test_slate_detection()
    naming_test_passed = test_clip_naming()
    
    # Summary
    print("\n" + "="*50)
    print("Test Summary")
    print("="*50)
    
    if slate_test_passed:
        print("✓ Slate detection test PASSED")
    else:
        print("✗ Slate detection test FAILED")
    
    if naming_test_passed:
        print("✓ Clip naming test PASSED")
    else:
        print("✗ Clip naming test FAILED")
    
    if slate_test_passed and naming_test_passed:
        print("\n🎉 All tests PASSED! Slate detection is ready to use.")
        return True
    else:
        print("\n❌ Some tests FAILED. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

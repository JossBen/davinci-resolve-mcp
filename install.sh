#!/bin/bash

# DaVinci Resolve MCP Server with Slate Detection - Installation Script

echo "=============================================="
echo "DaVinci Resolve MCP Server Installation"
echo "=============================================="

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check Python version
echo "Checking Python installation..."
if command_exists python3; then
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    echo "✓ Python found: $PYTHON_VERSION"
    PYTHON_CMD="python3"
elif command_exists python; then
    PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
    echo "✓ Python found: $PYTHON_VERSION"
    PYTHON_CMD="python"
else
    echo "✗ Python not found. Please install Python 3.8 or higher."
    exit 1
fi

# Check if we're in the correct directory
if [ ! -f "setup.py" ] && [ ! -f "requirements.txt" ]; then
    echo "✗ Please run this script from the root directory of the resolve-mcp project"
    exit 1
fi

echo ""
echo "Installing Python dependencies..."
echo "=================================="

# Install core dependencies first
echo "Installing core MCP dependencies..."
$PYTHON_CMD -m pip install mcp>=0.3.0 pydantic>=2.0.0 typing-extensions>=4.0.0

# Install slate detection dependencies
echo "Installing slate detection dependencies..."
$PYTHON_CMD -m pip install opencv-python>=4.8.0 pytesseract>=0.3.10 numpy>=1.21.0 Pillow>=9.0.0 imageio>=2.25.0 imageio-ffmpeg>=0.4.8

echo ""
echo "Installing Tesseract OCR..."
echo "==========================="

# Detect OS and provide instructions
OS="$(uname -s)"
case "${OS}" in
    Linux*)
        echo "Detected Linux system"
        if command_exists apt-get; then
            echo "Installing Tesseract via apt-get..."
            sudo apt-get update && sudo apt-get install -y tesseract-ocr
        elif command_exists yum; then
            echo "Installing Tesseract via yum..."
            sudo yum install -y tesseract
        elif command_exists dnf; then
            echo "Installing Tesseract via dnf..."
            sudo dnf install -y tesseract
        else
            echo "Please install Tesseract OCR manually:"
            echo "  Ubuntu/Debian: sudo apt-get install tesseract-ocr"
            echo "  CentOS/RHEL: sudo yum install tesseract"
            echo "  Fedora: sudo dnf install tesseract"
        fi
        ;;
    Darwin*)
        echo "Detected macOS system"
        if command_exists brew; then
            echo "Installing Tesseract via Homebrew..."
            brew install tesseract
        else
            echo "Homebrew not found. Please install Tesseract manually:"
            echo "1. Install Homebrew: /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
            echo "2. Install Tesseract: brew install tesseract"
            echo ""
            echo "Or download from: https://github.com/tesseract-ocr/tesseract/wiki"
        fi
        ;;
    CYGWIN*|MINGW*|MSYS*)
        echo "Detected Windows system"
        echo "Please install Tesseract OCR manually:"
        echo "1. Download from: https://github.com/UB-Mannheim/tesseract/wiki"
        echo "2. Install the executable"
        echo "3. Add Tesseract to your system PATH"
        echo "4. Common installation path: C:\\Program Files\\Tesseract-OCR"
        ;;
    *)
        echo "Unknown OS: ${OS}"
        echo "Please install Tesseract OCR manually for your system"
        ;;
esac

echo ""
echo "Verifying installation..."
echo "========================="

# Test Python imports
echo "Testing Python dependencies..."
$PYTHON_CMD -c "
try:
    import mcp
    print('✓ MCP library installed')
except ImportError as e:
    print('✗ MCP library not found:', e)

try:
    import cv2
    print('✓ OpenCV installed')
except ImportError as e:
    print('✗ OpenCV not found:', e)

try:
    import pytesseract
    print('✓ pytesseract installed')
except ImportError as e:
    print('✗ pytesseract not found:', e)

try:
    import numpy
    print('✓ numpy installed')
except ImportError as e:
    print('✗ numpy not found:', e)

try:
    from PIL import Image
    print('✓ Pillow installed')
except ImportError as e:
    print('✗ Pillow not found:', e)
"

# Test Tesseract
echo ""
echo "Testing Tesseract OCR..."
if command_exists tesseract; then
    TESSERACT_VERSION=$(tesseract --version 2>&1 | head -n1)
    echo "✓ Tesseract found: $TESSERACT_VERSION"
else
    echo "✗ Tesseract not found in PATH"
    echo "  Please ensure Tesseract is installed and added to your system PATH"
fi

echo ""
echo "Creating slate detection module..."
echo "=================================="

# Check if slate_detection.py exists
if [ ! -f "src/resolve_mcp/slate_detection.py" ]; then
    echo "✗ slate_detection.py not found"
    echo "Please create src/resolve_mcp/slate_detection.py with the slate detection code"
else
    echo "✓ slate_detection.py found"
fi

echo ""
echo "Installation Summary"
echo "==================="
echo ""
echo "Next steps:"
echo "1. Ensure DaVinci Resolve is installed and running"
echo "2. Start the MCP server:"
echo "   $PYTHON_CMD src/resolve_mcp/server.py"
echo ""
echo "3. Test slate detection functionality:"
echo "   - Use analyze_and_rename_clips(dry_run=True) to preview"
echo "   - Use analyze_single_clip_slate('clip_name.mov') to test single clips"
echo ""
echo "4. If you encounter issues:"
echo "   - Check that all dependencies are installed"
echo "   - Verify Tesseract is in your PATH"
echo "   - Ensure DaVinci Resolve is running"
echo ""
echo "For help, refer to the usage guide or run:"
echo "install_slate_detection_dependencies()"
echo ""
echo "Installation complete!"
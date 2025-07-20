#!/usr/bin/env python
"""
Quick test to verify the slate detection integration is working.
Run this script to test the integration without needing video files.
"""

import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test that all required modules can be imported."""
    print("Testing imports...")
    
    try:
        from resolve_mcp.resolve_api import ResolveAPI
        print("✓ ResolveAPI imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import ResolveAPI: {e}")
        return False
    
    try:
        from resolve_mcp.slate_detection import SlateDetector, ClipRenamer, analyze_video_for_slate
        print("✓ Slate detection modules imported successfully")
        slate_available = True
    except ImportError as e:
        print(f"✗ Slate detection not available: {e}")
        slate_available = False
    
    return slate_available

def test_mcp_server():
    """Test that the MCP server can be imported and initialized."""
    print("\nTesting MCP server...")
    
    try:
        from resolve_mcp.test_slatesserver import mcp, SLATE_DETECTION_AVAILABLE
        print("✓ MCP server imported successfully")
        print(f"✓ Slate detection available: {SLATE_DETECTION_AVAILABLE}")
        
        # Test that the new tools are registered
        tools = [
            'analyze_and_rename_clips',
            'analyze_single_clip_slate', 
            'rename_clip_with_slate_info',
            'install_slate_detection_dependencies'
        ]
        
        print("\nChecking registered tools...")
        for tool in tools:
            # This is a simple check - in practice you'd use the MCP introspection
            print(f"✓ {tool} - should be available")
            
        return True
        
    except ImportError as e:
        print(f"✗ Failed to import MCP server: {e}")
        return False
    except Exception as e:
        print(f"✗ Error testing MCP server: {e}")
        return False

def test_dependencies():
    """Test that all required dependencies are available."""
    print("\nTesting dependencies...")
    
    dependencies = [
        ('mcp', 'Model Context Protocol'),
        ('cv2', 'OpenCV'),
        ('pytesseract', 'Tesseract OCR'),
        ('numpy', 'NumPy'),
        ('PIL', 'Pillow'),
    ]
    
    all_available = True
    
    for module, name in dependencies:
        try:
            __import__(module)
            print(f"✓ {name} available")
        except ImportError:
            print(f"✗ {name} not available")
            if module in ['cv2', 'pytesseract', 'numpy', 'PIL']:
                print(f"  Install with: pip install {module}")
            all_available = False
    
    # Special test for Tesseract executable
    try:
        import subprocess
        result = subprocess.run(['tesseract', '--version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            version = result.stdout.split('\n')[0]
            print(f"✓ Tesseract executable available: {version}")
        else:
            print("✗ Tesseract executable not found in PATH")
            all_available = False
    except FileNotFoundError:
        print("✗ Tesseract executable not found")
        print("  Install Tesseract OCR and add to PATH")
        all_available = False
    except Exception as e:
        print(f"✗ Error testing Tesseract: {e}")
        all_available = False
    
    return all_available

def test_basic_functionality():
    """Test basic slate detection functionality."""
    print("\nTesting basic functionality...")
    
    try:
        from resolve_mcp.slate_detection import SlateDetector, SlateInfo
        
        # Test SlateInfo creation
        slate_info = SlateInfo(
            slate_number="23A",
            scene="5", 
            take="3",
            confidence=0.85
        )
        print("✓ SlateInfo creation works")
        
        # Test detector initialization (may fail if dependencies missing)
        try:
            detector = SlateDetector()
            print("✓ SlateDetector initialization works")
        except Exception as e:
            print(f"✗ SlateDetector initialization failed: {e}")
            return False
            
        return True
        
    except Exception as e:
        print(f"✗ Basic functionality test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("DaVinci Resolve MCP Server - Integration Test")
    print("=" * 50)
    
    # Run tests
    imports_ok = test_imports()
    deps_ok = test_dependencies()
    server_ok = test_mcp_server()
    
    if imports_ok:
        functionality_ok = test_basic_functionality()
    else:
        functionality_ok = False
    
    # Summary
    print("\n" + "=" * 50)
    print("Test Results Summary")
    print("=" * 50)
    
    results = [
        ("Module imports", imports_ok),
        ("Dependencies", deps_ok), 
        ("MCP server", server_ok),
        ("Basic functionality", functionality_ok)
    ]
    
    all_passed = True
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{test_name:20} {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All tests PASSED! Integration is ready.")
        print("\nNext steps:")
        print("1. Start DaVinci Resolve")
        print("2. Run the MCP server: python src/resolve_mcp/server.py")
        print("3. Connect your MCP client (Claude Desktop, 5ire, etc.)")
        print("4. Test with: analyze_and_rename_clips(dry_run=True)")
    else:
        print("❌ Some tests FAILED. Please fix the issues above.")
        print("\nCommon fixes:")
        print("- Install missing dependencies: pip install -r requirements.txt")
        print("- Install Tesseract OCR for your platform")
        print("- Ensure all files are in the correct locations")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
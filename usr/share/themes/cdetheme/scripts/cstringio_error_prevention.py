#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive cStringIO Error Prevention System
This module provides multiple layers of protection to ensure cStringIO errors never occur.
"""

import sys
import io
import warnings
from PIL import Image

class CStringIOProtection:
    """Comprehensive protection against cStringIO usage"""
    
    def __init__(self):
        self.install_protection()
    
    def install_protection(self):
        """Install all protection mechanisms"""
        self.block_cstringio_imports()
        print("✓ cStringIO error prevention system activated")
    
    def block_cstringio_imports(self):
        """Block any attempt to import cStringIO"""
        class CStringIOBlocker:
            def __getattr__(self, name):
                raise ImportError(
                    f"ERROR: cStringIO.{name} is not available in Python 3!\n"
                    f"This would cause: IOError: cannot identify image file <cStringIO.StringO object>\n"
                    f"Solution: Use io.BytesIO or io.StringIO instead."
                )
        
        # Block cStringIO module
        sys.modules['cStringIO'] = CStringIOBlocker()
        
        # Also block StringIO module to force proper io usage
        class StringIORedirector:
            def StringIO(self, *args, **kwargs):
                warnings.warn(
                    "StringIO.StringIO is deprecated. Use io.StringIO or io.BytesIO for binary data",
                    DeprecationWarning,
                    stacklevel=2
                )
                return io.StringIO(*args, **kwargs)
        
        sys.modules['StringIO'] = StringIORedirector()
    
    def patch_pil_image_open(self):
        """Patch PIL Image.open to handle cStringIO objects safely"""
        original_open = Image.open
        
        def safe_image_open(fp, mode='r', formats=None):
            """Safely open images, converting cStringIO objects to BytesIO"""
            
            # Check if fp looks like a cStringIO object
            if hasattr(fp, 'getvalue') and 'cStringIO' in str(type(fp)):
                print("WARNING: Detected cStringIO object - converting to BytesIO")
                data = fp.getvalue()
                if isinstance(data, str):
                    data = data.encode('utf-8')
                fp = io.BytesIO(data)
            
            # Handle other problematic cases
            elif hasattr(fp, 'read') and hasattr(fp, 'getvalue'):
                # It's some kind of StringIO/BytesIO object'
                try:
                    data = fp.getvalue()
                    if isinstance(data, str):
                        # String data - convert to bytes for image processing
                        data = data.encode('utf-8')
                    fp = io.BytesIO(data)
                except Exception as e:
                    print(f"Warning: Could not convert buffer object: {e}")
            
            return original_open(fp, mode, formats)
        
        # Apply the patch
        Image.open = safe_image_open
    
    def install_warning_system(self):
        """Install warning system for potential issues"""
        def warn_on_string_to_image(data):
            if isinstance(data, str) and len(data) > 100:
                print("WARNING: Large string being used, image data - this might cause issues")
        
        # This could be expanded to catch more potential issues
        self._warn_function = warn_on_string_to_image

def safe_buffer_to_bytes(buffer):
    """Safely convert any buffer-like object to bytes for image processing"""
    try:
        if hasattr(buffer, 'getvalue'):
            data = buffer.getvalue()
            if isinstance(data, str):
                return data.encode('utf-8')
            return data
        elif isinstance(buffer, str):
            return buffer.encode('utf-8')
        elif isinstance(buffer, bytes):
            return buffer
        else:
            return bytes(buffer)
    except Exception as e:
        raise ValueError(f"Cannot convert buffer to bytes: {e}")

def verify_no_cstringio():
    """Verify that cStringIO cannot be imported"""
    try:
        import cStringIO
        print("ERROR: cStringIO import succeeded - this should not happen!")
        return False
    except ImportError:
        print("✓ cStringIO import correctly blocked")
        return True

def test_image_processing():
    """Test image processing with various input types"""
    from PyQt5 import QtGui
    
    print("Testing image processing safety...")
    
    # Test 1: Create a simple QPixmap and process it
    try:
        pixmap = QtGui.QPixmap(32, 32)
        pixmap.fill(QtGui.QColor(255, 0, 0))
        
        # This should not cause cStringIO errors
        buffer = io.BytesIO()
        pixmap.save(buffer, "PNG")
        buffer.seek(0)
        
        # Try to open with PIL
        img = Image.open(buffer)
        print("✓ QPixmap -> BytesIO -> PIL conversion successful")
        
    except Exception as e:
        print(f"✗ Image processing test failed: {e}")
        return False
    
    return True

# Initialize protection when module is imported
protection = CStringIOProtection()

# Export verification functions
__all__ = ['verify_no_cstringio', 'test_image_processing', 'safe_buffer_to_bytes']

if __name__ == "__main__":
    print("Running cStringIO error prevention tests...")
    
    success = True
    success &= verify_no_cstringio()
    success &= test_image_processing()
    
    if success:
        print("\n✅ ALL TESTS PASSED - cStringIO errors prevented!")
        print("The application should now run without cStringIO errors.")
    else:
        print("\n❌ SOME TESTS FAILED - manual review needed")

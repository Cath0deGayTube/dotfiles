import io
import sys
import warnings
from PIL import Image
from PyQt5 import QtGui, QtCore
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Image Compatibility Layer for Python 3
This module ensures complete compatibility and prevents cStringIO errors.
"""


# Monkey patch to prevent any cStringIO usage
class CStringIOBlocker:
    """Block any attempt to use cStringIO"""
    def __getattr__(self, name):
        raise ImportError(
            f"cStringIO.{name} is not available in Python 3. "
            f"Use io.BytesIO or io.StringIO instead."
        )

# Install the blocker
sys.modules['cStringIO'] = CStringIOBlocker()

# Also block StringIO module to force io usage
class StringIOBlocker:
    """Block direct StringIO import to force io.StringIO usage"""
    def StringIO(self, *args, **kwargs):
        warnings.warn(
            "StringIO.StringIO is deprecated. Use io.StringIO or io.BytesIO",
            DeprecationWarning,
            stacklevel=2
        )
        return io.StringIO(*args, **kwargs)

sys.modules['StringIO'] = StringIOBlocker()

def safe_image_open(fp, mode='r'):
    """
    Safely open an image file with comprehensive error handling.
    
    Args:
        fp: File path, file object, or buffer
        mode: File mode (ignored for compatibility)
        
    Returns:
        PIL Image object
        
    Raises:
        IOError: If image cannot be opened
    """
    try:
        # Handle different input types
        if hasattr(fp, 'read'):
            # It's a file-like object'
            if hasattr(fp, 'getvalue'):
                # It's a StringIO/BytesIO object'
                data = fp.getvalue()
                if isinstance(data, str):
                    # Convert string to bytes
                    data = data.encode('utf-8')
                fp = io.BytesIO(data)
            elif hasattr(fp, 'seek'):
                # Reset position for file objects
                fp.seek(0)
        elif isinstance(fp, (str, bytes)):
            if isinstance(fp, str) and not fp.startswith('/'):
                # It might be raw image data
                fp = io.BytesIO(fp.encode('utf-8'))
            elif isinstance(fp, bytes):
                fp = io.BytesIO(fp)
        
        # Try to open the image
        return Image.open(fp)
        
    except Exception as e:
        raise IOError(f"Cannot identify image file: {e}")

def qpixmap_to_pil_safe(pixmap):
    """
    Safely convert QPixmap to PIL Image without cStringIO.
    
    Args:
        pixmap: QtGui.QPixmap object
        
    Returns:
        PIL Image object
    """
    if pixmap.isNull():
        raise ValueError("Cannot convert null QPixmap")
    
    try:
        # Method 1: Direct conversion via QImage
        qimage = pixmap.toImage()
        qimage = qimage.convertToFormat(QtGui.QImage.Format_RGBA8888)
        
        width = qimage.width()
        height = qimage.height()
        ptr = qimage.bits()
        if ptr is None:
            raise ValueError("QImage.bits() returned None — image may be null or empty")
        ptr.setsize(height * width * 4)
        
        # Create PIL Image from raw data
        return Image.frombuffer('RGBA', (width, height), ptr, 'raw', 'RGBA', 0, 1)
        
    except Exception:
        # Method 2: Fallback using PNG buffer
        try:
            buffer = QtCore.QBuffer()
            buffer.open(QtCore.QIODevice.ReadWrite)
            
            if not pixmap.save(buffer, "PNG"):
                raise RuntimeError("Failed to save QPixmap to buffer")
            
            buffer.seek(0)
            png_data = buffer.readAll()
            buffer.close()
            
            # Convert QByteArray to bytes
            if hasattr(png_data, 'data'):
                png_bytes = png_data.data()
            else:
                png_bytes = bytes(png_data)
            
            return Image.open(io.BytesIO(png_bytes))
            
        except Exception as e:
            raise IOError(f"Failed to convert QPixmap to PIL Image: {e}")

def pil_to_qpixmap_safe(pil_image):
    """
    Safely convert PIL Image to QPixmap.
    
    Args:
        pil_image: PIL Image object
        
    Returns:
        QtGui.QPixmap object
    """
    try:
        # Ensure RGBA format
        if pil_image.mode != 'RGBA':
            pil_image = pil_image.convert('RGBA')
        
        # Get image data
        data = pil_image.tobytes('raw', 'RGBA')
        qimage = QtGui.QImage(data, pil_image.width, pil_image.height, QtGui.QImage.Format_RGBA8888)
        
        # Create pixmap and ensure data persistence
        return QtGui.QPixmap.fromImage(qimage.copy())
        
    except Exception as e:
        raise IOError(f"Failed to convert PIL Image to QPixmap: {e}")

def validate_image_buffer(buffer):
    """
    Validate and fix image buffer to ensure Python 3 compatibility.
    
    Args:
        buffer: Image buffer or data
        
    Returns:
        io.BytesIO object with valid image data
    """
    if hasattr(buffer, 'getvalue'):
        # It's a StringIO/BytesIO-like object'
        data = buffer.getvalue()
        if isinstance(data, str):
            # Convert string to bytes
            data = data.encode('utf-8')
        return io.BytesIO(data)
    elif isinstance(buffer, str):
        # String data, convert to bytes
        return io.BytesIO(buffer.encode('utf-8'))
    elif isinstance(buffer, bytes):
        # Already bytes
        return io.BytesIO(buffer)
    else:
        # Unknown type, try to handle
        try:
            return io.BytesIO(bytes(buffer))
        except Exception:
            raise TypeError(f"Cannot handle buffer type: {type(buffer)}")

# Monkey patch PIL.Image.open to use our safe version
_original_image_open = Image.open
Image.open = safe_image_open

print("Image compatibility layer loaded - cStringIO errors prevented")

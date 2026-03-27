import os
import time
import tempfile
from io import BytesIO
from fontTools.ttLib import TTFont
from fontTools.subset import Subsetter


class FontCompressor:
    SUPPORTED_FORMATS = ['ttf', 'otf', 'woff', 'woff2']
    FORMAT_MIME_TYPES = {
        'ttf': 'font/ttf',
        'otf': 'font/otf',
        'woff': 'font/woff',
        'woff2': 'font/woff2'
    }

    @staticmethod
    def get_unique_chars(text: str) -> set:
        chars = set()
        for char in text:
            chars.add(char)
        return chars

    @staticmethod
    def compress(font_path: str, text: str, target_format: str, output_path: str = None) -> dict:
        start_time = time.time()
        target_format = target_format.lower()
        
        if target_format not in FontCompressor.SUPPORTED_FORMATS:
            raise ValueError(f"不支持的目标格式: {target_format}")
        
        input_size = os.path.getsize(font_path)
        
        font = TTFont(font_path)
        
        unique_chars = FontCompressor.get_unique_chars(text)
        
        subsetter = Subsetter()
        subsetter.populate(text=text)
        subsetter.subset(font)
        
        if output_path is None:
            base_name = os.path.splitext(os.path.basename(font_path))[0]
            output_dir = tempfile.gettempdir()
            output_path = os.path.join(output_dir, f"{base_name}_subset.{target_format}")
        
        if target_format == 'woff':
            font.flavor = 'woff'
        elif target_format == 'woff2':
            font.flavor = 'woff2'
        else:
            font.flavor = None
        
        font.save(output_path)
        font.close()
        
        output_size = os.path.getsize(output_path)
        elapsed_time = time.time() - start_time
        
        compression_ratio = (1 - output_size / input_size) * 100 if input_size > 0 else 0
        
        return {
            'success': True,
            'input_path': font_path,
            'output_path': output_path,
            'target_format': target_format,
            'input_size': input_size,
            'output_size': output_size,
            'char_count': len(unique_chars),
            'compression_ratio': round(compression_ratio, 2),
            'elapsed_time': round(elapsed_time, 3)
        }

    @staticmethod
    def compress_bytes(font_bytes: bytes, original_filename: str, text: str, target_format: str) -> dict:
        start_time = time.time()
        target_format = target_format.lower()
        
        if target_format not in FontCompressor.SUPPORTED_FORMATS:
            raise ValueError(f"不支持的目标格式: {target_format}")
        
        input_size = len(font_bytes)
        
        ext = os.path.splitext(original_filename)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
            tmp.write(font_bytes)
            tmp_path = tmp.name
        
        try:
            font = TTFont(tmp_path)
            
            unique_chars = FontCompressor.get_unique_chars(text)
            
            subsetter = Subsetter()
            subsetter.populate(text=text)
            subsetter.subset(font)
            
            output_buffer = BytesIO()
            
            if target_format == 'woff':
                font.flavor = 'woff'
            elif target_format == 'woff2':
                font.flavor = 'woff2'
            else:
                font.flavor = None
            
            font.save(output_buffer)
            font.close()
            
            output_bytes = output_buffer.getvalue()
            output_size = len(output_bytes)
            elapsed_time = time.time() - start_time
            
            compression_ratio = (1 - output_size / input_size) * 100 if input_size > 0 else 0
            
            base_name = os.path.splitext(original_filename)[0]
            output_filename = f"{base_name}_subset.{target_format}"
            
            return {
                'success': True,
                'output_bytes': output_bytes,
                'output_filename': output_filename,
                'target_format': target_format,
                'input_size': input_size,
                'output_size': output_size,
                'char_count': len(unique_chars),
                'compression_ratio': round(compression_ratio, 2),
                'elapsed_time': round(elapsed_time, 3),
                'mime_type': FontCompressor.FORMAT_MIME_TYPES.get(target_format, 'application/octet-stream')
            }
        finally:
            os.unlink(tmp_path)

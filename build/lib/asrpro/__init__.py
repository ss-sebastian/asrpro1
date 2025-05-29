"""
ASR Audio Preprocessor

Optimize audio files for child speech recognition with enhanced preprocessing for low-volume speech.

Features:
- Dynamic range compression
- Noise reduction filters
- Low-volume enhancement
- Sample rate standardization (16kHz mono)
- Batch processing of directories
- Cross-platform support (Windows/macOS/Linux)
"""

__version__ = "0.1.2"
__author__ = "Chuqiao 'Sebastian' Song"
__email__ = "songchuqiao23@gmail.com"
__url__ = "https://github.com/ss-sebastian/asrpro"

# 设置包级别的日志记录器
import logging

# 创建包级别的日志记录器
logger = logging.getLogger("asrpro")
logger.setLevel(logging.INFO)

# 如果没有处理器，添加一个控制台处理器
if not logger.handlers:
    ch = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

# 定义包级别的函数
def get_version():
    """返回当前包版本号"""
    return __version__

def enable_debug_logging():
    """启用调试级别的日志记录"""
    logger.setLevel(logging.DEBUG)
    for handler in logger.handlers:
        handler.setLevel(logging.DEBUG)
    logger.debug("Debug logging enabled")

# 导入关键功能以方便访问
from .processor import AudioProcessor
from .cli import main as cli_main

# 简化导入路径
__all__ = [
    'AudioProcessor',
    'cli_main',
    'get_version',
    'enable_debug_logging',
    'logger'
]

# 包初始化信息
logger.info(f"ASRPro v{__version__} initialized")
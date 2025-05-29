import argparse
import sys
import os
import logging
from .processor import AudioProcessor

def main():
    parser = argparse.ArgumentParser(
        description="ASR Audio Preprocessor - Optimize audio files for child speech recognition",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        "input",
        help="Input directory containing audio files"
    )
    
    parser.add_argument(
        "output",
        help="Output directory for processed files"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging for debugging"
    )
    
    parser.add_argument(
        "-f", "--format",
        default="mp3",
        choices=["mp3", "wav", "flac"],
        help="Output audio format"
    )
    
    args = parser.parse_args()
    
    # 设置日志级别
    logger = logging.getLogger("ASRProcessor")
    console_handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    if args.verbose:
        logger.setLevel(logging.DEBUG)
        logger.debug("Verbose mode enabled")
    else:
        logger.setLevel(logging.INFO)
    
    # 验证路径
    if not os.path.exists(args.input):
        logger.error(f"Input directory does not exist: {args.input}")
        sys.exit(1)
    
    processor = AudioProcessor(output_format=args.format)
    processor.process_directory(args.input, args.output)
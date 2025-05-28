import argparse
import sys
from .processor import AudioProcessor

def main():
    parser = argparse.ArgumentParser(
        description="ASR Audio Preprocessor - Optimize audio files for speech recognition",
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
    
    args = parser.parse_args()
    
    # 设置日志级别
    from asrpro.processor import L
    if args.verbose:
        L.setLevel(logging.DEBUG)
    
    processor = AudioProcessor()
    processor.process_directory(args.input, args.output)

if __name__ == "__main__":
    main()
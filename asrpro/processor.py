import os
import tempfile
import logging
import shutil
from pydub import AudioSegment
from pydub.exceptions import CouldntDecodeError

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
L = logging.getLogger("ASRProcessor")

class AudioProcessor:
    def __init__(self):
        pass

    def preprocess_audio(self, input_path):
        """Enhanced audio preprocessing for low-volume speech"""
        try:
            L.info(f"Optimizing audio for ASR: {input_path}")
            
            # 读取音频文件
            audio = AudioSegment.from_file(input_path)

            # 标准化参数
            audio = audio.set_channels(1)  
            audio = audio.set_frame_rate(16000)  

            # 动态范围压缩
            audio = audio.compress_dynamic_range(
                threshold=-40, 
                ratio=3,
                attack=5, 
                release=100
            )
            audio = audio.low_pass_filter(4000)  # 过滤高频噪声
            audio = audio.normalize(headroom=2)  # 保持动态余量
            
            # 二次压缩增强
            audio = audio.compress_dynamic_range(
                threshold=-55,
                ratio=6,
                attack=15,
                release=200
            )

            # 增强低音量部分
            audio = audio.high_pass_filter(80)
            boosted = audio.high_pass_filter(1000).apply_gain(+4)
            audio = audio.overlay(boosted)

            # 调试信息
            if L.level <= logging.DEBUG:
                self._print_audio_stats(audio)

            # 创建临时文件
            temp_fd, temp_path = tempfile.mkstemp(suffix=".mp3")
            os.close(temp_fd)
            
            # 导出处理后的音频
            audio.export(
                temp_path,
                format="mp3",
                codec="libmp3lame",
                bitrate="96k",
                tags={"title": "BA_Optimized"},
                parameters=[
                    "-compression_level", "2",
                    "-reservoir", "0",
                    "-joint_stereo", "0"
                ]
            )

            return temp_path

        except CouldntDecodeError:
            L.error(f"Audio decoding failed: {input_path}")
            return None
        except Exception as e:
            L.error(f"Audio processing error: {str(e)}")
            return None

    def _print_audio_stats(self, audio):
        """打印音频统计信息（仅用于调试）"""
        L.debug(f"Audio stats: duration={len(audio)/1000:.1f}s, "
               f"channels={audio.channels}, "
               f"sample_rate={audio.frame_rate}Hz, "
               f"dBFS={audio.dBFS:.1f}")

    def process_directory(self, input_dir, output_dir):
        """处理整个目录的音频文件"""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            L.info(f"Created output directory: {output_dir}")

        processed_count = 0
        failed_count = 0

        for filename in os.listdir(input_dir):
            input_path = os.path.join(input_dir, filename)
            
            if not os.path.isfile(input_path):
                continue
                
            # 处理音频
            temp_path = self.preprocess_audio(input_path)
            
            # 准备输出路径
            base, ext = os.path.splitext(filename)
            output_filename = f"{base}_processed.mp3"
            output_path = os.path.join(output_dir, output_filename)
            
            if temp_path:
                try:
                    # 移动临时文件到输出目录
                    shutil.move(temp_path, output_path)
                    L.info(f"Processed: {filename} -> {output_filename}")
                    processed_count += 1
                except Exception as e:
                    L.error(f"Failed to save {filename}: {str(e)}")
                    failed_count += 1
            else:
                L.warning(f"Skipped file due to processing error: {filename}")
                failed_count += 1
        
        L.info(f"Processing completed: {processed_count} succeeded, {failed_count} failed")
        return processed_count, failed_count
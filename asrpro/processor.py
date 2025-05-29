import os
import tempfile
import logging
import shutil
import numpy as np
from pydub import AudioSegment
from pydub.silence import detect_nonsilent
from pydub.exceptions import CouldntDecodeError
import webrtcvad

class AudioProcessor:
    def __init__(self, output_format="wav", aggressiveness=3):
        """
        :param output_format: 输出格式 (wav, mp3, flac)
        :param aggressiveness: VAD攻击性级别 (1-3, 3最激进)
        """
        self.output_format = output_format
        self.aggressiveness = min(max(aggressiveness, 1), 3)
        self.logger = logging.getLogger("ChildSpeechProcessor")
        self.vad = webrtcvad.Vad(self.aggressiveness)
    
    def preprocess_audio(self, input_path):
        """针对儿童语音优化的预处理流程"""
        try:
            self.logger.info(f"Processing child speech: {input_path}")
            
            # 1. 加载并基础处理
            audio = AudioSegment.from_file(input_path)
            audio = audio.set_channels(1).set_frame_rate(16000)
            
            # 2. 儿童语音专用噪声抑制
            audio = self._child_specific_noise_reduction(audio)
            
            # 3. 增强型VAD（针对高音调优化）
            audio = self._enhanced_child_vad(audio)
            
            # 4. 儿童语音动态增强
            audio = self._child_voice_enhancement(audio)
            
            # 5. 感知加权归一化
            audio = self._perceptual_normalization(audio)
            
            # 调试信息
            if self.logger.level <= logging.DEBUG:
                self._print_audio_stats(audio)

            # 导出处理后的音频
            return self._export_processed_audio(audio)

        except CouldntDecodeError:
            self.logger.error(f"Audio decoding failed: {input_path}")
            return None
        except Exception as e:
            self.logger.error(f"Audio processing error: {str(e)}")
            return None

    def _child_specific_noise_reduction(self, audio):
        """针对儿童语音的噪声抑制"""
        # 保留高频成分（儿童语音特征）
        filtered = audio.high_pass_filter(150)  # 保留更高频段
        
        # 自适应频谱降噪
        if audio.dBFS < -35:  # 非常轻柔的语音
            filtered = filtered.low_pass_filter(6000)  # 保留更多高频
        else:
            filtered = filtered.low_pass_filter(5000)  # 常规高频保留
            
        # 针对电子噪声的陷波滤波
        for freq in [3000, 4000]:  # 常见电子噪声频率
            filtered = filtered.notch_filter(freq, q=10)
            
        return filtered

    def _enhanced_child_vad(self, audio):
        """针对儿童高音调的增强型VAD"""
        # 转换为适合VAD的格式
        raw_audio = np.array(audio.get_array_of_samples())
        sample_rate = audio.frame_rate
        frame_duration = 30  # ms
        frames = self._frame_generator(raw_audio, sample_rate, frame_duration)
        
        # 检测语音活动
        speech_frames = []
        for frame in frames:
            speech_frames.append(self.vad.is_speech(frame.tobytes(), sample_rate))
        
        # 创建语音活动掩码
        mask = self._create_speech_mask(speech_frames, len(raw_audio), frame_duration, sample_rate)
        
        # 应用时域掩码（保留语音部分，衰减非语音部分）
        return self._apply_soft_mask(audio, mask)

    def _child_voice_enhancement(self, audio):
        """儿童语音动态增强"""
        # 第一级压缩：提升轻柔部分
        compressed = audio.compress_dynamic_range(
            threshold=-45.0,  # 较低阈值捕捉轻柔语音
            ratio=3.0,
            attack=10.0,      # 较慢攻击时间保留自然度
            release=200.0
        )
        
        # 高频增强（儿童语音特征频率）
        high_boost = compressed.high_pass_filter(1500).apply_gain(6)  # 增强1.5kHz以上
        enhanced = compressed.overlay(high_boost)
        
        # 针对尖锐声音的平滑处理
        return enhanced.low_pass_filter(6500)  # 限制极高频率

    def _perceptual_normalization(self, audio):
        """针对儿童语音的感知加权归一化"""
        # 基于感知响度的归一化
        normalized = audio.normalize(headroom=3)
        
        # 针对安静段落的额外增益
        if normalized.dBFS < -25:
            return normalized.apply_gain(6)
        elif normalized.dBFS < -20:
            return normalized.apply_gain(3)
        return normalized

    def _frame_generator(self, audio, sample_rate, frame_duration):
        """生成音频帧"""
        frame_size = int(sample_rate * frame_duration / 1000)
        offset = 0
        while offset + frame_size < len(audio):
            yield audio[offset:offset + frame_size]
            offset += frame_size

    def _create_speech_mask(self, speech_frames, total_samples, frame_duration, sample_rate):
        """创建语音活动软掩码"""
        frame_size = int(sample_rate * frame_duration / 1000)
        mask = np.zeros(total_samples)
        
        for i, is_speech in enumerate(speech_frames):
            start = i * frame_size
            end = min(start + frame_size, total_samples)
            
            # 语音区域：增益1.0，非语音区域：增益0.3
            mask[start:end] = 1.0 if is_speech else 0.3
            
        # 添加平滑过渡
        return np.convolve(mask, np.hanning(50), 'same')

    def _apply_soft_mask(self, audio, mask):
        """应用软掩码到音频"""
        samples = np.array(audio.get_array_of_samples())
        masked_samples = samples * mask[:len(samples)]
        
        # 创建新音频段
        return AudioSegment(
            masked_samples.tobytes(),
            frame_rate=audio.frame_rate,
            sample_width=audio.sample_width,
            channels=1
        )

    def _export_processed_audio(self, audio):
        """导出处理后的音频"""
        temp_fd, temp_path = tempfile.mkstemp(suffix=f".{self.output_format}")
        os.close(temp_fd)
        
        # 儿童语音推荐使用WAV格式保持质量
        if self.output_format == "wav":
            audio.export(temp_path, format="wav", codec="pcm_s16le")
        else:
            format_params = {
                "mp3": {"format": "mp3", "bitrate": "128k"},
                "flac": {"format": "flac", "compression": "5"}
            }.get(self.output_format, {})
            audio.export(temp_path, **format_params)
            
        return temp_path

    def _print_audio_stats(self, audio):
        """打印音频统计信息"""
        self.logger.debug(f"Audio stats: duration={len(audio)/1000:.1f}s, "
               f"channels={audio.channels}, "
               f"sample_rate={audio.frame_rate}Hz, "
               f"dBFS={audio.dBFS:.1f}")

    def process_directory(self, input_dir, output_dir):
        """处理整个目录的音频文件"""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            self.logger.info(f"Created output directory: {output_dir}")

        processed_count = 0
        failed_count = 0

        for filename in os.listdir(input_dir):
            input_path = os.path.join(input_dir, filename)
            
            if not os.path.isfile(input_path):
                continue
                
            # 处理音频
            self.logger.info(f"Processing: {filename}")
            temp_path = self.preprocess_audio(input_path)
            
            if temp_path:
                # 准备输出路径
                base, ext = os.path.splitext(filename)
                output_filename = f"{base}_enhanced.{self.output_format}"
                output_path = os.path.join(output_dir, output_filename)
                
                try:
                    # 移动临时文件到输出目录
                    shutil.move(temp_path, output_path)
                    self.logger.info(f"Enhanced: {filename} -> {output_filename}")
                    processed_count += 1
                except Exception as e:
                    self.logger.error(f"Failed to save {filename}: {str(e)}")
                    failed_count += 1
            else:
                self.logger.warning(f"Skipped file due to processing error: {filename}")
                failed_count += 1
        
        self.logger.info(f"Processing completed: {processed_count} succeeded, {failed_count} failed")
        return processed_count, failed_count
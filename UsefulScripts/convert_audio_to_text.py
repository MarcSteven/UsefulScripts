import speech_recognition as sr
from googletrans import Translator, LANGUAGES
from pydub import AudioSegment
import os

def convert_audio_to_wav(audio_file):
    """将音频文件（包括 M4A）转换为 WAV 格式"""
    try:
        # 支持的音频格式
        supported_formats = ['.wav', '.mp3', '.m4a']
        file_ext = os.path.splitext(audio_file)[1].lower()
        
        if file_ext not in supported_formats:
            print(f"不支持的音频格式：{file_ext}。支持的格式：{', '.join(supported_formats)}")
            return None
        
        if file_ext != '.wav':
            print(f"正在将 {audio_file} 转换为 WAV 格式...")
            audio = AudioSegment.from_file(audio_file)
            wav_file = "temp_audio.wav"
            audio.export(wav_file, format="wav")
            return wav_file
        return audio_file
    except Exception as e:
        print(f"音频转换失败：{e}")
        return None

def speech_to_text(audio_file):
    """将语音转换为文字"""
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(audio_file) as source:
            audio_data = recognizer.record(source)
            # 使用 Google Speech Recognition 转换为文字
            text = recognizer.recognize_google(audio_data)
            print("转录文本：", text)
            return text
    except sr.UnknownValueError:
        print("无法识别音频内容")
        return None
    except sr.RequestError as e:
        print(f"语音识别请求失败：{e}")
        return None
    except Exception as e:
        print(f"转录过程中出错：{e}")
        return None

def translate_text(text, target_language):
    """将文本翻译成指定语言"""
    if not text:
        return None
    try:
        translator = Translator()
        translated = translator.translate(text, dest=target_language)
        print(f"翻译成 {LANGUAGES.get(target_language, target_language)}：{translated.text}")
        return translated.text
    except Exception as e:
        print(f"翻译失败：{e}")
        return None

def main():
    # 配置信息
    audio_file = input("请输入音频文件路径（例如 input_audio.m4a）：")
    target_language = input("请输入目标语言代码（例如 en, zh-cn, es）：")

    # 验证语言代码
    if target_language.lower() not in LANGUAGES:
        print(f"无效的语言代码！支持的语言代码包括：{', '.join(LANGUAGES.keys())}")
        return

    # 验证音频文件是否存在
    if not os.path.exists(audio_file):
        print(f"错误：音频文件 {audio_file} 不存在！")
        return

    # 转换为 WAV 格式（如果需要）
    wav_file = convert_audio_to_wav(audio_file)
    if not wav_file:
        return

    # 语音转文字
    text = speech_to_text(wav_file)
    if text:
        # 翻译文本
        translated_text = translate_text(text, target_language.lower())
        if translated_text:
            # 保存结果到文件
            output_file = "output_text.txt"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"原始文本: {text}\n")
                f.write(f"翻译文本 ({target_language}): {translated_text}\n")
            print(f"结果已保存到 {output_file}")

    # 清理临时 WAV 文件
    if wav_file != audio_file and os.path.exists(wav_file):
        os.remove(wav_file)
        print(f"已删除临时文件 {wav_file}")

if __name__ == "__main__":
    main()
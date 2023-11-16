import pyaudio
import wave
import openai
import tempfile
import os
from googletrans import Translator

# 環境変数からOpenAI APIキーを設定
api_key = os.getenv("OPENAI_API_KEY")

if api_key is None:
    print("APIキーが設定されていません。環境変数を確認してください。")
else:
    # OpenAIライブラリにAPIキーを設定
    openai.api_key = api_key

# リアルタイム音声録音を行い、一時ファイルに保存する関数
def record_audio(duration=5):
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    CHUNK = 1024
    RECORD_SECONDS = duration
    audio = pyaudio.PyAudio()

    # 録音開始
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK)
    print("Recording...")
    frames = []

    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("Finished recording.")

    # 録音終了
    stream.stop_stream()
    stream.close()
    audio.terminate()

    # 一時ファイルに保存
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
    wf = wave.open(temp_file.name, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(audio.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

    return temp_file.name

# Whisperモデルを使用して音声認識を行う関数
def recognize_speech_with_whisper(audio_file_path):
    
    response = openai.Audio.transcribe(
        model="whisper-1",
        file=open(audio_file_path, "rb"),
        language=None
    )
    return response['text']

# googletransを使用してテキストを翻訳する関数
def translate_text_with_googletrans(text, target_language="ja"):
    translator = Translator()
    translation = translator.translate(text, src='en', dest=target_language)
    return translation.text

# メイン関数
def main():
    audio_file = record_audio(5)  # 5秒間の録音
    recognized_text = recognize_speech_with_whisper(audio_file)
    translated_text = translate_text_with_googletrans(recognized_text)  # googletransで翻訳
    print("Recognized Text:", recognized_text)
    print("Translated Text:", translated_text)
    os.remove(audio_file)  # 一時ファイルの削除

main()
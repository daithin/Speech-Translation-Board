import pyaudio
import wave
import openai
import tempfile
import os
from googletrans import Translator
import tkinter as tk

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
def translate_text_with_googletrans(text, source_language="en", target_language="ja"):
    translator = Translator()
    translation = translator.translate(text, src=source_language, dest=target_language)
    return translation.text

def main():
    def start_recognition():
        record_seconds = int(record_seconds_entry.get())
        source_language = source_language_entry.get()
        target_language = target_language_entry.get()

        audio_file = record_audio(record_seconds)
        recognized_text = recognize_speech_with_whisper(audio_file)
        translated_text = translate_text_with_googletrans(recognized_text, source_language, target_language)
        
        # 結果をリストボックスに追加
        history_listbox.insert(tk.END, f"認識: {recognized_text}")
        history_listbox.insert(tk.END, f"翻訳: {translated_text}")
        
        os.remove(audio_file)


    def swap_languages():
        # 現在の言語設定を取得
        current_source = source_language_entry.get()
        current_target = target_language_entry.get()

        # ソースとターゲットを入れ替え
        source_language_entry.delete(0, tk.END)
        source_language_entry.insert(0, current_target)
        target_language_entry.delete(0, tk.END)
        target_language_entry.insert(0, current_source)

    # Tkinterウィンドウの設定
    root = tk.Tk()
    root.title("音声認識と翻訳")

    tk.Label(root, text="録音秒数").grid(row=0, column=0)
    record_seconds_entry = tk.Entry(root)
    record_seconds_entry.grid(row=0, column=1)

    tk.Label(root, text="入力言語").grid(row=1, column=0)
    source_language_entry = tk.Entry(root)
    source_language_entry.grid(row=1, column=1)

    tk.Label(root, text="翻訳言語").grid(row=2, column=0)
    target_language_entry = tk.Entry(root)
    target_language_entry.grid(row=2, column=1)

    start_button = tk.Button(root, text="開始", command=start_recognition)
    start_button.grid(row=3, column=0, columnspan=2)

    swap_button = tk.Button(root, text="言語入れ替え", command=swap_languages)
    swap_button.grid(row=4, column=0, columnspan=2)

    # 会話履歴表示用のリストボックス
    history_listbox = tk.Listbox(root, height=10, width=50)
    history_listbox.grid(row=5, column=0, columnspan=2)


    root.mainloop()

if __name__ == "__main__":
    main()

#!/bin/env python

import os
import sys
import openai
import settings
import textract
from playsound import playsound
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QPushButton, QLineEdit, QTextEdit, QWidget, QComboBox, QHBoxLayout, QCheckBox, QLabel, QFileDialog
from PySide6.QtCore import Qt, QThread, Signal
from elevenlabs import ElevenLabs
from gtts import gTTS
from pydub import AudioSegment

import pyaudio
import wave
import time
import numpy as np
import threading
from vosk import Model, KaldiRecognizer


class SpeechRecognitionThread(QThread):
    result_signal = Signal(str)

    def run(self):
        print("Starting speech recognition thread...")
        MODEL_FOLDER = 'vosk-model-en-us-aspire-0.2'
        model = Model(MODEL_FOLDER)
        sample_rate = 16000
        recognizer = KaldiRecognizer(model, sample_rate)

        audio_format = pyaudio.paInt16
        channels = 1
        chunk_size = 1024

        buffer = []

        def callback(in_data, frame_count, time_info, status):
            data = np.frombuffer(in_data, dtype=np.int16)
            buffer.append(data)
            if not hasattr(callback, 'speech_detected') and recognizer.AcceptWaveform(data.tobytes()):
                callback.speech_detected = True
                print("Speech detected! Recording...")
            return (in_data, pyaudio.paContinue)

        p = pyaudio.PyAudio()

        # Define the stream's settings
        stream_settings = {
            'format': audio_format,
            'channels': channels,
            'rate': sample_rate,
            'input': True,
            'frames_per_buffer': chunk_size,
            'stream_callback': callback
        }

        while self.isRunning():

            print("Listening for speech...")
            buffer.clear()
            self.stream = p.open(**stream_settings)
            self.stream.start_stream()
            try:
                while self.stream.is_active():
                    print("stream is active")
                    time.sleep(0.1)
                    if hasattr(callback, 'speech_detected'):
                        time.sleep(5)  # Record for 5 seconds after speech is detected.
                        break
                print("stream no longer active")
            except KeyboardInterrupt:
                print("Exiting...")
                break
            finally:
                print("we are here")
                self.stream.stop_stream()
                self.stream.close()

            print("so now we teset")
            if hasattr(callback, 'speech_detected'):
                delattr(callback, 'speech_detected')
                print("buffer len:", len(buffer))
                output_file = save_audio(buffer, sample_rate, channels)
                result = transcribe_audio(recognizer, output_file)
                if len(result)>5:
                    self.result_signal.emit(result)

    def stop(self):
        self.stream.stop_stream()
        self.stream.close()
        self.stream.terminate()
        self.stream.wait()


def save_audio(buffer, sample_rate, channels):
    output_file = "speech.wav"
    print("Finished recording. Saving audio...")

    audio_data = np.concatenate(buffer, axis=0).tobytes()
    with wave.open(output_file, 'wb') as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(2)  # 2 bytes (16 bits) per sample
        wf.setframerate(sample_rate)
        wf.writeframes(audio_data)

    print(f"Audio saved to {output_file}")
    return output_file

def transcribe_audio(recognizer, audio_file):
    use_whisper = True
    result = ''
    if use_whisper:
        wav_audio = AudioSegment.from_file(audio_file, format="wav")
        wav_filename = audio_file.replace('.wav','.mp3')
        wav_audio.export(wav_filename, format="mp3")
        transcript = openai.Audio.transcribe("whisper-1", open(wav_filename,'rb'))
        result = transcript.text
    else:
        with wave.open(audio_file, 'rb') as wf:
            audio_data = wf.readframes(wf.getnframes())
            audio_data_np = np.frombuffer(audio_data, dtype=np.int16)

        recognizer.AcceptWaveform(audio_data_np.tobytes())
        result = recognizer.Result()
    print(f"Transcription: {result}")
    return result


# Set your OpenAI API key
openai.api_key = settings.openai_key
eleven = ElevenLabs(settings.elevenapi_key)

messages = [
        {"role":"system","content":"You are wise and kind old monk handing out wisdom to fellow travellers"},
        ]

def chat_response(prompt):
    messages.append({"role":"user","content":prompt})
    response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages
    )
    messages.append(response.choices[0].message)
    return response.choices[0].message.content

# Custom QTextEdit to handle Ctrl+Enter
class CustomTextEdit(QTextEdit):

    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent

    def keyPressEvent(self, event):
        if (event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return) and event.modifiers() == Qt.ControlModifier:
            self.parent.on_button_click()
        else:
            super().keyPressEvent(event)

class ChatWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ChatGPT")
        layout = QVBoxLayout()

# Create input field, submit button, engine selector, and output field
        self.input_field = CustomTextEdit(self)
        self.submit_button = QPushButton("Submit")
        self.output_field = QTextEdit()
        self.output_field.setReadOnly(True)

        self.speak_label = QLabel("Voice")
        self.speak_option = QComboBox()
        self.speak_option.addItem("gTTS")
        self.speak_option.addItem("Eleven AI")
        self.speak = QCheckBox("Speak")
        self.listening = False
        self.listen = QCheckBox("Listen")
        self.speech_thread = SpeechRecognitionThread()
        self.listen.stateChanged.connect(self.on_listen_state_changed)

        controllers = QHBoxLayout()

# Connect the button click event to the handler function
        self.submit_button.clicked.connect(self.on_button_click)

        self.file_label = QLabel("File: ")
        self.file_text = QLineEdit()
        self.file_text.setReadOnly(True)
        self.file_button = QPushButton("Select file")
        self.file_button.clicked.connect(self.on_file_button_click)

        controllers.addWidget(self.speak_label)
        controllers.addWidget(self.speak_option)
        controllers.addWidget(self.speak)
        controllers.addWidget(self.listen)
        controllers.addWidget(self.file_label)
        controllers.addWidget(self.file_text)
        controllers.addWidget(self.file_button)
        controllers.addWidget(self.submit_button)
# Add widgets to the layout and set the layout for the window
        layout.addWidget(self.input_field)
        layout.addLayout(controllers)
        layout.addWidget(self.output_field)
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
        self.showMaximized()
        # threading.Thread(target=detect_speech_and_record, args=(self.listen.isChecked,self), daemon=True).start()

    def on_listen_state_changed(self, state):
        print(f"Listening: {state} - {Qt.Checked}")
        self.listening = self.listen.isChecked()

        if self.listening:
            print("Starting speech recognition thread")
            self.speech_thread.start()
            self.speech_thread.result_signal.connect(self.process)
        else:
            print("Stopping speech recognition thread")
            self.speech_thread.terminate()
            self.speech_thread.wait()

    def process(self, result):
        print("Processing results: ", result)
        self.input_field.setText(result)
        self.on_button_click()
        self.listen.setChecked(False)

    def on_file_button_click(self):
        file_name = QFileDialog.getOpenFileName(self, 'Open file', '/home')
        if file_name[0]:
            self.file_text.setText(file_name[0])

# Function to handle button clicks
    def on_button_click(self):
        try:
            user_input = self.input_field.toPlainText()
            prompt = f"{user_input}"

            if os.path.exists(self.file_text.text()):
                prompt += f"\nFile content: {textract.process(self.file_text.text())}"
                self.file_text.setText("")

            self.output_field.append(f"You: {user_input}\n")
            self.input_field.clear()
            response = chat_response(prompt)
            self.output_field.append(f"ChatGPT: {response}\n")
            self.output_field.append(f"---------------------------------------------------------------------------------------------------------------\n")
            print('Speak:',self.speak_option.currentText())
            if self.speak.isChecked():
                OUTPUT_PATH = "output.mp3"
                if self.speak_option.currentText() == "Eleven AI":
                    voice = eleven.voices["Bella"]
                    audio = voice.generate(response)
                    audio.save("output")
                else:
                    tts = gTTS(response, lang='en', tld='co.uk')
                    tts.save(OUTPUT_PATH)

                playsound(OUTPUT_PATH)
        except Exception as e:
            print('Error generating answer:',e)

def main():
# Create the PySide6 application
    app = QApplication(sys.argv)
    window = ChatWindow()

# Show the window and run the application
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

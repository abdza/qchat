#!/bin/env python

import os
import sys
import openai
import settings
import textract
from playsound import playsound
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QPushButton, QLineEdit, QTextEdit, QWidget, QComboBox, QHBoxLayout, QCheckBox, QLabel, QFileDialog
from PySide6.QtCore import Qt
from elevenlabs import ElevenLabs
from gtts import gTTS

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

# Function to call the OpenAI API
def generate_response(prompt, engine):
    response = openai.Completion.create(
        engine=engine,
        prompt=prompt,
        max_tokens=100,
        n=1,
        stop=None,
        temperature=0.5,
    )

    message = response.choices[0].text.strip()
    return message

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

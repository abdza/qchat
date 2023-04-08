#!/bin/env python

import sys
import openai
import settings
from playsound import playsound
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QPushButton, QLineEdit, QTextEdit, QWidget, QComboBox, QHBoxLayout, QCheckBox
from PySide6.QtCore import Qt
from elevenlabs import ElevenLabs


# Set your OpenAI API key
openai.api_key = settings.openai_key
eleven = ElevenLabs(settings.elevenapi_key)

messages = [
        {"role":"system","content":"You are a superstar programmer"},
        ]

def chat_response(prompt):
    messages.append({"role":"user","content":prompt})
    response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages
    )
    messages.append(response.choices[0].message)
    print(response)
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
        self.speak = QCheckBox("Speak")

        controllers = QHBoxLayout()

# Connect the button click event to the handler function
        self.submit_button.clicked.connect(self.on_button_click)

        controllers.addWidget(self.speak)
        controllers.addWidget(self.submit_button)
# Add widgets to the layout and set the layout for the window
        layout.addWidget(self.input_field)
        layout.addLayout(controllers)
        layout.addWidget(self.output_field)
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
        self.showMaximized()

# Function to handle button clicks
    def on_button_click(self):
        try:
            user_input = self.input_field.toPlainText()
            prompt = f"{user_input}"
            self.output_field.append(f"You: {user_input}\n")
            self.input_field.clear()
            # selected_engine = engine_selector.currentText()
            # response = generate_response(prompt, selected_engine)
            response = chat_response(prompt)
            # Append the user input and response to the output field
            self.output_field.append(f"ChatGPT: {response}\n")
            self.output_field.append(f"---------------------------------------------------------------------------------------------------------------\n")
            if self.speak.isChecked():
                print("Setting voices")
                voice = eleven.voices["Bella"]
                # Generate the TTS
                print("Generating voice")
                audio = voice.generate(response)
                print("Saving voice")
                audio.save("output")
                print("Playing voice")
                playsound("output.mp3")
                print("Done it all")
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

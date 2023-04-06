#!/bin/env python

import sys
import openai
import settings
from playsound import playsound
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QPushButton, QLineEdit, QTextEdit, QWidget, QComboBox
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
    def keyPressEvent(self, event):
        if (event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return) and event.modifiers() == Qt.ControlModifier:
            on_button_click()
        else:
            super().keyPressEvent(event)

# Function to handle button clicks
def on_button_click():
    user_input = input_field.toPlainText()
    prompt = f"{user_input}"
    output_field.append(f"You: {user_input}\n")
    input_field.clear()
    selected_engine = engine_selector.currentText()
    # response = generate_response(prompt, selected_engine)
    response = chat_response(prompt)
    output_field.append(f"ChatGPT: {response}\n")
    output_field.append(f"---------------------------------------------------------------------------------------------------------------\n")
    
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
    # Append the user input and response to the output field

# Create the PySide6 application
app = QApplication(sys.argv)
window = QMainWindow()
window.setWindowTitle("ChatGPT")
layout = QVBoxLayout()

# Create input field, submit button, engine selector, and output field
input_field = CustomTextEdit()
submit_button = QPushButton("Submit")
output_field = QTextEdit()
output_field.setReadOnly(True)

# Create a QComboBox for engine selection and add available engines
engine_selector = QComboBox()
engine_selector.addItem("gpt-4")
engine_selector.addItem("gpt-3.5-turbo")
engine_selector.addItem("davinci")
engine_selector.addItem("curie")
engine_selector.addItem("babbage")
engine_selector.addItem("ada")

# Connect the button click event to the handler function
submit_button.clicked.connect(on_button_click)

# Add widgets to the layout and set the layout for the window
layout.addWidget(input_field)
# layout.addWidget(engine_selector)
layout.addWidget(submit_button)
layout.addWidget(output_field)
central_widget = QWidget()
central_widget.setLayout(layout)
window.setCentralWidget(central_widget)

# Show the window and run the application
window.showMaximized()
sys.exit(app.exec())


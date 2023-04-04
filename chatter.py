import sys
import openai
import settings
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QPushButton, QLineEdit, QTextEdit, QWidget, QComboBox

# Set your OpenAI API key
openai.api_key = settings.openai_key

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

# Function to handle button clicks
def on_button_click():
    user_input = input_field.text()
    prompt = f"{user_input}"
    selected_engine = engine_selector.currentText()
    # response = generate_response(prompt, selected_engine)
    response = chat_response(prompt)
    
    # Append the user input and response to the output field
    output_field.append(f"You: {user_input}\nChatGPT: {response}\n")

# Create the PySide6 application
app = QApplication(sys.argv)
window = QMainWindow()
window.setWindowTitle("ChatGPT")
layout = QVBoxLayout()

# Create input field, submit button, engine selector, and output field
input_field = QLineEdit()
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
layout.addWidget(engine_selector)
layout.addWidget(submit_button)
layout.addWidget(output_field)
central_widget = QWidget()
central_widget.setLayout(layout)
window.setCentralWidget(central_widget)

# Show the window and run the application
window.show()
sys.exit(app.exec())

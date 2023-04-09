# qchat

qchat is an OpenAI API chatbot with a Qt interface.

## About

qchat is a project that uses the OpenAI API to create a friendly and intelligent chatbot. You can interact with the bot using text or voice input, and the bot will reply with text and voice output. The project uses Qt for the graphical user interface, and Eleven API for the text-to-speech and speech-to-text features.

## Installation

To install qchat, you need to have Python 3.6 or higher and pip installed on your system. Then, clone this repository and navigate to the project directory.

It is recommended to create a virtual environment for this project to avoid any conflicts with other packages. You can use the following command to create a virtual environment named `venv`:

```bash
python -m venv venv
```

Then, activate the virtual environment using the following command:

```bash
source venv/bin/activate
```

Next, install the required packages using the following command:

```bash
pip install -r requirements.txt
```

You also need to create a file named `settings.py` in the project directory and add your OpenAI API key and Eleven API key as follows:

```python
OPENAI_API_KEY = "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
ELEVEN_API_KEY = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

## Usage

To start qchat, run the following command in the project directory:

```bash
./chat.sh
```

This will launch a Qt window where you can type or speak your messages to the bot. The bot will reply with text and voice output. You can also check the box to enable voice input only.

## License

qchat is licensed under the MIT license. See the LICENSE file for more details.

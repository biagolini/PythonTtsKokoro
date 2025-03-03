# Python TTS with Kokoro-82M

This project provides a simple implementation of the Kokoro-82M text-to-speech (TTS) model, enabling users to generate high-quality speech from text in English and Portuguese. Kokoro-82M is a lightweight and efficient TTS model designed for fast speech synthesis while maintaining natural-sounding voice output.

## Features
- Converts text into high-quality speech using the Kokoro-82M model.
- Supports English and Portuguese languages.
- Provides customizable options such as voice selection and speech speed.
- Saves generated speech as `.wav` files.
- Simple and easy-to-use Python scripts for generating speech.

## Getting Started

Follow these steps to set up and use this project.

### Prerequisites

Before installing the required packages, it is recommended to update the system repositories:

```bash
sudo apt-get update && sudo apt-get upgrade -y
```

Kokoro TTS depends on `espeak-ng` for text-to-speech conversion. To install it, run:

```bash
sudo apt-get install espeak-ng -y
```

### Installation

1. **Clone the Repository**  
   Clone the project repository to your local machine:
   ```bash
   git clone https://github.com/biagolini/PythonTtsKokoro.git
   cd PythonTtsKokoro
   ```

2. **Set Up a Virtual Environment**  
   It is recommended to use a virtual environment for dependencies:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows, use venv\Scripts\activate
   ```

3. **Install Dependencies**  
   Install the required libraries using `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```

### Usage

You can generate speech from text using the provided Python scripts.


To generate English speech, run:
```bash
python en.py
```

To generate Portuguese speech, run:

```bash
python pt.py
```

### Output Files
The generated speech files will be stored in the `output` directory, named sequentially (e.g., `en_0.wav`, `pt_0.wav`).



## Contributing

Feel free to submit issues, create pull requests, or fork the repository to help improve the project.

## License and Disclaimer

This project is open-source and distributed under the Apache License. For detailed licensing information, please refer to the official Kokoro-82M repository at: [Kokoro-82M Hugging Face](https://huggingface.co/hexgrad/Kokoro-82M).


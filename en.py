from kokoro import KPipeline  # Import the Kokoro-82M text-to-speech pipeline
from IPython.display import display, Audio  # For displaying audio output in Jupyter notebooks
import soundfile as sf  # Library for saving audio files
import os  # Standard library for handling file system operations

# Define the output folder where generated audio files will be saved
output_folder = 'output'

# Check if the output folder exists, if not, create it
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Initialize the Kokoro-82M pipeline with English language support ('a' represents English)
pipeline = KPipeline(lang_code='a') 

# Define the input text that will be converted to speech
text = '''
Hello and welcome! In this tutorial, we will explore how to use Kokoro-82M! 
'''

# Generate speech using the pipeline with specific parameters:
# - voice='af_heart': Specifies the voice model to use
# - speed=1: Normal speech speed
# - split_pattern=r'\n+': Splits text based on new lines
generator = pipeline(
    text, 
    voice='af_heart', 
    speed=1, 
    split_pattern=r'\n+'
)

# Iterate through the generated speech outputs
for i, (gs, ps, audio) in enumerate(generator):
    # Save each generated audio file in the output folder with a unique name
    sf.write(f'{output_folder}/en_{i}.wav', audio, 24000)  # 24kHz sample rate
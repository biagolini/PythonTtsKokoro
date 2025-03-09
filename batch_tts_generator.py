import warnings  # Suppress warnings
from kokoro import KPipeline  # Import Kokoro-82M TTS pipeline
from pydub import AudioSegment  # Library for audio processing
import numpy as np  # Library for handling arrays
import os  # Standard library for file system operations
import glob  # Used to list files in a directory

# Suppress specific warnings
warnings.simplefilter('ignore', UserWarning)
warnings.simplefilter('ignore', FutureWarning)

# Define input and output folders
input_folder = 'input'
output_folder = 'output'

# Define the gap between audio segments (in seconds)
audio_gap_seconds = 0.30  

# Ensure the output folder exists; create it if not
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Initialize the Kokoro-82M pipeline with English language support
pipeline = KPipeline(lang_code='a', repo_id='hexgrad/Kokoro-82M')

# Get a sorted list of all .txt files in the input folder
text_files = sorted(glob.glob(f"{input_folder}/*.txt"))

# List to store the final MP3 file names and durations
mp3_files_info = []

# Process each text file
for text_file in text_files:
    file_prefix = os.path.splitext(os.path.basename(text_file))[0]  # Extract filename without extension

    # Read the text content from the file
    with open(text_file, "r", encoding="utf-8") as file:
        text = file.read()

    # Generate speech using the pipeline
    generator = pipeline(
        text,
        voice='af_heart',  # Best American voices: F = af_heart; M = am_michael
        speed=1,
        split_pattern=r'\n+'
    )

    # Initialize an empty audio segment to store the combined output
    combined_audio = AudioSegment.silent(duration=0)

    # Create a silent segment for spacing between audios
    silence_segment = AudioSegment.silent(duration=audio_gap_seconds * 1000)  # Convert seconds to milliseconds

    # List to store generated .wav files for later removal
    generated_wav_files = []

    # Iterate through generated speech outputs
    for i, (gs, ps, audio) in enumerate(generator):
        # Convert the numpy array to the correct format for pydub
        audio = np.array(audio) * 32767  # Convert to int16 range
        audio = audio.astype(np.int16)

        # Create an AudioSegment object from the audio data
        audio_segment = AudioSegment(
            audio.tobytes(),
            frame_rate=24000,  # 24kHz sample rate
            sample_width=audio.dtype.itemsize,
            channels=1
        )

        # Temporarily save the WAV file before merging
        wav_file = f"{output_folder}/{file_prefix}_{i}.wav"
        audio_segment.export(wav_file, format="wav")
        generated_wav_files.append(wav_file)

        # Append the generated audio to the combined track, including the silence segment
        combined_audio += audio_segment + silence_segment

    # Check if any audio was generated for this text file
    if len(combined_audio) > 0:
        # Define the final MP3 file name
        final_mp3_path = f"{output_folder}/{file_prefix}.mp3"

        # Export the final compiled audio to MP3
        combined_audio.export(final_mp3_path, format="mp3", bitrate="192k")
        print(f'Compiled audio file generated: {final_mp3_path}')

        # Get the duration in seconds
        duration_seconds = len(combined_audio) / 1000  # Convert milliseconds to seconds

        # Store file info
        mp3_files_info.append(f"{file_prefix}.mp3 - {duration_seconds:.2f}")

        # Remove intermediate WAV files
        for wav_file in generated_wav_files:
            os.remove(wav_file)
            print(f"Removed: {wav_file}")

# Save the MP3 files info to a text file
output_txt_path = os.path.join(output_folder, "mp3_files_info.txt")
with open(output_txt_path, "w", encoding="utf-8") as txt_file:
    txt_file.write("\n".join(mp3_files_info))

print(f"MP3 files information saved to: {output_txt_path}")

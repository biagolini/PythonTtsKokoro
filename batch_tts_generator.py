import warnings
import json
from kokoro import KPipeline
from pydub import AudioSegment
import numpy as np
import os
import glob

warnings.simplefilter('ignore', UserWarning)
warnings.simplefilter('ignore', FutureWarning)

# Define input and output folders
input_folder = 'input'
output_folder = 'output'

# Define the gap between audio segments (in seconds)
audio_gap_seconds = 0.30

# Ensure the output folder exists
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Language setting (set to "by_folder" to use subdirectories under input/)
selected_language = "by_folder"  # Can be "en", "es", "pt", or "by_folder"

# Load language configurations from JSON file
with open("default_configs.json", "r", encoding="utf-8") as json_file:
    lang_configs = json.load(json_file)

# List to store final MP3 file names and durations
mp3_files_info = []

def process_language_folder(language_key, language_input_path, language_output_path):
    """Process all text files in a language-specific folder."""
    language_settings = lang_configs.get(language_key, lang_configs.get("en"))
    lang_code = language_settings["lang_code"]
    voice = language_settings["voice"]

    pipeline = KPipeline(lang_code=lang_code, repo_id='hexgrad/Kokoro-82M')

    # Find all .txt files in the specific language input folder
    text_files = sorted(glob.glob(f"{language_input_path}/*.txt"))
    
    for text_file in text_files:
        file_prefix = os.path.splitext(os.path.basename(text_file))[0]

        with open(text_file, "r", encoding="utf-8") as file:
            text = file.read()

        generator = pipeline(
            text,
            voice=voice,
            speed=1,
            split_pattern=r'\n+'
        )

        combined_audio = AudioSegment.silent(duration=0)
        silence_segment = AudioSegment.silent(duration=audio_gap_seconds * 1000)

        generated_wav_files = []

        for i, (gs, ps, audio) in enumerate(generator):
            audio = np.array(audio) * 32767
            audio = audio.astype(np.int16)

            audio_segment = AudioSegment(
                audio.tobytes(),
                frame_rate=24000,
                sample_width=audio.dtype.itemsize,
                channels=1
            )

            wav_file = f"{language_output_path}/{file_prefix}_{i}.wav"
            audio_segment.export(wav_file, format="wav")
            generated_wav_files.append(wav_file)

            combined_audio += audio_segment + silence_segment

        if len(combined_audio) > 0:
            final_mp3_path = f"{language_output_path}/{file_prefix}.mp3"
            combined_audio.export(final_mp3_path, format="mp3", bitrate="192k")
            print(f'Compiled audio file generated: {final_mp3_path}')

            duration_seconds = len(combined_audio) / 1000
            mp3_files_info.append(f"{language_key}/{file_prefix}.mp3 - {duration_seconds:.2f}")

            for wav_file in generated_wav_files:
                os.remove(wav_file)
                print(f"Removed: {wav_file}")

# Determine execution mode
if selected_language == "by_folder":
    subfolders = [d for d in os.listdir(input_folder) if os.path.isdir(os.path.join(input_folder, d))]

    for lang_key in subfolders:
        input_lang_path = os.path.join(input_folder, lang_key)
        output_lang_path = os.path.join(output_folder, lang_key)

        if not os.path.exists(output_lang_path):
            os.makedirs(output_lang_path)

        print(f"Processing language folder: {lang_key}")
        process_language_folder(lang_key, input_lang_path, output_lang_path)
else:
    # Fallback to single language mode
    language_settings = lang_configs.get(selected_language, lang_configs["en"])
    lang_code = language_settings["lang_code"]
    voice = language_settings["voice"]

    pipeline = KPipeline(lang_code=lang_code, repo_id='hexgrad/Kokoro-82M')
    text_files = sorted(glob.glob(f"{input_folder}/*.txt"))

    for text_file in text_files:
        file_prefix = os.path.splitext(os.path.basename(text_file))[0]

        with open(text_file, "r", encoding="utf-8") as file:
            text = file.read()

        generator = pipeline(
            text,
            voice=voice,
            speed=1,
            split_pattern=r'\n+'
        )

        combined_audio = AudioSegment.silent(duration=0)
        silence_segment = AudioSegment.silent(duration=audio_gap_seconds * 1000)
        generated_wav_files = []

        for i, (gs, ps, audio) in enumerate(generator):
            audio = np.array(audio) * 32767
            audio = audio.astype(np.int16)

            audio_segment = AudioSegment(
                audio.tobytes(),
                frame_rate=24000,
                sample_width=audio.dtype.itemsize,
                channels=1
            )

            wav_file = f"{output_folder}/{file_prefix}_{i}.wav"
            audio_segment.export(wav_file, format="wav")
            generated_wav_files.append(wav_file)

            combined_audio += audio_segment + silence_segment

        if len(combined_audio) > 0:
            final_mp3_path = f"{output_folder}/{file_prefix}.mp3"
            combined_audio.export(final_mp3_path, format="mp3", bitrate="192k")
            print(f'Compiled audio file generated: {final_mp3_path}')

            duration_seconds = len(combined_audio) / 1000
            mp3_files_info.append(f"{file_prefix}.mp3 - {duration_seconds:.2f}")

            for wav_file in generated_wav_files:
                os.remove(wav_file)
                print(f"Removed: {wav_file}")

# Save the MP3 files info to a text file
output_txt_path = os.path.join(output_folder, "mp3_files_info.txt")
with open(output_txt_path, "w", encoding="utf-8") as txt_file:
    txt_file.write("\n".join(mp3_files_info))

print(f"MP3 files information saved to: {output_txt_path}")

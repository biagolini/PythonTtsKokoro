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

# Define output audio format: "wav" or "mp3"
output_audio_format = "mp3"  # default to mp3

# Ensure the output folder exists
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Language setting
selected_language = "by_folder"  # "en", "es", "pt" ou "by_folder"

# Load language configurations
print("Loading language configurations...")
with open("default_configs.json", "r", encoding="utf-8") as json_file:
    lang_configs = json.load(json_file)

print(f"Loaded configurations: {lang_configs}")

# List to store MP3/WAV file information
audio_files_info = []

def process_language_folder(language_key, language_input_path, language_output_path):
    print(f"Processing folder for language key: {language_key}")
    
    language_settings = lang_configs.get(language_key, lang_configs.get("pt"))
    lang_code = language_settings["lang_code"]
    voice = language_settings["voice"]

    print(f"Using language code '{lang_code}' and voice '{voice}'")

    pipeline = KPipeline(lang_code=lang_code, repo_id='hexgrad/Kokoro-82M')

    text_files = sorted(glob.glob(f"{language_input_path}/*.txt"))
    print(f"Found {len(text_files)} text files: {text_files}")
    
    for text_file in text_files:
        file_prefix = os.path.splitext(os.path.basename(text_file))[0]
        print(f"Processing file: {text_file} (prefix: {file_prefix})")

        with open(text_file, "r", encoding="utf-8") as file:
            text = file.read()
        print(f"Text content loaded ({len(text)} characters)")

        generator = pipeline(
            text,
            voice=voice,
            speed=1,
            split_pattern=r'\n+'
        )
        print("Generator created.")

        combined_audio = AudioSegment.silent(duration=0)
        silence_segment = AudioSegment.silent(duration=audio_gap_seconds * 1000)
        generated_wav_files = []

        segment_count = 0
        for i, (gs, ps, audio) in enumerate(generator):
            segment_count += 1
            print(f"Processing audio segment {i}")

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
            print(f"Exported WAV: {wav_file}")
            generated_wav_files.append(wav_file)

            combined_audio += audio_segment + silence_segment

        print(f"Total segments processed: {segment_count}")

        if len(combined_audio) > 0:
            final_audio_path = f"{language_output_path}/{file_prefix}.{output_audio_format}"
            combined_audio.export(final_audio_path, format=output_audio_format, bitrate="192k" if output_audio_format == "mp3" else None)
            print(f"Compiled audio generated: {final_audio_path}")

            duration_seconds = len(combined_audio) / 1000
            audio_files_info.append(f"{language_key}/{file_prefix}.{output_audio_format} - {duration_seconds:.2f}")

            for wav_file in generated_wav_files:
                os.remove(wav_file)
                print(f"Removed temporary WAV file: {wav_file}")
        else:
            print(f"No audio segments generated for file {text_file}.")

# Determine execution mode
if selected_language == "by_folder":
    print("Running in 'by_folder' mode...")
    subfolders = [d for d in os.listdir(input_folder) if os.path.isdir(os.path.join(input_folder, d))]

    if not subfolders:
        print("[WARNING] No language subfolders found in the 'input/' directory.")
        print("To use 'by_folder' mode, create subdirectories inside 'input/' named according to language keys (e.g., 'pt', 'en', 'es').")
        print("Each subdirectory must contain the corresponding .txt files to be processed.")
    else:
        for lang_key in subfolders:
            input_lang_path = os.path.join(input_folder, lang_key)
            output_lang_path = os.path.join(output_folder, lang_key)

            if not os.path.exists(output_lang_path):
                os.makedirs(output_lang_path)

            process_language_folder(lang_key, input_lang_path, output_lang_path)
else:
    print(f"Running in single language mode: {selected_language}")
    language_settings = lang_configs.get(selected_language, lang_configs["en"])
    lang_code = language_settings["lang_code"]
    voice = language_settings["voice"]

    pipeline = KPipeline(lang_code=lang_code, repo_id='hexgrad/Kokoro-82M')
    text_files = sorted(glob.glob(f"{input_folder}/*.txt"))
    print(f"Found {len(text_files)} text files.")

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
            final_audio_path = f"{output_folder}/{file_prefix}.{output_audio_format}"
            combined_audio.export(final_audio_path, format=output_audio_format, bitrate="192k" if output_audio_format == "mp3" else None)
            print(f"Compiled audio generated: {final_audio_path}")

            duration_seconds = len(combined_audio) / 1000
            audio_files_info.append(f"{file_prefix}.{output_audio_format} - {duration_seconds:.2f}")

            for wav_file in generated_wav_files:
                os.remove(wav_file)
                print(f"Removed temporary WAV file: {wav_file}")

# Save the audio files info
output_txt_path = os.path.join(output_folder, "audio_files_info.txt")
with open(output_txt_path, "w", encoding="utf-8") as txt_file:
    txt_file.write("\n".join(audio_files_info))

print(f"Audio files information saved to: {output_txt_path}")
print("Processing complete.")

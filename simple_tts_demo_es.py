import os
import soundfile as sf
from IPython.display import Audio, display
from kokoro import KPipeline

output_folder = 'output'

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

pipeline = KPipeline(lang_code='e')

text = '''
Hola y bienvenido! En este tutorial, exploraremos cómo utilizar el Kokoro-82M!
'''

generator = pipeline(
    text, 
    voice='ef_dora', 
    speed=1, split_pattern=r'\n+'
)

for i, (gs, ps, audio) in enumerate(generator):
    sf.write(f'{output_folder}/es_{i}.wav', audio, 24000) 



import whisper
import os
import subprocess
import argparse
from urllib.parse import urlparse
from colorama import Fore, init
import asyncio

# Initialize colorama
init(autoreset=True)

# Function to check if the given path is a URL
def is_url(path):
    try:
        result = urlparse(path)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

radios = {
    'SAN': {
        'Ground': 'http://d.liveatc.net/ksan1_gnd',
        'Tower': 'http://d.liveatc.net/ksan1_twr',
        'Departure': 'http://d.liveatc.net/ksan_dep_125150',
    }
}

async def transcribe_stream(stream_url):
    model = whisper.load_model("base")

    # Create a directory to store audio chunks
    if not os.path.exists("chunks"):
        os.makedirs("chunks")

    chunk_index = 0
    while True:
        chunk_path = f"chunks/output{chunk_index:03d}.wav"

        # Use FFmpeg to record the stream for 15 seconds
        print(f"{Fore.LIGHTBLUE_EX}Recording chunk...")
        ffmpeg_command = [
            'ffmpeg', '-y', '-loglevel', 'panic', '-i', stream_url, '-t', '15',
            '-c', 'copy', chunk_path
        ]

        try:
            subprocess.run(ffmpeg_command, stderr=subprocess.STDOUT, check=True)
            print(f"{Fore.LIGHTBLUE_EX}Chunk recorded.")
        except subprocess.CalledProcessError as e:
            print(f"{Fore.RED}Error recording chunk: {e}")
            continue

        # Transcribe the chunk
        try:
            print(f"{Fore.YELLOW}Transcribing chunk...")
            result = model.transcribe(chunk_path)
            transcription = result['text']
            print(f"{Fore.GREEN}{transcription}")
        except Exception as e:
            print(f"{Fore.RED}Error transcribing chunk: {e}")
            continue

        # Delete the chunk after processing
        try:
            os.remove(chunk_path)
        except OSError as e:
            print(f"{Fore.RED}Error deleting chunk: {e}")

        chunk_index += 1

def transcribe_file(file_path):
    model = whisper.load_model("base")

    if not os.path.exists(file_path):
        print(f"{Fore.RED}File {file_path} does not exist.")
        return

    print(f"{Fore.YELLOW}Transcribing file: {file_path}")
    result = model.transcribe(file_path)
    print(f"{Fore.GREEN}{result['text']}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Transcribe audio from a file or URL.")
    parser.add_argument("source", nargs="?", help="URL of the audio stream or path to the audio file")

    args = parser.parse_args()
    source = args.source

    if source:
        if is_url(source):
            print(f"{Fore.CYAN}Starting transcription for stream URL: {source}")
            asyncio.run(transcribe_stream(source))
        else:
            print(f"{Fore.CYAN}Starting transcription for file: {source}")
            transcribe_file(source)
    else:
        print(f"{Fore.RED}No source provided. Please provide a URL or file path.")

import whisper
import sys
import os
import subprocess
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

def transcribe_chunk(model, chunk_path):
    print(f"{Fore.YELLOW}Transcribing chunk: {chunk_path}")
    result = model.transcribe(chunk_path)
    transcription = result['text']
    print(f"{Fore.GREEN}Transcription: {transcription}")
    sys.stdout.flush()  # Ensure the output is immediately flushed
    return transcription

def transcribe_audio_from_stream(stream_url):
    model = whisper.load_model("base")

    # Create a directory to store audio chunks
    if not os.path.exists("chunks"):
        os.makedirs("chunks")

    chunk_index = 0
    while True:
        chunk_path = f"chunks/output{chunk_index:03d}.wav"
        
        # Use FFmpeg to record the stream for 30 seconds
        print(f"{Fore.BLUE}Recording chunk {chunk_index}...")
        ffmpeg_command = [
            'ffmpeg', '-y', '-i', stream_url, '-t', '30',
            '-c', 'copy', chunk_path
        ]
        
        subprocess.run(ffmpeg_command, stderr=subprocess.STDOUT)
        print(f"{Fore.BLUE}Chunk {chunk_index} recorded.")
        
        # Transcribe the chunk
        transcription = transcribe_chunk(model, chunk_path)
        
        # Send the transcription to stdout
        print(transcription)
        
        chunk_index += 1

def transcribe_audio_from_file(file_path):
    if not os.path.exists(file_path):
        print(f"{Fore.RED}File {file_path} does not exist.")
        return
    
    print(f"{Fore.YELLOW}Transcribing file: {file_path}")
    model = whisper.load_model("base")
    result = model.transcribe(file_path)
    print(f"{Fore.GREEN}Transcription: {result['text']}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if os.path.isfile(arg):
            # Test mode with local file
            transcribe_audio_from_file(arg)
        else:
            # Live transcription mode with URL
            transcribe_audio_from_stream(arg)
    else:
        print(f"{Fore.RED}Please provide a stream URL or a local file path as an argument.")

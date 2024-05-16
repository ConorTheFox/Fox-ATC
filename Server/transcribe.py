import whisper
import os
import subprocess
import json
import asyncio
import websockets
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

radios = {
    'SAN': {
        'Ground': 'http://d.liveatc.net/ksan1_gnd',
        'Tower': 'http://d.liveatc.net/ksan1_twr',
        'Departure': 'http://d.liveatc.net/ksan_dep_125150',
    }
}

async def transcribe_and_send(stream_url, websocket):
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
        print(f"{Fore.YELLOW}Transcribing chunk: {chunk_path}")
        result = model.transcribe(chunk_path)
        transcription = result['text']
        print(f"{Fore.GREEN}Transcription: {transcription}")

        # Send the transcription to the client
        await websocket.send(transcription)

        chunk_index += 1

async def handle_client(websocket, path):
    async for message in websocket:
        data = json.loads(message)
        airport_code = data.get('airport_code')
        frequency = data.get('frequency')

        stream_url = radios[airport_code][frequency]
        await transcribe_and_send(stream_url, websocket)

async def main():
    async with websockets.serve(handle_client, "localhost", 3000):
        print("WebSocket server running on ws://localhost:3000")
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())

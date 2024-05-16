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

        # Use FFmpeg to record the stream for 15 seconds
        print(f"{Fore.BLUE}Recording chunk {chunk_index}...")
        ffmpeg_command = [
            'ffmpeg', '-y', '-i', stream_url, '-t', '15',
            '-c', 'copy', chunk_path
        ]

        try:
            subprocess.run(ffmpeg_command, stderr=subprocess.STDOUT)
            print(f"{Fore.BLUE}Chunk {chunk_index} recorded.")
        except Exception as e:
            print(f"{Fore.RED}Error recording chunk: {e}")
            await websocket.send(f"Error recording chunk: {e}")
            break

        # Transcribe the chunk
        try:
            print(f"{Fore.YELLOW}Transcribing chunk: {chunk_path}")
            result = model.transcribe(chunk_path)
            transcription = result['text']
            print(f"{Fore.GREEN}Transcription: {transcription}")

            # Send the transcription to the client
            await websocket.send(transcription)
        except Exception as e:
            print(f"{Fore.RED}Error transcribing chunk: {e}")
            await websocket.send(f"Error transcribing chunk: {e}")
            break

        chunk_index += 1

async def handle_client(websocket, path):
    print(f"{Fore.GREEN}Client connected")
    try:
        async for message in websocket:
            print(f"{Fore.YELLOW}Received message: {message}")
            data = json.loads(message)
            airport_code = data.get('airport_code')
            frequency = data.get('frequency')

            stream_url = radios[airport_code][frequency]
            await transcribe_and_send(stream_url, websocket)
    except websockets.exceptions.ConnectionClosed as e:
        print(f"{Fore.RED}Connection closed: {e}")

async def main():
    async with websockets.serve(handle_client, "localhost", 3000):
        print("WebSocket server running on ws://localhost:3000")
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())

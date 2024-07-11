"""
Input: WebSocket data
Output: PiCamera video
Behavior:
  - Record video with PiCamera.
  - Save with timestamp filename.
  - Record at fixed intervals.
"""

import asyncio, json, os
import websockets.client as websockets
from time import time
from datetime import datetime as dt

from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
from picamera2.outputs import FfmpegOutput

from communication.message import ClientToServer as WebsocketMsg

NAME = "picam_record.py"
# ================================================================#

VIDEO_DURATION = 60  # seconds
MAX_VIDEO_COUNT = 100
started = False
stopped = True


def picam_init():
    picam2 = Picamera2()
    picam2.configure(
        picam2.create_video_configuration(
            main={"size": (1280, 720), "format": "RGB888"},
            lores={"size": (320, 240), "format": "YUV420"},
            display="lores",
            encode="lores",
        )
    )
    encoder = H264Encoder(
        bitrate=None,
        framerate=30,
    )
    encoder.output = FfmpegOutput("./videos/temp.mp4")
    return picam2, encoder


# ================================================================#


async def record_loop():
    global started, stopped
    encoding = False

    picam2.start_encoder(encoder)
    picam2.start()
    started = True
    start_time = time()

    try:
        while started and not stopped:
            if not encoding:
                # Start write frames to file
                encoder.output.output_filename = (
                    f"./videos/{dt.now().strftime('%Y%m%d_%H:%M:%S')}.mp4"
                )
                encoder.output.start()
                encoding = True
                start_time = time()
                print(f"Saving video: {encoder.output.output_filename}")
                check_video_count()

            elif encoding and time() - start_time > VIDEO_DURATION:
                # Save video if duration is reached
                encoder.output.stop()
                encoding = False

            await asyncio.sleep(0.5)

    except Exception as e:
        print(f"Error in [ record_loop() ] : {e}")

    finally:
        picam2.stop()
        picam2.stop_encoder()
        stopped = True
        print(f"Recording stopped")


# =================================================================#


def check_video_count(should_delete=True):
    videos = [f for f in os.listdir("./videos/") if f.endswith(".mp4")]
    if len(videos) > MAX_VIDEO_COUNT and should_delete:
        print(f"Max video count reached ({MAX_VIDEO_COUNT}). Deleting oldest video...")
        delete_oldest_video(videos)
    return len(videos)

def delete_oldest_video(videos_name: list):
    oldest_video = min(['./videos/' + name for name in videos_name], key=os.path.getatime)
    os.remove(f"{oldest_video}")
    print(f"Deleted video: {oldest_video}")

async def main():
    global started, stopped
    async with websockets.connect("ws://localhost:8000") as ws:
        await ws.send(WebsocketMsg(NAME, "Hello").to_json())
        print(f"Connected to server")
        print(f"Video duration: {VIDEO_DURATION} sec")
        print(f"Max video count: {MAX_VIDEO_COUNT}")
        print(f"Current video count: {check_video_count(False)}")
        
        try:
            async for message in ws:
                try:
                    message = json.loads(message)
                    status = message['status']
                    data = message['data']
                except Exception:
                    print('Invalid data from webSocket')
                    continue
                print(f"From server <- {message}")

                if data == "go" and stopped:
                    stopped = False
                    print(f'To server -> {WebsocketMsg(NAME, "Starting recording").show()}')
                    await ws.send(WebsocketMsg(NAME, "Starting recording").to_json())
                    asyncio.create_task(record_loop())

                elif data == "stop" and started:
                    started = False
                    print(f'To server -> {WebsocketMsg(NAME, "Stopping recording").show()}')
                    await ws.send(WebsocketMsg(NAME, "Stopping recording").to_json())

        except Exception as e:
            print(f"Error in [ main() ] : {e}")
    print('Connection closed.')


if __name__ == "__main__":
    picam2, encoder = picam_init()
    asyncio.run(main())

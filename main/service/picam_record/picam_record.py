import asyncio
import websockets.client as websockets
from time import time
from datetime import datetime as dt

from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
from picamera2.outputs import FfmpegOutput

class ProgramExit(Exception): pass

#================================================================#

VIDEO_DURATION = 60 # seconds
started = False
stopped = True

def picam_init():
    picam2 = Picamera2()
    picam2.configure(
        picam2.create_video_configuration(
            main  = {"size": (1280, 720), "format": "RGB888"},
            lores = {"size": (320, 240),  "format": "YUV420"},
            display = 'lores',
            encode = 'lores'
        ))
    encoder = H264Encoder(
        bitrate = None,
        framerate = 30,
        )
    encoder.output = FfmpegOutput('./videos/temp.mp4')
    return picam2, encoder

#================================================================#

async def record_loop():
    global started, stopped
    encoding = False

    picam2.start_encoder(encoder)
    picam2.start()
    started = True

    try:
        while started and not stopped:
            if not encoding:
                # Start write frames to file
                encoder.output.output_filename = f"./videos/{dt.now().strftime('%Y%m%d_%H:%M:%S')}.mp4"
                encoder.output.start()
                encoding = True
                start_time = time()
                print(f'Saving video: {encoder.output.output_filename}')

            elif encoding and time() - start_time > VIDEO_DURATION:
                # Save video if duration is reached
                encoder.output.stop()
                encoding = False
                
            await asyncio.sleep(0.5)

    except Exception as e:
        print(f'Error in [ __record_loop() ] : {e}')

    finally:
        picam2.stop()
        picam2.stop_encoder()
        stopped = True
        print(f'Recording stopped')

#=================================================================#

async def main():
    global started, stopped
    async with websockets.connect("ws://localhost:8000") as ws:
        await ws.send('[ picam_record.py ] : Hello')

        try:
            async for message in ws:
                print(f"From server <- {message}")

                if message == 'go' and stopped:
                    stopped = False
                    print(f'To server -> [ picam_record.py ] : Starting recording')
                    await ws.send('[ picam_record.py ] : Starting recording')
                    asyncio.create_task(record_loop())
                    
                elif message == 'stop' and started:
                    started = False
                    print(f'To server -> [ picam_record.py ] : Stopping recording')
                    await ws.send('[ picam_record.py ] : Stopping recording')

        except Exception as e:
            print(f"Error in [ main() ] : {e}")


if __name__ == '__main__':
    picam2, encoder = picam_init()
    asyncio.run(main())

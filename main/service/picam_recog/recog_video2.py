import argparse
import cv2
import numpy as np
import tflite_runtime.interpreter as tflite
from picamera2 import MappedArray, Picamera2
from picamera2.encoders import H264Encoder
from picamera2.outputs import FfmpegOutput
import asyncio
import websockets.client as websockets
from communication.message import ClientToServer as WebsocketMsg
# from pycoral.utils import edgetpu
# from pycoral.utils import dataset
# from pycoral.adapters import common
# from pycoral.adapters import classify
import time
import csv
from datetime import datetime
import os

normalSize = (720, 480)  
lowresSize = (320, 240)

rectangles = []
Detectnum = 0
IsSteady = False
already_up = False
already_down = False
Nothingnum = 0
NAME = 'picam_recog.py'
modelPath = "./model/model2.tflite"
labelPath = "./model/label_map.pbtxt"
outputName = "output.jpg"
should_stop = True

fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = None  
command_history = []

def picam_init():
    picam2 = Picamera2()
    vidConf = picam2.create_video_configuration(
        main={"size": (1280, 720), "format": "RGB888"},
        lores={"size": (320, 240), "format": "YUV420"},
        display="lores",
        encode="lores",
    )
    picam2.configure(vidConf)
    encoder = H264Encoder(bitrate=None, framerate=30)
    encoder.output = FfmpegOutput("./videos/temp.mp4")
    return picam2, encoder, vidConf

def save_command_history_to_csv(filename='command_history.csv'):

    filename = os.path.expanduser(filename)

    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)

        writer.writerow(["Command", "Timestamp", "Coordinates"])

        for command, timestamp, coordinates in command_history:

            if isinstance(timestamp, str):
                try:
                    timestamp = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    print(f"Timestamp format error for command '{command}': {timestamp}")
                    continue  
            
            # formatted_timestamp = timestamp.strftime('%Y-%m-%d %H:%M:%S')
            formatted_timestamp = timestamp
            writer.writerow([command, formatted_timestamp, coordinates])

    print(f"Command history saved to {filename}")


def ReadLabelFile(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()
    ret = {}
    for line in lines:
        pair = line.strip().split(maxsplit=1)
        ret[int(pair[0])] = pair[1].strip()
    return ret

def DrawRectangles(request):
    with MappedArray(request, "main") as m:
        for rect in rectangles:
            if len(rect) == 4:  
                rect_start = (int(rect[0] * normalSize[0] / 320) - 5, int(rect[1] * normalSize[1] / 240) - 5)
                rect_end = (int(rect[2] * normalSize[0] / 320) + 5, int(rect[3] * normalSize[1] / 240) + 5)
                cv2.rectangle(m.array, rect_start, rect_end, (0, 255, 0, 255), 2)
            else:
                print("Invalid rectangle:", rect)

async def InferenceTensorFlow(ws, result, image, model, output, label=None):
    global rectangles, Detectnum ,Nothingnum, command_history
    if label:
        labels = ReadLabelFile(label)
    else:
        labels = None
    
    start_time = time.time()
    interpreter = tflite.Interpreter(model_path=model, num_threads=4)
    interpreter.allocate_tensors()

    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    height = input_details[0]['shape'][1]
    width = input_details[0]['shape'][2]
    floating_model = False
    if input_details[0]['dtype'] == np.float32:
        floating_model = True

    rgb = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
    picture = cv2.resize(rgb, (width, height)) 

    input_data = np.expand_dims(picture, axis=0)
    if floating_model:
        input_data = (np.float32(input_data) - 127.5) / 127.5

    interpreter.set_tensor(input_details[0]['index'], input_data)
    interpreter.invoke()

    detected_boxes = interpreter.get_tensor(output_details[1]['index'])
    detected_classes = interpreter.get_tensor(output_details[3]['index'])
    detected_scores = interpreter.get_tensor(output_details[0]['index'])
    num_boxes = interpreter.get_tensor(output_details[2]['index'])

    num_boxes = int(num_boxes[0])
    print("new detect")
    
    for i in range(num_boxes):
        box = detected_boxes[0][i]
        top, left, bottom, right = box
        classId = int(detected_classes[0][i])
        score = detected_scores[0][i]
        Nothingnum += 1
        if score > 0.7:
            Detectnum += 1
            Nothingnum -= 10
            ymin = top * normalSize[1]
            xmin = left * normalSize[0]
            ymax = bottom * normalSize[1]
            xmax = right * normalSize[0]

            if labels:
                print(f"  Label: {labels[classId]}, Score = {score}")
                result.label = labels[classId]
                result.score = score
                if out is not None:
                    current_time = datetime.now()
                    # formatted_time = current_time.strftime('%Y-%m-%d %H:%M:%S')
                    formatted_time = current_time
                    cv2.putText(image, f'Time: {formatted_time}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                    cv2.rectangle(image, (int(xmin), int(ymin)), (int(xmax), int(ymax)), (0, 255, 0), 2)
                    cv2.putText(image, f"{labels[classId]}: {score:.2f}", (int(xmin), int(ymin)-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2) 
            else:
                print(f"  Score = {score}")
                result.score = score
            print(f"  Coordinates in pixels: xmin = {xmin:.1f}, ymin = {ymin:.1f}, xmax = {xmax:.1f}, ymax = {ymax:.1f}")
            result.xmin, result.ymin = f"{xmin:.1f}", f"{ymin:.1f}"
            result.xmax, result.ymax = f"{xmax:.1f}", f"{ymax:.1f}"

            rectangles.append([xmin, ymin, xmax, ymax])
    
    print(f"Detectnum:{Detectnum}")
    print(f"Nothingnum:{Nothingnum}")
    if Nothingnum >= 29:
        print("Nothing R2")
        await ws.send(WebsocketMsg(NAME, {"toSerial":
            [ord("R"), ord("2"), 0, 0]}).to_json())
        await asyncio.sleep(0.1)
        Nothingnum = 0

    if Detectnum >= 1:
        await resultforControl(ws)
        Detectnum = 0
        rectangles = []
    else:
        print("controlFun not implemented")
    
    end_time = time.time()
    processing_time = end_time - start_time
    print(f"模型辨識時間: {processing_time:.4f} seconds")
    return rgb  

async def resultforControl(ws):
    Xmin = 0
    Ymin = 0
    Xmax = 0
    Ymax = 0
    global IsSteady, already_up, already_down, command_history
    for i in range(len(rectangles)):
        Xmin += rectangles[i][0]
        Ymin += rectangles[i][1]
        Xmax += rectangles[i][2]
        Ymax += rectangles[i][3]
    if len(rectangles) > 0:
        Xmin = Xmin / len(rectangles)
        Ymin = Ymin / len(rectangles)
        Xmax = Xmax / len(rectangles)
        Ymax = Ymax / len(rectangles)
    Xmid = (Xmin + Xmax) / 2
    Ymid = (Ymin + Ymax) / 2
    
    current_time = datetime.now()
    # formatted_time = current_time.strftime('%Y-%m-%d %H:%M:%S')
    formatted_time = current_time
    coordinates_message = f"X:{Xmin}~{Xmax}；Y:{Ymin}~{Ymax}"
    X_steadyzone_min = 280
    X_steadyzone_max = 440
    Y_steadyzone_min = 180
    Y_steadyzone_max = 300

    x_adjusted = False
    if Xmid < X_steadyzone_min: 
        print("L")
        IsSteady = False
        await ws.send(WebsocketMsg(NAME, {"toSerial":
            [ord("L"), ord("1"), 0, 0]}).to_json())
        command_history.append(("L", formatted_time, coordinates_message))
        await asyncio.sleep(0.1)
        x_adjusted = True
    elif Xmid > X_steadyzone_max: 
        print("R")
        IsSteady = False
        await ws.send(WebsocketMsg(NAME, {"toSerial":
            [ord("R"), ord("1"), 0, 0]}).to_json())
        command_history.append(("R", formatted_time, coordinates_message))
        await asyncio.sleep(0.1)
        x_adjusted = True

    if x_adjusted:
        await asyncio.sleep(0.1)

    if Ymid < Y_steadyzone_min: 
        print("U")
        if already_up == False:
            IsSteady = False
            await ws.send(WebsocketMsg(NAME, {"toSerial":
                [ord("U"), 0, 0, 0]}).to_json())
            command_history.append(("U", formatted_time, coordinates_message))
            already_up = True
        else:
            print("Already Up")
    elif Ymid > Y_steadyzone_max:
        print("D")
        if already_down == False:
            IsSteady = False
            await ws.send(WebsocketMsg(NAME, {"toSerial":
                [ord("D"), 0, 0, 0]}).to_json())
            command_history.append(("D", formatted_time, coordinates_message))
            already_down = True
        else:
            print("Already Down")
    else:
        already_up = False
        already_down = False
        print("Balance")
        await ws.send(WebsocketMsg(NAME, {"toSerial":
            [ord("B"), 0, 0, 0]}).to_json())
        command_history.append(("B", formatted_time, coordinates_message))

    if X_steadyzone_min <= Xmid <= X_steadyzone_max and Y_steadyzone_min <= Ymid <= Y_steadyzone_max:
        if IsSteady == False:
            print("Steady - No Movement")
            await ws.send(WebsocketMsg(NAME, {"toSerial":
                [ord("X"), 0, 0, 0]}).to_json())
            command_history.append(("X", formatted_time, coordinates_message))
            IsSteady = True
        else:
            print("Steady Already")

    if Xmax - Xmin > 576 and Ymax - Ymin > 384:  # 座標面積在整個鏡頭的80%以上就微小擺動直走
        if IsSteady == False:
            print("3")
            await ws.send(WebsocketMsg(NAME, {"toSerial":
                [ord("3"), 0, 0, 0]}).to_json())
            command_history.append(("3", formatted_time, coordinates_message))
            await asyncio.sleep(0.1)
            await ws.send(WebsocketMsg(NAME, {"toSerial":
                [ord("2"), 0, 0, 0]}).to_json())
            command_history.append(("2", formatted_time, coordinates_message))
            IsSteady = True
        else:
            print("Already !")


async def recognitionLoop(recoResult, ws):
    picam2 = Picamera2()
    config = picam2.create_preview_configuration(main={"size": normalSize},
                                                 lores={"size": lowresSize, "format": "YUV420"})
    picam2.configure(config)

    stride = picam2.stream_configuration("lores")["stride"]
    picam2.post_callback = DrawRectangles

    encoder = H264Encoder(bitrate=None, framerate=30)
    encoder.output = FfmpegOutput("./videos/temp.mp4")
    picam2.start_encoder(encoder)
    picam2.switch_mode(config)
    picam2.start()

    try:
        while True:
            buffer = picam2.capture_buffer("lores")
            grey = buffer[:stride * lowresSize[1]].reshape((lowresSize[1], stride))
            await InferenceTensorFlow(ws, recoResult, grey, modelPath, outputName, labelPath)
            await asyncio.sleep(0.8)
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        picam2.stop()
        picam2.stop_encoder()
        encoder.output.output_filename = (
            f"./videos/{datetime.now().strftime('%Y%m%d_%H:%M:%S')}.mp4"
            )
        encoder.output.start()
        print(f"正在儲存影片: {encoder.output.output_filename}")
        save_command_history_to_csv()
        print("影片已保存")


def stopRecognition():
    global should_stop
    should_stop = True
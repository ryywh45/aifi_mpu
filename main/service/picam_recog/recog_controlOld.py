#改成讀取1920*1080的影像 到模型辨識前才轉成320*240的影像
import argparse
import cv2
import numpy as np
import tflite_runtime.interpreter as tflite
from picamera2 import MappedArray, Picamera2
import asyncio
import websockets.client as websockets
from communication.message import ClientToServer as WebsocketMsg
from pycoral.utils import edgetpu
from pycoral.utils import dataset
from pycoral.adapters import common
from pycoral.adapters import classify
import time
from datetime import datetime
normalSize = (720, 480) 
# 720*480+0.7延遲 30分鐘後不行 640*480+0.5 50分鐘都正常
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
    global rectangles, Detectnum ,Nothingnum
    if label:
        labels = ReadLabelFile(label)
    else:
        labels = None
    
    start_time = time.time()
    interpreter = tflite.Interpreter(model_path=model, num_threads=4)
    # interpreter = tflite.Interpreter(model_path=model,
    # experimental_delegates=[tflite.load_delegate('libedgetpu.so.1')])
    # interpreter = edgetpu.make_interpreter(model)
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
            else:
                print(f"  Score = {score}")
                result.score = score
            print(f"  Coordinates in pixels: xmin = {xmin:.1f}, ymin = {ymin:.1f}, xmax = {xmax:.1f}, ymax = {ymax:.1f}")
            result.xmin, result.ymin = f"{xmin:.1f}", f"{ymin:.1f}"
            result.xmax, result.ymax = f"{xmax:.1f}", f"{ymax:.1f}"

            if xmin <= 0: xmin = 0
            if xmax <= 0: xmax = 0
            if ymin <= 0: ymin = 0
            if ymax <= 0: ymax = 0
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
        if(IsSteady == False):
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
    IsSteady = True
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
    print("R2")
    print(f"IsSteady值:{IsSteady}")
    await ws.send(WebsocketMsg(NAME, {"toSerial":
        [ord("R"), ord("2"), 0, 0]}).to_json())
    current_time = datetime.now()
    formatted_time = current_time.strftime('%Y-%m-%d %H:%M:%S') + f".{current_time.microsecond // 1000:03d}"
    print(f"開始動作:{formatted_time}")
    await asyncio.sleep(0.1)

            


async def recognitionLoop(recoResult, ws):
    picam2 = Picamera2()
    config = picam2.create_preview_configuration(main={"size": normalSize},
                                                 lores={"size": lowresSize, "format": "YUV420"})
    picam2.configure(config)

    stride = picam2.stream_configuration("lores")["stride"]
    picam2.post_callback = DrawRectangles

    picam2.start()

    try:
        while True:
            current_time = datetime.now()
            formatted_time = current_time.strftime('%Y-%m-%d %H:%M:%S') + f".{current_time.microsecond // 1000:03d}"
            print(f"迴圈開始時間:{formatted_time}")
            buffer = picam2.capture_buffer("lores")
            grey = buffer[:stride * lowresSize[1]].reshape((lowresSize[1], stride))
            await InferenceTensorFlow(ws,recoResult, grey, modelPath, outputName, labelPath)
            await asyncio.sleep(0.8)
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        picam2.stop()
    
def stopRecognition():
    global should_stop
    should_stop = True

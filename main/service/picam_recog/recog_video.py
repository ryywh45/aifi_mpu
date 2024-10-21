import argparse
import cv2
import numpy as np
import tflite_runtime.interpreter as tflite
from picamera2 import MappedArray, Picamera2
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
    global rectangles, Detectnum ,Nothingnum, command_history,IsSteady
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

    # 檢查影像通道數，確保只有一個通道時才進行灰階轉換
    if len(image.shape) == 2:  # 如果是灰階影像
        rgb = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    else:
        rgb = image  # 如果已經是彩色影像，直接使用

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
                    cv2.rectangle(image, (int(xmin), int(ymin)), (int(xmax), int(ymax)), (0, 255, 0), 2)
                    cv2.putText(image, f"{labels[classId]}: {score:.2f}", (int(xmin), int(ymin)-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2) 
            else:
                print(f"  Score = {score}")
                result.score = score
            print(f"  Coordinates in pixels: xmin = {xmin:.1f}, ymin = {ymin:.1f}, xmax = {xmax:.1f}, ymax = {ymax:.1f}")
            result.xmin, result.ymin = f"{xmin:.1f}", f"{ymin:.1f}"
            result.xmax, result.ymax = f"{xmax:.1f}", f"{ymax:.1f}"

            rectangles.append([xmin, ymin, xmax, ymax])
    
    if Nothingnum >= 29:
        # print("Nothing R2")
        # await ws.send(WebsocketMsg(NAME, {"toSerial":
        #     [ord("R"), ord("2"), 0, 0]}).to_json())
        # await asyncio.sleep(0.1)
        Nothingnum = 0

    if Detectnum >= 2:
        if(IsSteady == False):
            await resultforControl(ws)
            IsSteady == True
        Detectnum = 0
        rectangles = []
    else:
        print("controlFun not implemented")
    
    end_time = time.time()
    processing_time = end_time - start_time
    print(f"模型辨識時間: {processing_time:.4f} seconds")
    return image

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
    print("R2")
    current_time = datetime.now()
    formatted_time = current_time
    coordinates_message = f"X:{Xmin}~{Xmax}；Y:{Ymin}~{Ymax}"
    await ws.send(WebsocketMsg(NAME, {"toSerial":
        [ord("R"), ord("2"), 0, 0]}).to_json())
    command_history.append(("3", formatted_time, coordinates_message))
    await asyncio.sleep(0.1)



async def recognitionLoop(recoResult, ws):
    global out
    picam2 = Picamera2()
    config = picam2.create_preview_configuration(main={"size": normalSize},
                                                 lores={"size": lowresSize, "format": "YUV420"})
    picam2.configure(config)
    picam2.post_callback = DrawRectangles

    picam2.start()

    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    frame_size = (normalSize[0], normalSize[1])
    out = cv2.VideoWriter(f"{datetime.now().strftime('%Y%m%d_%H:%M:%S')}.avi", fourcc, 20.0, frame_size)

    if not out.isOpened():
        print("VideoWriter 無法開啟。")
        return

    latest_detection_frame = None  # 用來存儲辨識結果


    async def perform_inference(rgb_frame, frame_time):
        nonlocal latest_detection_frame
        print("影像辨識")
        frame_with_detections = await InferenceTensorFlow(ws, recoResult, rgb_frame, modelPath, outputName, labelPath)
        latest_detection_frame = (frame_with_detections, frame_time)  # 存儲辨識結果與時間

    try:
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        buffer = picam2.capture_buffer("lores")
        grey = buffer[:picam2.stream_configuration("lores")["stride"] * lowresSize[1]].reshape((lowresSize[1], picam2.stream_configuration("lores")["stride"]))
        rgb = cv2.cvtColor(grey, cv2.COLOR_GRAY2BGR)
        asyncio.create_task(perform_inference(rgb, current_time))  

        while True:
            start_time = time.time()

            buffer = picam2.capture_buffer("lores")
            grey = buffer[:picam2.stream_configuration("lores")["stride"] * lowresSize[1]].reshape((lowresSize[1], picam2.stream_configuration("lores")["stride"]))
            rgb = cv2.cvtColor(grey, cv2.COLOR_GRAY2BGR)
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f"迴圈開始:{current_time}")
            frame_with_detections = rgb
            if latest_detection_frame is not None:
                detection_frame, detection_time = latest_detection_frame
                if detection_time != None:
                    frame_with_detections = detection_frame
                    latest_detection_frame = None  


            frame_with_detections = cv2.resize(frame_with_detections, frame_size)
            cv2.putText(frame_with_detections, current_time, (10, 20), cv2.FONT_HERSHEY_SIMPLEX,
                        fontScale=0.5, color=(255, 255, 255), thickness=1)

            out.write(frame_with_detections)

            if latest_detection_frame is None:
                current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                buffer = picam2.capture_buffer("lores")
                grey = buffer[:picam2.stream_configuration("lores")["stride"] * lowresSize[1]].reshape((lowresSize[1], picam2.stream_configuration("lores")["stride"]))
                rgb = cv2.cvtColor(grey, cv2.COLOR_GRAY2BGR)
                asyncio.create_task(perform_inference(rgb, current_time))  # 啟動新一輪辨識

            elapsed_time = time.time() - start_time
            await asyncio.sleep(max(0, (1 / 20.0) - elapsed_time))  # 維持每秒 20 幀
    except KeyboardInterrupt:
        print("中斷執行...")
    finally:
        picam2.stop()
        if out is not None:
            out.release()
        save_command_history_to_csv()
        print("影片已保存")












def stopRecognition():
    global should_stop
    should_stop = True
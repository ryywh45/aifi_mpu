#改成讀取1920*1080的影像 到模型辨識前才轉成320*240的影像
import argparse
import cv2
import numpy as np
import tflite_runtime.interpreter as tflite
from picamera2 import MappedArray, Picamera2
import asyncio
from picam_recog import RecoResult
import websockets.client as websockets
from communication.message import ClientToServer as WebsocketMsg
normalSize = (1920, 1080)
lowresSize = (320, 240)

rectangles = []
NAME = 'picam_recog.py'
modelPath = "./model/model1.tflite"
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

async def InferenceTensorFlow(ws,result: RecoResult, image, model, output, label=None):
    global rectangles

    if label:
        labels = ReadLabelFile(label)
    else:
        labels = None

    interpreter = tflite.Interpreter(model_path=model, num_threads=4)
    interpreter.allocate_tensors()

    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    height = input_details[0]['shape'][1]
    width = input_details[0]['shape'][2]
    floating_model = input_details[0]['dtype'] == np.float32

    rgb = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)

    # Resize the image to the model's input size
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

    rectangles = []
    for i in range(num_boxes):
        box = detected_boxes[0][i]
        top, left, bottom, right = box
        classId = int(detected_classes[0][i])
        score = detected_scores[0][i]

        if score > 0.6:
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
            rectangles.append([xmin, ymin, xmax, ymax])
            # res = result.to_dict().copy()
            await ws.send(WebsocketMsg(NAME, {"toSerial":[ord("T"),int(classId),int(round(xmin+xmax)/2,0),int(round(ymin+ymax)/2,0)]}).to_json())
    return rgb  # Return the resized RGB image for saving later

async def recognitionLoop(recoResult: RecoResult,ws):
    picam2 = Picamera2()
    config = picam2.create_preview_configuration(main={"size": normalSize},
                                                 lores={"size": lowresSize, "format": "YUV420"})
    picam2.configure(config)

    stride = picam2.stream_configuration("lores")["stride"]
    picam2.post_callback = DrawRectangles

    picam2.start()

    try:
        while True:
            buffer = picam2.capture_buffer("lores")
            grey = buffer[:stride * lowresSize[1]].reshape((lowresSize[1], stride))
            InferenceTensorFlow(ws,recoResult, grey, modelPath, outputName, labelPath)
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        picam2.stop()
def stopRecognition():
    global should_stop
    should_stop = True
if __name__ == '__main__':
    r = RecoResult()
    should_stop = False
    asyncio.run(recognitionLoop(r))

# for new4.py
import asyncio 
import cv2
import numpy as np
import tflite_runtime.interpreter as tflite
from picamera2 import MappedArray, Picamera2
from picam_recog import RecoResult

normalSize = (640, 480)
lowresSize = (320, 240)

rectangles = []

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
                rect_start = (int(rect[0] * 2) - 5, int(rect[1] * 2) - 5)
                rect_end = (int(rect[2] * 2) + 5, int(rect[3] * 2) + 5)
                cv2.rectangle(m.array, rect_start, rect_end, (0, 255, 0, 255), 2)
            else:
                print("Invalid rectangle:", rect) 

def InferenceTensorFlow(result: RecoResult, image, model, output, label=None):
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
    initial_h, initial_w, channels = rgb.shape

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

    # print("num_boxes:", num_boxes)
    # print("detected_boxes:", detected_boxes)
    # print("detected_classes:", detected_classes)
    # print("detected_scores:", detected_scores)

    num_boxes = int(num_boxes[0])

    rectangles = []
    for i in range(num_boxes):
        box = detected_boxes[0][i]
        top, left, bottom, right = box
        classId = int(detected_classes[0][i])
        score = detected_scores[0][i]

        if score > 0.8:
            ymin = top * initial_h
            xmin = left * initial_w
            ymax = bottom * initial_h
            xmax = right * initial_w
            # print(f"Box {i}:")
            # print(f"  Detected box coordinates: {box}")
            

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

async def recognitionLoop(recoResult: RecoResult):
    picam2 = Picamera2()
    config = picam2.create_preview_configuration(main={"size": normalSize},
                                                 lores={"size": lowresSize, "format": "YUV420"})
    picam2.configure(config)

    stride = picam2.stream_configuration("lores")["stride"]
    picam2.post_callback = DrawRectangles

    picam2.start()

    try:
        while not should_stop:
            buffer = picam2.capture_buffer("lores")
            grey = buffer[:stride * lowresSize[1]].reshape((lowresSize[1], stride))
            InferenceTensorFlow(recoResult, grey, modelPath, outputName, labelPath)
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

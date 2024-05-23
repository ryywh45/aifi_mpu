import asyncio
import websockets
import serial
import json

async def websocket_server(websocket, path):
    """deal with incoming messages from webSocket"""
    try:
        async for data in websocket:
            print(f"From webSocket <- {data}")
            await serial_write(json.loads(data))
    except websockets.exceptions.ConnectionClosedError as e:
        print(f"WebSocket connection closed: {e}")
    except Exception as e:
        print(f"Error in websocket_server: {e}")

async def serial_reader():
    """deal with incoming messages from serial"""
    try:
        while True:
            data = await loop.run_in_executor(None, ser.readline)
            print(f"From serial <- {data}={list(data)}")
    except Exception as e:
        print(f"Error in serial_reader: {e}")

async def serial_write(data):
    """process data and send it to serial"""
    try:
        msg = [ord('!'), 2, data["Address"], data["Value"], 0]
        checksum = sum(msg)
        msg.append(checksum // 256)
        msg.append(checksum % 256)
        msg.append(ord('\n'))
        print(f"To serial -> {msg}={[chr(i) for i in msg]}")
        ser.write(bytes(msg))
    except Exception as e:
        print(f"Error in serial_write: {e}")

async def main():
    # websocket_server_task = websockets.serve(websocket_server, "localhost", 8000)
    # await websocket_server_task
    print("WebSocket server start")

    await asyncio.gather(
        websockets.serve(websocket_server, "localhost", 8000),
        serial_reader()
    )

if __name__ == "__main__":
    try:
        ser = serial.Serial('/dev/serial0', 115200)
    except serial.SerialException as err:
        print(f"Failed to open serial port: {err}")
        exit(1)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.run_forever()

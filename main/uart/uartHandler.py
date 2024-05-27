import asyncio
import websockets.server as websockets
from serial import Serial, SerialException
import json

#=================================================================#

wsConnections: dict[str, websockets.WebSocketServerProtocol] = {}

async def wsHandler(websocket: websockets.WebSocketServerProtocol):
    """deal with incoming messages from webSocket"""
    try:
        async for data in websocket:
            try: 
                service, service_data = data.split(' : ')
            except Exception: 
                print('Invalid data from webSocket')
                continue
            print(f"From {service} <- {data}")
            if service_data == 'Hello':
                wsConnections[service] = websocket
                continue

            if service == '[ test.py ]':
                result = await serial_write(json.loads(service_data))
                if result is True:
                    print(f'To {service} -> ok')
                    await websocket.send('ok')
                else:
                    print(f'To {service} -> error')
                    await websocket.send('error')

            elif service == '[ test2.py ]':
                result = await serial_write(json.loads(service_data))
                if result is True:
                    print(f'To {service} -> ok')
                    await websocket.send('ok')
                else:
                    print(f'To {service} -> error')
                    await websocket.send('error')

            elif service == '[ picam_record.py ]':
                pass

    except Exception as e:
        print(f"Error in [ wsHandler() ] : {e}")

    finally:
        if service in wsConnections:
            del wsConnections[service]

async def wsSend(service, data):
    """send data to webSocket"""
    try:
        print(f"To {service} -> {data}")
        await wsConnections[service].send(data)

    except KeyError:
        print(f"Error in [ wsSend() ] : {service} not connected")
    
    except Exception as e:
        print(f"Error in [ wsSend() ] : {e}")

#=================================================================#

async def serial_reader():
    """deal with incoming messages from serial"""
    await asyncio.sleep(3)
    loop = asyncio.get_event_loop()
    print("Serial reader start")

    try:
        while True:
            data = await loop.run_in_executor(None, ser.readline)
            if list(data) == []: continue

            print(f"From serial <- {data}={list(data)}")
            if data[1] == 2:                                          # code 2 = control picam
                if data[2] == 1:
                    await wsSend('[ picam_record.py ]', 'go')               # start recording
                elif data[2] == 2:
                    await wsSend('[ picam_record.py ]', 'stop')             # stop recording
                else:
                    pass
            else:
                pass

    except Exception as e:
        print(f"Error in [ serial_reader() ] : {e}")

    finally:
        ser.close()

async def serial_write(data):
    """process data and send it to serial"""
    try:
        msg = [ord('!'), 2, data["Address"], data["Value"], 0]
        checksum = sum(msg)
        msg.append(checksum // 256)
        msg.append(checksum % 256)
        msg.append(ord('\n'))
        ser.write(bytes(msg))
        print(f"To serial -> {msg}={[chr(i) for i in msg]}")

    except Exception as e:
        print(f"Error in [ serial_write() ] : {e}")
        return False

    return True

#=================================================================#

async def main():
    print("WebSocket server start")
    async with websockets.serve(wsHandler, "localhost", 8000):
        await serial_reader()


if __name__ == "__main__":
    try:
        ser = Serial('/dev/serial0', 115200, timeout=1)
        ser.flush()

    except SerialException as err:
        print(f"Failed to open serial port: {err}")
        exit(1)

    asyncio.run(main())
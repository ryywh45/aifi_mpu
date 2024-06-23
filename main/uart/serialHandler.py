import asyncio

from communication.message import ServerToClient as WebsocketMsg
from communication.message import ToSerial as SerialMsg, PREFIX, LENGTH, DATA_LENGTH


async def serial_reader(ser, serial_write, ws_send):
    """handles incoming serial data"""
    await asyncio.sleep(3)
    loop = asyncio.get_event_loop()
    print("Serial reader start")

    try:
        while True:
            prefix = await loop.run_in_executor(None, ser.read, 1)
            if prefix != ord(PREFIX):
                continue

            length = await loop.run_in_executor(None, ser.read, 1)
            if length != LENGTH:
                continue

            data = await loop.run_in_executor(None, ser.read, LENGTH - 2)
            fulldata = [prefix, length, *data]
            if fulldata != SerialMsg(data[:DATA_LENGTH]).show():
                print(f"[ serial_reader() ] : checksum unmatch")
                continue

            print(f"From serial <- {fulldata}={list(fulldata)}")
            if data[1] == 2:
                if data[2] == 1:
                    await ws_send('picam_record.py', WebsocketMsg(0, 'go'))
                elif data[2] == 2:
                    await ws_send('picam_record.py', WebsocketMsg(0, 'stop'))
                else:
                    pass
            else:
                pass

    except Exception as e:
        print(f"Error in [ serial_reader() ] : {e}")

    finally:
        ser.close()


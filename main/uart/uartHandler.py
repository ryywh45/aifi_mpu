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
            if prefix == b'': continue
            if prefix != PREFIX:
                print(f"[ serial_reader() ] : prefix unmatch ({prefix})")
                continue

            length = await loop.run_in_executor(None, ser.read, 1)
            if ord(length) != LENGTH:
                print(f"[ serial_reader() ] : length unmatch ({length})")
                continue

            data = await loop.run_in_executor(None, ser.read, LENGTH - 2)
            data = list(data)
            fulldata = [ord(prefix), ord(length), *data]
            if fulldata != SerialMsg(data[:DATA_LENGTH]).show():
                print(f"[ serial_reader() ] : checksum unmatch")
                continue

            print(f"From serial <- {fulldata}")
            if data[0] == 1:
                if data[1] == 0:
                    await ws_send('picam_record.py', WebsocketMsg(3, 'go'))
                elif data[1] == 1:
                    await ws_send('picam_record.py', WebsocketMsg(3, 'stop'))
                elif data[1] == 2:
                    await ws_send('picam_record.py', WebsocketMsg(3, 'take-a-pic'))
                else:
                    pass
            else:
                pass

    except Exception as e:
        print(f"Error in [ serial_reader() ] : {e}")

    finally:
        ser.close()


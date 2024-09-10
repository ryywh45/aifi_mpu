# Used to test multiple clients sending and receiving data from the server.

import asyncio
import websockets.client as websockets
import json

from communication.message import ClientToServer as WebsocketMsg
from communication.message import ToSerial as SerialMsg
NAME = 'test.py'


async def send_loop(ws) -> int:
    loop = asyncio.get_event_loop()
    try:
        while True:
            userinput = await loop.run_in_executor(
                None,
                lambda: input("Command:\n1) Send to serial\n2) Start recording\n3) Stop recording\n4) Take a picture\n5) Exit\n> "))
            try:
                userinput = int(userinput)
            except ValueError:
                print("\033[31mInvalid input, please enter an integer value\n\033[0m")
                continue

            if userinput == 5:
                return
            elif userinput == 1:
                while True:
                    data = await loop.run_in_executor(
                        None, 
                        lambda: input("\nEnter w,x,y,z to send to serial\n* length must be 4\n* values must be integers\nor 'exit' to exit\n> "))
                    if len(data.split(',')) == 4 and all(ord(x) for x in data.split(',')):
                        break
                    elif data == 'exit':
                        return
                    else:
                        print("\033[31mInvalid input\n\033[0m")
                new_data = data.split(',')
                for x in range(new_data):
                    new_data[x] = ord(new_data[x])
                
                await ws.send(WebsocketMsg(NAME, {'toSerial': [int(x) for x in new_data]}).to_json())
            elif userinput == 2:
                await ws.send(WebsocketMsg(NAME, 'startRecording').to_json())
            elif userinput == 3:
                await ws.send(WebsocketMsg(NAME,'stopRecording').to_json())
            elif userinput == 4:
                await ws.send(WebsocketMsg(NAME,'take-a-pic').to_json())
            else:
                print("\033[31mInvalid input, fk u\n\033[0m")
                continue

            response = await ws.recv()
            print(f"From server <- {json.loads(response)}\n")

            await asyncio.sleep(1)

    except Exception as e:
        print(f"Error in [ send_loop() ]: {e}")

async def main():
    async with websockets.connect("ws://localhost:8000") as ws:
        await ws.send(WebsocketMsg(NAME, 'Hello').to_json())
        try:
            await send_loop(ws)
        except Exception as e:
            print(f"Error in [ main() ]: {e}")
    print('Connection closed.')

if __name__ == "__main__":
    asyncio.run(main())

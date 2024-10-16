import asyncio, json
import websockets.client as websockets
from dataclasses import dataclass, asdict

from communication.message import ClientToServer as WebsocketMsg
NAME = 'picam_recog.py'

# from recog_control import recognitionLoop, stopRecognition
from recog_control import recognitionLoop, stopRecognition
@dataclass()
class RecoResult:
    label = ""
    score = ""
    xmin = ""
    ymin = ""
    xmax = ""
    ymax = ""

    def to_dict(self):
        return asdict(self)

async def main():
    async with websockets.connect("ws://localhost:8000") as ws:
        await ws.send(WebsocketMsg(NAME, 'Hello').to_json())
        recoResult = RecoResult()
        asyncio.create_task(recognitionLoop(recoResult,ws))
        try:
            async for message in ws:
                try:
                    message = json.loads(message)
                    status = message['status']
                    data = message['data']
                except Exception:
                    print('Invalid data from webSocket')
                    continue
                print(f"From server <- {message}")

                if data == "go":
                    print(f'To server -> {WebsocketMsg(NAME, "Starting recognition").show()}')
                    await ws.send(WebsocketMsg(NAME, "Starting recognition").to_json())
                    asyncio.create_task(recognitionLoop(recoResult,ws))

                elif data == "stop":
                    stopRecognition()
                    print(f'To server -> {WebsocketMsg(NAME, "Stopping recognition").show()}')
                    await ws.send(WebsocketMsg(NAME, "Stopping recognition").to_json())

                elif data == "get":
                    res = recoResult.to_dict().copy()
                    print(f'To server -> {WebsocketMsg(NAME, res).show()}')
                    await ws.send(WebsocketMsg(NAME, res).to_json())

        except Exception as e:
            print(f"Error in [ main() ]: {e}")
    print('Connection closed.')


if __name__ == '__main__':
    asyncio.run(main())

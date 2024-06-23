import asyncio
import websockets.client as websockets

from communication.message import ClientToServer as WebsocketMsg
NAME = 'template.py'

from your_code import your_function


async def main():
    async with websockets.connect("ws://localhost:8000") as ws:
        await ws.send(WebsocketMsg(NAME, 'Hello').to_json())
        try:
            return_value = your_function()
            print(f'To server -> {WebsocketMsg(NAME, return_value).show()}')
            await ws.send(WebsocketMsg(NAME, return_value).to_json())
            response = await ws.recv()
            print(f"From server <- {response}")

        except Exception as e:
            print(f"Error in [ main() ]: {e}")


if __name__ == '__main__':
    asyncio.run(main())
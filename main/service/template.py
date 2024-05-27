import asyncio
import websockets.client as websockets

from your_code import your_function

async def main():
    async with websockets.connect("ws://localhost:8000") as ws:
        await ws.send('[ template.py ] : Hello')
        try:
            return_value = your_function()
            print(f'To server -> [ template.py ] : {return_value}')
            await ws.send(f'[ template.py ] : {return_value}')
            response = await ws.recv()
            print(f"From server <- {response}")

        except Exception as e:
            print(f"Error in [ main() ]: {e}")


if __name__ == '__main__':
    asyncio.run(main())
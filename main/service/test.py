import asyncio
import websockets
import json

async def send(serviceName: str, address: int, value: int) -> int:
    loop = asyncio.get_event_loop()
    async with websockets.connect("ws://localhost:8000") as ws:
        try:
            while True:
                userinput = await loop.run_in_executor(None, lambda: input("Enter an integer to send, or 'exit' to exit: "))

                if userinput.lower() == 'exit':
                    return

                try:
                    value = int(userinput)
                except ValueError:
                    print("Invalid input, please enter an integer value.")
                    continue

                data = json.dumps({"Service": serviceName, "Address": address, "Value": value})
                try:
                    await ws.send(data)
                    # response = await ws.recv()
                    # print(f"Received response from server: {response}")
                except websockets.exceptions.ConnectionClosedError as e:
                    print(f"WebSocket connection closed: {e}")
                    return
                except Exception as errMsg:
                    print(f"WebSocket Error -> {errMsg}")
                    return
        finally:
            await ws.close()

if __name__ == "__main__":
    asyncio.run(send("init", 1, 1))

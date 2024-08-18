import asyncio
import websockets.server as websockets
from serial import Serial, SerialException
import json

from communication.message import ServerToClient as WebsocketMsg
from communication.message import ToSerial as SerialMsg
from service.serviceHandler import service_handler
from uart.uartHandler import serial_reader


class CommunicaionBridge:
    """Bridge between webSocket and serial"""

    def __init__(self):
        self.wsConnections: dict[str, websockets.WebSocketServerProtocol] = {}
        try:
            self.ser = Serial('/dev/serial0', 115200, timeout=1)
        except SerialException as err:
            print(f"Failed to open serial port: {err}")
            exit(1)

    async def ws_handler(self, ws: websockets.WebSocketServerProtocol):
        """deal with incoming messages from webSocket"""
        service_name = ''
        try:
            async for message in ws:
                try:
                    message = json.loads(message)
                    service_name = message['service']
                    service_data = message['data']
                except Exception:
                    print('Invalid data from webSocket')
                    continue

                print(f"From [ {service_name} ] <- {service_data}")
                if service_data == 'Hello':
                    self.wsConnections[service_name] = ws
                    continue

                result = await service_handler(service_name, service_data, self.serial_write, self.ws_send)
                if result is True:
                    await self.ws_send(service_name, WebsocketMsg(0, 'ok'))
                else:
                    await self.ws_send(service_name, WebsocketMsg(1, 'error'))
        except Exception as e:
            print(f"Error in [ wsHandler() ] : {e}")
        finally:
            await ws.close()
            if service_name in self.wsConnections:
                del self.wsConnections[service_name]
                print(f'[ {service_name} ] disconnected')

    async def ws_send(self, service_name: str, msg: WebsocketMsg):
        """send data to webSocket"""
        try:
            print(f"To {service_name} -> {msg.show()}")
            await self.wsConnections[service_name].send(msg.to_json())
            return True
        except KeyError:
            print(f"Error in [ ws_send() ] : {service_name} not connected")
            return False
        except Exception as e:
            print(f"Error in [ ws_send() ] : {e}")
            return False

    async def serial_write(self, msg: SerialMsg):
        """process data and send it to serial"""
        try:
            assert isinstance(msg, SerialMsg), "Paremeter msg should be a SerialMsg"
            self.ser.write(msg.to_bytes())
            print(f"To serial -> {msg.show()}")
        except Exception as e:
            print(f"Error in [ serial_write() ] : {e}")
            return False
        return True

    async def main(self):
        print("WebSocket server start")
        async with websockets.serve(self.ws_handler, "localhost", 8000):
            await serial_reader(self.ser, self.serial_write, self.ws_send)


if __name__ == "__main__":
    cb = CommunicaionBridge()
    asyncio.run(cb.main())

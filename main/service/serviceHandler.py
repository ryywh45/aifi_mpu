from communication.message import ServerToClient as WebsocketMsg
from communication.message import ToSerial as SerialMsg


async def service_handler(service_name: str, service_data, serial_write, ws_send):
    """handles incoming service data"""
    if service_name == 'test.py':
        if isinstance(service_data, dict) and 'toSerial' in service_data:
            return await serial_write(SerialMsg(service_data['toSerial']))
        elif service_data == 'startRecording':
            return await ws_send('picam_record.py', WebsocketMsg(3, 'go'))
        elif service_data =='stopRecording':
            return await ws_send('picam_record.py', WebsocketMsg(3, 'stop'))
        elif service_data =='take-a-pic':
            return await ws_send('picam_record.py', WebsocketMsg(3, 'take-a-pic'))
    elif service_name == 'picam_record.py':
        return True

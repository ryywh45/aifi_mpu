from communication.message import ServerToClient as WebsocketMsg
from communication.message import ToSerial as SerialMsg


async def service_handler(service_name: str, service_data, serial_write, ws_send):
    """handles incoming service data"""
    if service_name == 'test.py':
        return await serial_write(SerialMsg(service_data))

    # elif service_name == 'picam_record.py':
    #     pass

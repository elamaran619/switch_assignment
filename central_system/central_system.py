import base64
import logging
from typing import Optional

import websockets

from central_system.ocpp_handler import OcppMessageHandler
from central_system.server_state import ServerState

from common.constants import *

state: Optional[ServerState] = None


async def on_connect(websocket, path):
    global state

    if HEADER_SEC_WEBSOCKET_PROTOCOL not in websocket.request_headers:
        logging.error('Client has not requested any protocol')
        return await websocket.close()

    if HEADER_AUTHORIZATION not in websocket.request_headers:
        logging.error('Missing authorization header')
        return await websocket.close()

    auth_data = websocket.request_headers[HEADER_AUTHORIZATION]
    if not state.is_valid_credentials(auth_data):
        logging.error('Invalid credentials')
        return await websocket.close()

    if not websocket.subprotocol:
        logging.warning('Protocols Mismatched | Expected Subprotocols: %s,'
                        ' but client supports %s | Closing connection',
                        websocket.available_subprotocols,
                        websocket.request_headers[HEADER_SEC_WEBSOCKET_PROTOCOL])
        return await websocket.close()

    cp_id = path.strip('/')
    try:
        cp_id = int(cp_id)
    except ValueError:
        logging.error('Invalid cp id, expected integer')
        return await websocket.close()

    ocpp_handler = OcppMessageHandler(state, id=cp_id, connection=websocket)

    try:
        state.add_cp(cp_id)
        await ocpp_handler.start()
    except Exception:
        state.remove_cp(cp_id)


async def start_ocpp_server(user: str, password: str, port_number: int = 9000):
    global state

    server = await websockets.serve(
        on_connect,
        '0.0.0.0',
        port_number,
        subprotocols=['ocpp2.0.1']
    )

    logging.info("Server Started listening to new connections...")

    state = ServerState(user, password)

    await server.wait_closed()

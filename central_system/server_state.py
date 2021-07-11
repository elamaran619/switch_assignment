import base64

from common.constants import STATE_ONLINE, STATE_OFFLINE
from common.ocpp_message_type import OcppMessageType

OCPP_STATE_FSM = {
    STATE_OFFLINE: lambda message: (
        (STATE_ONLINE, True) if message == OcppMessageType.BOOT_NOTIFICATION else (STATE_OFFLINE, False)
    ),
    STATE_ONLINE: lambda message: (STATE_ONLINE, True)
}


class ServerState:
    def __init__(self, user: str, password: str):
        self.user = user
        self.password = password
        self.cps_state = {}

    def is_valid_credentials(self, auth_data: str) -> bool:
        if not auth_data:
            return False

        if not auth_data.lower().startswith('basic '):
            return False

        encoded_credentials = base64.b64encode(f'{self.user}:{self.password}'.encode('utf-8')).decode('utf-8')
        if encoded_credentials != auth_data[6:]:
            return False

        return True

    def add_cp(self, cp_id: int):
        self.cps_state[cp_id] = STATE_OFFLINE

    def remove_cp(self, cp_id: int):
        self.cps_state.pop(cp_id, None)

    # Basic FSM which will accept BootNotification at any time and StatusNotification only after a BootNotification
    def next_cp_state(self, cp_id: int, message_type: OcppMessageType):
        if cp_id not in self.cps_state:
            return False

        if self.cps_state[cp_id] not in OCPP_STATE_FSM:
            return False

        self.cps_state[cp_id], is_allowed = OCPP_STATE_FSM[self.cps_state[cp_id]](message_type)

        return is_allowed

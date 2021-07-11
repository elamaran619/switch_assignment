import base64

from common.ocpp_message_type import OcppMessageType


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

    # A proper implementation needs a Finite State Machine here, but I don't really have the time to do this properly atm
    def set_cp_state(self, cp_id: int, state: str):
        self.cps_state[cp_id] = (state == "ONLINE")

    def remove_cp(self, cp_id: int):
        self.cps_state.pop(cp_id, None)

    def is_message_allowed(self, cp_id: int, message_type: OcppMessageType):
        if not cp_id in self.cps_state:
            return False

        if message_type == OcppMessageType.BOOT_NOTIFICATION:
            return True

        if message_type == OcppMessageType.STATUS_NOTIFICATION:
            return self.cps_state[cp_id]

        return False
from ocpp.exceptions import OCPPError, GenericError
from ocpp.routing import on
from ocpp.v201 import ChargePoint as cp
from ocpp.v201 import call_result

from datetime import datetime

import logging

from central_system.server_state import ServerState
from common.constants import VALUE_STATUS_ACCEPTED, VALUE_STATUS_REJECTED
from common.ocpp_message_type import OcppMessageType


class OcppMessageHandler(cp):
    def __init__(self, state: ServerState, **kwargs):
        cp.__init__(self, **kwargs)
        self.server_state = state

    @on('BootNotification')
    def on_boot_notification(self, charging_station, reason, **kwargs):
        if not self.server_state.next_cp_state(self.id, OcppMessageType.BOOT_NOTIFICATION):
            logging.error('BootNotification message type not allowed in current state')
            raise GenericError(details='Message not allowed in current state')

        return call_result.BootNotificationPayload(
            current_time=datetime.utcnow().isoformat(),
            interval=10,
            status=VALUE_STATUS_ACCEPTED
        )

    @on('StatusNotification')
    def on_status_notification(self, **kwargs):
        if not self.server_state.next_cp_state(self.id, OcppMessageType.BOOT_NOTIFICATION):
            logging.error('StatusNotification message type not allowed in current state')
            raise GenericError(details='Message not allowed in current state')

        logging.info(f'Received StatusNotification with {str(kwargs)}')
        return call_result.StatusNotificationPayload()
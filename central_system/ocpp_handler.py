from ocpp.exceptions import OCPPError
from ocpp.routing import on
from ocpp.v201 import ChargePoint as cp
from ocpp.v201 import call_result

from datetime import datetime

import logging

from central_system.server_state import ServerState
from common.constants import VALUE_STATUS_ACCEPTED, VALUE_STATUS_REJECTED
from common.ocpp_message_type import OcppMessageType


class OcppMessageHandler(cp):
    def set_state(self, state: ServerState):
        self.server_state = state

    @on('BootNotification')
    def on_boot_notification(self, charging_station, reason, **kwargs):
        if not self.server_state or not self.server_state.is_message_allowed(self.id, OcppMessageType.BOOT_NOTIFICATION):
            raise OCPPError(details='Not allowed')

        self.server_state.set_cp_state(self.id, 'ONLINE')

        return call_result.BootNotificationPayload(
            current_time=datetime.utcnow().isoformat(),
            interval=10,
            status=VALUE_STATUS_ACCEPTED
        )

    @on('StatusNotification')
    def on_status_notification(self, **kwargs):
        if not self.server_state or not self.server_state.is_message_allowed(self.id, OcppMessageType.STATUS_NOTIFICATION):
            raise OCPPError(details='Message not allowed')

        logging.info(f'Received StatusNotification with {str(kwargs)}')
        return call_result.StatusNotificationPayload()
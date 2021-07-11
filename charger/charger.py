import asyncio
from datetime import datetime
from typing import List

from ocpp.v201 import call
from ocpp.v201 import ChargePoint as BaseChargePoint

from common.constants import *

import logging

from common.ocpp_message_type import OcppMessageType


class ChargePoint(BaseChargePoint):
    def __init__(self, cp_id: int, connection, connector_ids: List[int]):
        BaseChargePoint.__init__(self, cp_id, connection)

        if not connector_ids:
            logging.error("Unable to create instance of 'ChargePoint': missing value for parameter 'connector_ids'")
            raise Exception("Class initialization exception")

        self.connector_ids = connector_ids
        self.cp_id = cp_id
        self.can_send = asyncio.Lock()

        # These can actually be passed as constructor arguments, but keeping it simple
        self.model = 'testModel'
        self.vendor = 'testVendor'

    async def send_message(self, message_type: OcppMessageType, payload: {}):
        async with self.can_send:
            if message_type == OcppMessageType.BOOT_NOTIFICATION:
                return await self._send_boot_notification(payload)
            elif message_type == OcppMessageType.STATUS_NOTIFICATION:
                return await self._send_status_notification(payload)

    async def _send_boot_notification(self, payload):
        request = call.BootNotificationPayload(
            charging_station={
                FIELD_CP_MODEL: payload[FIELD_CP_MODEL],
                FIELD_CP_VENDOR: payload[FIELD_CP_MODEL]
            },
            reason=payload[FIELD_BOOT_NOTIFICATION_REASON]
        )

        return await self.call(request)

    async def _send_status_notification(self, payload):
        request = call.StatusNotificationPayload(
            timestamp=datetime.utcnow().isoformat(),
            connector_status=payload[FIELD_CONNECTOR_STATUS],
            evse_id=payload[FIELD_CONNECTOR_ID],
            connector_id=self.cp_id
        )

        return await self.call(request)

    def has_connector_with_id(self, cp_id: int):
        return cp_id in self.connector_ids

    async def send_boot_up_sequence(self):
        await self.send_message(
            OcppMessageType.BOOT_NOTIFICATION,
            {
                FIELD_CP_MODEL: self.model,
                FIELD_CP_VENDOR: self.vendor,
                FIELD_BOOT_NOTIFICATION_REASON: VALUE_REASON_POWER_UP
            }
        )

        await self.send_message(
            OcppMessageType.STATUS_NOTIFICATION,
            {
                FIELD_CONNECTOR_STATUS: VALUE_AVAILABLE,
                FIELD_CONNECTOR_ID: 1
            }
        )


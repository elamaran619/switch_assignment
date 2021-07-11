import asyncio
import logging
import traceback

import aiohttp.web
from ocpp.exceptions import OCPPError, ValidationError

from charger.charger import ChargePoint

from aiohttp import web

from common.constants import *
from common.ocpp_message_type import OcppMessageType


class ChargerApi:
    def __init__(self, cp: ChargePoint, port: int = 8080):
        self.cp = cp
        self.port = port

    def _initialize_routes(self, app):
        app.router.add_get('/', self.get_version)
        app.router.add_post('/status_notification', self.send_status_notification)

    # Preliminary data validation
    def _validate_send_notification_message(self, payload):
        if not payload:
            raise ValueError('{}')

        for field in [FIELD_CONNECTOR_STATUS, FIELD_CONNECTOR_ID]:
            if field not in payload:
                raise ValueError(field)

        if not isinstance(payload[FIELD_CONNECTOR_ID], int) or \
                not self.cp.has_connector_with_id(payload[FIELD_CONNECTOR_ID]):
            raise ValueError(FIELD_CONNECTOR_ID)

    async def start(self):
        logging.info(f"Starting local REST API Server on 'localhost' on port {self.port}")

        app = web.Application()

        self._initialize_routes(app)

        runner = aiohttp.web.AppRunner(app)
        await runner.setup()

        site = aiohttp.web.TCPSite(
            runner=runner,
            port=self.port,
            host='0.0.0.0'
        )
        await site.start()

        # Serve forever
        while True:
            await asyncio.sleep(3600)

    @staticmethod
    def get_version(request):
        return web.json_response({
            FIELD_JSON_NAME: 'OCPP CP Rest API',
            FIELD_JSON_VERSION: '0.0.1'
        })

    async def send_status_notification(self, request):
        try:
            payload = await request.json()

            self._validate_send_notification_message(payload)

            await self.cp.send_message(OcppMessageType.STATUS_NOTIFICATION, payload)

            return web.json_response(
                data={
                    FIELD_JSON_STATUS: VALUE_SUCCESS
                }
            )
        except (ValueError, ValidationError) as err:
            logging.error(traceback.format_exc())
            return web.json_response(
                data={
                    FIELD_JSON_STATUS: VALUE_ERROR,
                    FIELD_JSON_DETAILS: 'Invalid ocpp payload'
                },
                status=404
            )
        except OCPPError as err:
            logging.error(traceback.format_exc())
            return web.json_response(
                data={
                    FIELD_JSON_STATUS: VALUE_ERROR,
                    FIELD_JSON_DETAILS: f"Received CallError response: {str(err)}"
                },
                status=404
            )
        except Exception as err:
            logging.error(traceback.format_exc())
            return web.json_response(
                data={
                    FIELD_JSON_STATUS: VALUE_ERROR,
                    FIELD_JSON_DETAILS: 'Internal Server Error. Please check server logs'
                },
                status=500
            )

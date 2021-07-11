import asyncio
import logging
import base64

from typing import List

import websockets

from central_system.central_system import start_ocpp_server
from charger.charger import ChargePoint

from charger.charger_api import ChargerApi

from argparse import ArgumentParser

from common.constants import HEADER_AUTHORIZATION

logging.basicConfig(level=logging.INFO)


async def start_ocpp_client_components(host_url: str, cp_id: int, connectors: List[int], rest_api_port: int, user: str, password: str):
    logging.info(f'Connecting to {host_url} as {cp_id}...')

    async with websockets.connect(
        uri=f'{host_url}/{cp_id}',
        subprotocols=['ocpp2.0.1'],
        timeout=10,
        extra_headers={
            HEADER_AUTHORIZATION: 'Basic ' + base64.b64encode(f'{user}:{password}'.encode('utf-8')).decode('utf-8')
        }
    ) as ws:
        charge_point = ChargePoint(
            cp_id=cp_id,
            connection=ws,
            connector_ids=connectors
        )

        charger_api_server = ChargerApi(
            cp=charge_point,
            port=rest_api_port
        )

        await asyncio.gather(charge_point.start(),
                             charge_point.send_boot_up_sequence(),
                             charger_api_server.start())


def parse_command_line_arguments():
    parser = ArgumentParser()
    parser.add_argument("-m", "--mode", help="[Required] 1 - OCPP client and REST API, 2 - OCPP server", type=int)
    parser.add_argument("-cpid", "--charge-point-id", help="[Required] Id of charge point", type=int)
    parser.add_argument("-cids", "--connector-ids", help="[Required] Comma separated list of connector ids")
    parser.add_argument("-op", "--ocpp-port", help="Depending on mode, the OCPP WS port. Default 9000")
    parser.add_argument("-ap", "--api-port", help="Only in mode 0, port for charging station REST API. Default 8080")

    args = parser.parse_args()

    if not args.mode:
        parser.error('Please select a mode via -m')

    if args.mode not in [1, 2]:
        parser.error('Please select 1 or 2 for mode via -m')

    if not args.ocpp_port:
        parser.error('OCPP port value needed via -op argument')

    if args.mode == 1 and not args.api_port:
        parser.error('Port value is needed for REST API via -ap argument')

    if args.mode == 1 and not args.connector_ids:
        parser.error('List of connector ids is needed')

    if args.mode == 1 and not args.charge_point_id:
        parser.error('Missing CP id')

    if args.mode == 1:
        cids = []
        try:
            for cid in args.connector_ids.split(','):
                if cid and cid.strip():
                    cids.append(int(cid))
            if not cids:
                raise ValueError
        except ValueError:
            parser.error('Invalid non-integer value for connector ids')

        args.connector_ids = cids

    return args


if __name__ == '__main__':
    args = parse_command_line_arguments()
    if args.mode == 2:
        asyncio.run(
            start_ocpp_server(
                port_number=args.ocpp_port,
                user='user',
                password='password'
            )
        )
    else:
        asyncio.run(
            start_ocpp_client_components(
                host_url=f'ws://localhost:{args.ocpp_port}',
                cp_id=args.charge_point_id,
                connectors=args.connector_ids,
                rest_api_port=args.api_port,
                user='user',
                password='password'
            )
        )
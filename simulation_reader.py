
from navigation_server.navigation_clients import GrpcNmeaServerClient, GrpcClient

class CANSimulationReader:

    def __init__(self, server_address: str):
        self._client = GrpcClient(server_address)
        self._service = GrpcNmeaServerClient()
        self._client.add_service(self._service)
        self._client.connect()

    def read_nmea_stream(self):
        for msg in self._service.getNMEA():
            yield msg




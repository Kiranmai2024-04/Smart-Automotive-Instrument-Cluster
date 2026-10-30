"""Logical ECU simulators."""
from can_bus import VirtualCANBus
from vehicle_model import VehicleState, encode_engine_frame, encode_body_frame


class EngineECU:
    def __init__(self, bus: VirtualCANBus, state: VehicleState):
        self.bus, self.state = bus, state

    def transmit(self):
        self.bus.send(encode_engine_frame(self.state))


class BodyBatteryECU:
    def __init__(self, bus: VirtualCANBus, state: VehicleState):
        self.bus, self.state = bus, state

    def transmit(self):
        self.bus.send(encode_body_frame(self.state))

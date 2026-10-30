"""Vehicle state and CAN payload definitions."""
from dataclasses import dataclass
import struct
from can_bus import CANFrame

ENGINE_CAN_ID = 0x100
BODY_CAN_ID = 0x101
GEARS = ("P", "R", "N", "D")


@dataclass
class VehicleState:
    speed_kmh: float = 62.0
    rpm: int = 2200
    engine_temp_c: float = 88.0
    fuel_percent: float = 72.0
    battery_voltage: float = 13.8
    gear: int = 3
    seatbelt_fastened: bool = True
    door_open: bool = False


def encode_engine_frame(state: VehicleState) -> CANFrame:
    """ID 0x100: speed(0.1 km/h), RPM, temperature(0.1 C), gear, reserved."""
    payload = struct.pack(
        ">HHHBB",
        max(0, min(65535, round(state.speed_kmh * 10))),
        max(0, min(65535, int(state.rpm))),
        max(0, min(65535, round(state.engine_temp_c * 10))),
        max(0, min(255, int(state.gear))),
        0,
    )
    return CANFrame(ENGINE_CAN_ID, payload)


def decode_engine_frame(frame: CANFrame) -> dict:
    if frame.arbitration_id != ENGINE_CAN_ID or len(frame.data) != 8:
        raise ValueError("Not a valid engine ECU frame")
    speed, rpm, temp, gear, _ = struct.unpack(">HHHBB", frame.data)
    return {"speed_kmh": speed / 10, "rpm": rpm,
            "engine_temp_c": temp / 10, "gear": gear}


def encode_body_frame(state: VehicleState) -> CANFrame:
    """ID 0x101: fuel(0.1%), battery(0.01 V), seatbelt, door, reserved."""
    payload = struct.pack(
        ">HHBBBB",
        max(0, min(65535, round(state.fuel_percent * 10))),
        max(0, min(65535, round(state.battery_voltage * 100))),
        int(state.seatbelt_fastened),
        int(state.door_open),
        0,
        0,
    )
    return CANFrame(BODY_CAN_ID, payload)


def decode_body_frame(frame: CANFrame) -> dict:
    if frame.arbitration_id != BODY_CAN_ID or len(frame.data) != 8:
        raise ValueError("Not a valid body ECU frame")
    fuel, battery, seatbelt, door, _, _ = struct.unpack(">HHBBBB", frame.data)
    return {"fuel_percent": fuel / 10, "battery_voltage": battery / 100,
            "seatbelt_fastened": bool(seatbelt), "door_open": bool(door)}

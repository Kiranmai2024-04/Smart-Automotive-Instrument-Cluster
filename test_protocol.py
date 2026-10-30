import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import unittest
from can_bus import CANFrame, VirtualCANBus
from vehicle_model import (
    VehicleState, encode_engine_frame, decode_engine_frame,
    encode_body_frame, decode_body_frame, ENGINE_CAN_ID, BODY_CAN_ID
)
from diagnostics import evaluate_warnings


class CANProtocolTests(unittest.TestCase):
    def test_engine_round_trip(self):
        state = VehicleState(speed_kmh=123.4, rpm=3456, engine_temp_c=92.5, gear=2)
        frame = encode_engine_frame(state)
        decoded = decode_engine_frame(frame)
        self.assertEqual(frame.arbitration_id, ENGINE_CAN_ID)
        self.assertEqual(len(frame.data), 8)
        self.assertEqual(decoded["speed_kmh"], 123.4)
        self.assertEqual(decoded["rpm"], 3456)
        self.assertEqual(decoded["engine_temp_c"], 92.5)
        self.assertEqual(decoded["gear"], 2)

    def test_body_round_trip(self):
        state = VehicleState(fuel_percent=24.5, battery_voltage=12.6,
                             seatbelt_fastened=False, door_open=True)
        frame = encode_body_frame(state)
        decoded = decode_body_frame(frame)
        self.assertEqual(frame.arbitration_id, BODY_CAN_ID)
        self.assertEqual(len(frame.data), 8)
        self.assertEqual(decoded["fuel_percent"], 24.5)
        self.assertEqual(decoded["battery_voltage"], 12.6)
        self.assertFalse(decoded["seatbelt_fastened"])
        self.assertTrue(decoded["door_open"])

    def test_invalid_frame_size(self):
        with self.assertRaises(ValueError):
            CANFrame(0x100, b"123456789")

    def test_invalid_identifier(self):
        with self.assertRaises(ValueError):
            CANFrame(0x800, b"")

    def test_virtual_bus(self):
        bus = VirtualCANBus()
        frame = CANFrame(0x100, b"123")
        bus.send(frame)
        self.assertEqual(bus.receive_all(), [frame])
        self.assertEqual(bus.receive_all(), [])

    def test_warning_rules(self):
        data = {"engine_temp_c": 115, "battery_voltage": 10.8,
                "fuel_percent": 5, "seatbelt_fastened": False, "door_open": True}
        warnings = evaluate_warnings(data)
        self.assertIn("CRITICAL ENGINE OVERHEAT", warnings)
        self.assertIn("LOW BATTERY VOLTAGE", warnings)
        self.assertIn("LOW FUEL", warnings)
        self.assertIn("SEATBELT NOT FASTENED", warnings)
        self.assertIn("DOOR OPEN", warnings)


if __name__ == "__main__":
    unittest.main()

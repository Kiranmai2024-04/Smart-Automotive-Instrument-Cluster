"""Educational in-process CAN-style bus (not a physical CAN implementation)."""
from dataclasses import dataclass
from queue import Queue, Empty
from typing import List


@dataclass(frozen=True)
class CANFrame:
    arbitration_id: int
    data: bytes

    def __post_init__(self):
        if not 0 <= self.arbitration_id <= 0x7FF:
            raise ValueError("Standard CAN ID must be between 0x000 and 0x7FF")
        if len(self.data) > 8:
            raise ValueError("Classic CAN payload cannot exceed 8 bytes")


class VirtualCANBus:
    """A simple queue-based message transport for simulated ECUs."""
    def __init__(self):
        self._queue = Queue()

    def send(self, frame: CANFrame) -> None:
        self._queue.put(frame)

    def receive_all(self) -> List[CANFrame]:
        frames = []
        while True:
            try:
                frames.append(self._queue.get_nowait())
            except Empty:
                break
        return frames

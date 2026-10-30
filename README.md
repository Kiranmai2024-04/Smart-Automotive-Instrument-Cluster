# Smart Automotive Digital Instrument Cluster with CAN-Based Vehicle Diagnostics

A simulation-only educational prototype demonstrating a digital vehicle dashboard, logical ECUs,
CAN-style message encoding/decoding, and threshold-based diagnostics.

## Features
- Digital dashboard: speed, RPM, gear, fuel, engine temperature, battery voltage
- Logical Engine ECU and Body/Battery ECU
- CAN-style standard 11-bit message identifiers and classic 8-byte payloads
- Virtual in-process message bus
- Warning logic for overtemperature, low battery, low fuel, seatbelt and open door
- Live simulated sensor controls
- CAN frame monitor
- Unit tests for protocol encoding/decoding and diagnostics

## Requirements
- Python 3.9+
- Tkinter (usually included with Python; Linux may require `python3-tk`)
- No third-party Python packages

## Run the application

From the project root:

```bash
python src/dashboard.py
```

## Run tests

```bash
python -m unittest discover -s tests -v
```

## Architecture

```text
Engine ECU -------------------\
  speed, RPM, temperature      \
                                > Virtual CAN Bus --> Instrument Cluster
Body/Battery ECU --------------/                      decode --> Dashboard
  fuel, battery, switches                             diagnostics --> Alerts
```

## CAN-style message definitions

This prototype uses two standard 11-bit identifiers. The payloads are encoded in
big-endian byte order and are limited to 8 bytes, as in Classical CAN.

### ID 0x100 — Engine ECU (8 bytes)
| Bytes | Field | Encoding |
|---|---|---|
| 0–1 | Speed | unsigned integer, 0.1 km/h per bit |
| 2–3 | RPM | unsigned integer, 1 RPM per bit |
| 4–5 | Engine temperature | unsigned integer, 0.1 °C per bit |
| 6 | Gear | 0=P, 1=R, 2=N, 3=D |
| 7 | Reserved | 0 |

### ID 0x101 — Body/Battery ECU (8 bytes)
| Bytes | Field | Encoding |
|---|---|---|
| 0–1 | Fuel | unsigned integer, 0.1% per bit |
| 2–3 | Battery voltage | unsigned integer, 0.01 V per bit |
| 4 | Seatbelt | 1=fastened, 0=unfastened |
| 5 | Door | 1=open, 0=closed |
| 6–7 | Reserved | 0 |

The queue is an in-process software transport. It demonstrates message formatting,
identifier-based routing, transmission, reception and decoding. It does **not**
simulate physical CAN signalling, arbitration, bit timing, bus load, error frames,
termination or a real transceiver.

## Illustrative warning thresholds
- Engine temperature >= 110 °C: critical overheat
- Battery voltage < 11.5 V: low battery
- Fuel <= 10%: low fuel
- Seatbelt unfastened: warning
- Door open: warning

These values are for demonstration only and are not OEM calibration values or
safety-certified vehicle requirements.

## Test plan
| Test | Input | Expected result |
|---|---|---|
| TC01 | 88 °C, 13.8 V, fuel 72% | Normal status |
| TC02 | Temperature 105 °C | High temperature warning |
| TC03 | Temperature 115 °C | Critical overheat warning |
| TC04 | Battery 10.8 V | Low battery warning |
| TC05 | Fuel 5% | Low fuel warning |
| TC06 | Seatbelt unfastened | Seatbelt warning |
| TC07 | Door open | Door warning |
| TC08 | Change speed and RPM sliders | Dashboard values update |
| TC09 | Change gear | P/R/N/D indicator updates |
| TC10 | Observe CAN monitor | IDs 0x100 and 0x101, each DLC 8 |

## Safety and scope
This is a desktop simulation for learning and portfolio demonstration. It is not intended
for installation in, connection to, or control of a real vehicle. Do not connect a
microcontroller directly to automotive battery or vehicle CAN wiring. A physical
prototype requires appropriate automotive-grade protection, a CAN transceiver,
hardware design review and validation.

## Suggested future work
- Replace the in-process queue with a CAN simulation tool or SocketCAN virtual interface
- Add message timeout and communication-loss detection
- Add CRC/counter concepts for message integrity
- Add configurable DBC-style signal definitions
- Add event logging and fault history
- Port ECU logic to Embedded C and validate on an STM32 board

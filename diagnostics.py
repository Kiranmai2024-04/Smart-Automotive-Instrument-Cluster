"""Illustrative dashboard warning rules; not OEM safety calibration."""
def evaluate_warnings(data: dict) -> list:
    warnings = []
    temp = data.get("engine_temp_c", 0)
    battery = data.get("battery_voltage", 12)
    fuel = data.get("fuel_percent", 100)

    if temp >= 110:
        warnings.append("CRITICAL ENGINE OVERHEAT")
    elif temp >= 100:
        warnings.append("HIGH ENGINE TEMPERATURE")
    if battery < 11.5:
        warnings.append("LOW BATTERY VOLTAGE")
    if fuel <= 10:
        warnings.append("LOW FUEL")
    if not data.get("seatbelt_fastened", True):
        warnings.append("SEATBELT NOT FASTENED")
    if data.get("door_open", False):
        warnings.append("DOOR OPEN")
    return warnings

"""Tkinter digital instrument cluster dashboard."""
import tkinter as tk
from tkinter import ttk

from can_bus import VirtualCANBus
from diagnostics import evaluate_warnings
from ecus import EngineECU, BodyBatteryECU
from vehicle_model import (
    VehicleState, GEARS, ENGINE_CAN_ID, BODY_CAN_ID,
    decode_engine_frame, decode_body_frame,
)

BG = "#101820"
PANEL = "#182630"
PANEL_ALT = "#203541"
TEXT = "#EAF2F5"
MUTED = "#9FB2BC"
CYAN = "#45D6E8"
GREEN = "#58D68D"
RED = "#FF5C5C"


class InstrumentClusterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Cockpit | Automotive Instrument Cluster")
        self.root.geometry("1120x790")
        self.root.minsize(980, 700)
        self.root.configure(bg=BG)

        self.bus = VirtualCANBus()
        self.vehicle = VehicleState()
        self.engine_ecu = EngineECU(self.bus, self.vehicle)
        self.body_ecu = BodyBatteryECU(self.bus, self.vehicle)
        self.received = {}
        self.running = True
        self._build_ui()
        self._update_loop()

    def panel(self, parent, title):
        frame = tk.Frame(parent, bg=PANEL, highlightbackground="#314955", highlightthickness=1)
        tk.Label(frame, text=title, bg=PANEL, fg=MUTED,
                 font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=14, pady=(10, 3))
        return frame

    def value_label(self, parent, text, unit="", size=28, color=TEXT):
        label = tk.Label(parent, text=f"{text}{unit}", bg=PANEL, fg=color,
                         font=("Segoe UI", size, "bold"))
        label.pack(anchor="w", padx=14, pady=(0, 10))
        return label

    def _build_ui(self):
        header = tk.Frame(self.root, bg=BG)
        header.pack(fill="x", padx=22, pady=(16, 8))
        tk.Label(header, text="SMART COCKPIT", bg=BG, fg=TEXT,
                 font=("Segoe UI", 23, "bold")).pack(side="left")
        tk.Label(header, text="AUTOMOTIVE DIGITAL INSTRUMENT CLUSTER",
                 bg=BG, fg=CYAN, font=("Segoe UI", 9, "bold")).pack(side="left", padx=16)
        tk.Label(header, text="● SIMULATION ONLINE", bg=BG, fg=GREEN,
                 font=("Segoe UI", 9, "bold")).pack(side="right")

        top = tk.Frame(self.root, bg=BG)
        top.pack(fill="x", padx=22, pady=6)
        self.speed_label = self._metric(top, "VEHICLE SPEED", "62.0 km/h", CYAN)
        self.rpm_label = self._metric(top, "ENGINE SPEED", "2200 RPM", TEXT)
        self.gear_label = self._metric(top, "GEAR", "D", GREEN)

        gauges = tk.Frame(self.root, bg=BG)
        gauges.pack(fill="x", padx=22, pady=6)
        self.fuel_label = self._metric(gauges, "FUEL LEVEL", "72.0 %", TEXT)
        self.temp_label = self._metric(gauges, "ENGINE TEMPERATURE", "88.0 °C", TEXT)
        self.battery_label = self._metric(gauges, "BATTERY VOLTAGE", "13.80 V", TEXT)

        warn = self.panel(self.root, "WARNINGS & DIAGNOSTICS")
        warn.pack(fill="x", padx=22, pady=6)
        self.warning_label = tk.Label(warn, text="✓ All monitored values normal",
                                      bg=PANEL, fg=GREEN, justify="left",
                                      font=("Segoe UI", 11, "bold"))
        self.warning_label.pack(anchor="w", padx=14, pady=(4, 12))

        bottom = tk.Frame(self.root, bg=BG)
        bottom.pack(fill="both", expand=True, padx=22, pady=6)
        controls = self.panel(bottom, "SIMULATED SENSOR INPUTS")
        controls.pack(side="left", fill="both", expand=True, padx=(0, 7))
        self.vars = {}
        self._slider(controls, "Speed (km/h)", "speed", 0, 220, 62)
        self._slider(controls, "Engine RPM", "rpm", 0, 8000, 2200)
        self._slider(controls, "Temperature (°C)", "temp", 40, 140, 88)
        self._slider(controls, "Fuel (%)", "fuel", 0, 100, 72)
        self._slider(controls, "Battery (V)", "battery", 9, 16, 13.8, 0.1)

        switch_row = tk.Frame(controls, bg=PANEL)
        switch_row.pack(fill="x", padx=12, pady=6)
        self.seatbelt_var = tk.BooleanVar(value=True)
        self.door_var = tk.BooleanVar(value=False)
        tk.Checkbutton(switch_row, text="Seatbelt fastened", variable=self.seatbelt_var,
                       bg=PANEL, fg=TEXT, selectcolor=PANEL_ALT,
                       activebackground=PANEL, activeforeground=TEXT).pack(side="left")
        tk.Checkbutton(switch_row, text="Door open", variable=self.door_var,
                       bg=PANEL, fg=TEXT, selectcolor=PANEL_ALT,
                       activebackground=PANEL, activeforeground=TEXT).pack(side="left", padx=10)

        gear_row = tk.Frame(controls, bg=PANEL)
        gear_row.pack(fill="x", padx=12, pady=(2, 12))
        tk.Label(gear_row, text="Gear:", bg=PANEL, fg=MUTED).pack(side="left")
        self.gear_var = tk.StringVar(value="D")
        gear_box = ttk.Combobox(gear_row, textvariable=self.gear_var,
                                values=list(GEARS), state="readonly", width=5)
        gear_box.pack(side="left", padx=8)

        log = self.panel(bottom, "VIRTUAL CAN BUS MONITOR")
        log.pack(side="left", fill="both", expand=True, padx=(7, 0))
        self.log_text = tk.Text(log, bg="#0B1218", fg=GREEN, relief="flat",
                                font=("Consolas", 9), height=15, wrap="word")
        self.log_text.pack(fill="both", expand=True, padx=12, pady=10)
        self.log_text.insert("end", "Virtual CAN monitor ready.\n11-bit IDs | Classic CAN payload: max 8 bytes\n\n")
        self.log_text.configure(state="disabled")

        tk.Label(self.root,
                 text="EDUCATIONAL SOFTWARE SIMULATION — NOT FOR CONNECTION TO A REAL VEHICLE",
                 bg=BG, fg=MUTED, font=("Segoe UI", 8)).pack(pady=(2, 9))

    def _metric(self, parent, title, initial, color):
        frame = self.panel(parent, title)
        frame.pack(side="left", fill="both", expand=True, padx=5)
        return self.value_label(frame, initial, size=27, color=color)

    def _slider(self, parent, title, key, low, high, initial, resolution=1):
        row = tk.Frame(parent, bg=PANEL)
        row.pack(fill="x", padx=12, pady=2)
        tk.Label(row, text=title, bg=PANEL, fg=MUTED,
                 font=("Segoe UI", 9)).pack(anchor="w")
        var = tk.DoubleVar(value=initial)
        tk.Scale(row, from_=low, to=high, resolution=resolution, variable=var,
                 orient="horizontal", showvalue=True, bg=PANEL, fg=TEXT,
                 troughcolor=PANEL_ALT, highlightthickness=0,
                 activebackground=CYAN, length=340).pack(fill="x")
        self.vars[key] = var

    def _write_log(self, frame):
        line = f"ID 0x{frame.arbitration_id:03X} | DLC {len(frame.data)} | {frame.data.hex(' ').upper()}\n"
        self.log_text.configure(state="normal")
        self.log_text.insert("end", line)
        self.log_text.see("end")
        if int(self.log_text.index("end-1c").split(".")[0]) > 35:
            self.log_text.delete("1.0", "6.0")
        self.log_text.configure(state="disabled")

    def _update_loop(self):
        if not self.running:
            return

        v = self.vehicle
        v.speed_kmh = self.vars["speed"].get()
        v.rpm = int(self.vars["rpm"].get())
        v.engine_temp_c = self.vars["temp"].get()
        v.fuel_percent = self.vars["fuel"].get()
        v.battery_voltage = self.vars["battery"].get()
        v.seatbelt_fastened = self.seatbelt_var.get()
        v.door_open = self.door_var.get()
        v.gear = GEARS.index(self.gear_var.get())

        self.engine_ecu.transmit()
        self.body_ecu.transmit()

        for frame in self.bus.receive_all():
            if frame.arbitration_id == ENGINE_CAN_ID:
                self.received.update(decode_engine_frame(frame))
            elif frame.arbitration_id == BODY_CAN_ID:
                self.received.update(decode_body_frame(frame))
            self._write_log(frame)

        d = self.received
        self.speed_label.configure(text=f"{d['speed_kmh']:.1f} km/h")
        self.rpm_label.configure(text=f"{d['rpm']} RPM")
        self.gear_label.configure(text=GEARS[d['gear']])
        self.fuel_label.configure(text=f"{d['fuel_percent']:.1f} %")
        self.temp_label.configure(text=f"{d['engine_temp_c']:.1f} °C")
        self.battery_label.configure(text=f"{d['battery_voltage']:.2f} V")

        warnings = evaluate_warnings(d)
        if warnings:
            self.warning_label.configure(text="⚠  " + "\n⚠  ".join(warnings), fg=RED)
        else:
            self.warning_label.configure(text="✓ All monitored values normal", fg=GREEN)

        self.root.after(200, self._update_loop)

    def close(self):
        self.running = False
        self.root.destroy()


def main():
    root = tk.Tk()
    app = InstrumentClusterApp(root)
    root.protocol("WM_DELETE_WINDOW", app.close)
    root.mainloop()


if __name__ == "__main__":
    main()

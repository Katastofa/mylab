"""Плата-пример: USB-C (5 В) -> 3.3 В, индикатор питания, выводы на гребёнку.

    python usb_c_3v3.py         # ERC + build/usb_c_3v3.net для PCB Editor
    python usb_c_3v3.py --sch   # + схема в build/sch/ для просмотра
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "lib"))

import kicad_env  # noqa: E402,F401  — должен идти до skidl

from skidl import POWER, Net  # noqa: E402

from blocks import indicator_led, ldo_3v3, pin_header, usb_c_power  # noqa: E402
from build import build  # noqa: E402

# --- Цепи -------------------------------------------------------------------
vbus = Net("+5V")
v3v3 = Net("+3V3")
gnd = Net("GND")
for n in (vbus, v3v3, gnd):
    n.drive = POWER  # питание приходит извне платы — подсказка для ERC

# --- Схема ------------------------------------------------------------------
# tag — стабильное имя экземпляра блока. Из тегов SKiDL строит UUID
# компонентов, и KiCad при повторном импорте netlist не теряет расстановку.
usb_c_power(vbus, gnd, tag="usb")
ldo_3v3(vbus, v3v3, gnd, tag="ldo")
indicator_led(v3v3, gnd, r_value="1k", color="green", tag="pwr_led")
pin_header([vbus, v3v3, gnd, gnd], tag="out")

if __name__ == "__main__":
    build(__file__, title="USB-C -> 3.3V")

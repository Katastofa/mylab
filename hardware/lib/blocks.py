"""Переиспользуемые блоки схем на SKiDL.

Каждый блок — функция с декоратором @subcircuit: принимает цепи (Net)
и сама создаёт нужные компоненты. Блоки можно собирать в любые платы.
"""

from skidl import Part, subcircuit

# Футпринты по умолчанию для пассивки (0603 — удобно паять руками).
R_FP = "Resistor_SMD:R_0603_1608Metric"
C_FP = "Capacitor_SMD:C_0603_1608Metric"
LED_FP = "LED_SMD:LED_0603_1608Metric"
C_BULK_FP = "Capacitor_SMD:C_0805_2012Metric"  # 10–22 мкФ


def resistor(value, tag, fp=R_FP):
    return Part("Device", "R", value=value, footprint=fp, tag=tag)


def capacitor(value, tag, fp=C_FP):
    return Part("Device", "C", value=value, footprint=fp, tag=tag)


@subcircuit
def usb_c_power(vbus, gnd):
    """Разъём USB-C только для питания: 5 В от любого источника USB-C.

    Резисторы 5.1 кОм на CC1/CC2 говорят зарядке, что мы потребитель (sink).
    """
    j = Part(
        "Connector",
        "USB_C_Receptacle_PowerOnly_6P",
        tag="conn",
        footprint="Connector_USB:USB_C_Receptacle_GCT_USB4125-xx-x_6P_TopMnt_Horizontal",
    )
    vbus += j["VBUS"]
    gnd += j["GND"], j["SHIELD"]
    for cc in ("CC1", "CC2"):
        r = resistor("5.1k", tag=f"r_{cc.lower()}")
        j[cc] & r & gnd


@subcircuit
def ldo_3v3(vin, vout, gnd):
    """Линейный стабилизатор AMS1117-3.3 с конденсаторами на входе и выходе."""
    u = Part("Regulator_Linear", "AMS1117-3.3", tag="reg")  # футпринт SOT-223 берётся из библиотеки
    vin += u["VI"]
    vout += u["VO"]
    gnd += u["GND"]
    vin & capacitor("10u", tag="c_in", fp=C_BULK_FP) & gnd
    vout & capacitor("22u", tag="c_out", fp=C_BULK_FP) & gnd


@subcircuit
def indicator_led(vcc, gnd, r_value="1k", color="green"):
    """Светодиод с токоограничивающим резистором."""
    led = Part("Device", "LED", value=color, footprint=LED_FP, tag="led")
    vcc & resistor(r_value, tag="r") & led["A K"] & gnd


@subcircuit
def pin_header(nets, ref_prefix="J"):
    """Штыревой разъём 2.54 мм; nets — список цепей по порядку пинов."""
    n = len(nets)
    j = Part(
        "Connector_Generic",
        f"Conn_01x{n:02d}",
        footprint=f"Connector_PinHeader_2.54mm:PinHeader_1x{n:02d}_P2.54mm_Vertical",
        ref_prefix=ref_prefix,
        tag="conn",
    )
    for i, net in enumerate(nets, start=1):
        net += j[i]
    return j

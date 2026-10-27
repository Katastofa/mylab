"""Общий запуск для скриптов плат: ERC, netlist и (по флагу) схема.

    python <board>.py          # ERC + build/<board>.net
    python <board>.py --sch    # + build/sch/<board>.kicad_sch (только для просмотра)
"""

import argparse
import sys
from pathlib import Path

import skidl
from skidl.logger import erc_logger


def build(board_file, title=""):
    here = Path(board_file).resolve().parent
    name = Path(board_file).stem
    out = here / "build"
    out.mkdir(exist_ok=True)

    ap = argparse.ArgumentParser(description=f"Сборка платы {name}")
    ap.add_argument("--sch", action="store_true", help="сгенерировать схему KiCad")
    args = ap.parse_args()

    skidl.ERC()
    erc_errors = erc_logger.error.count + erc_logger.bare_error.count
    if erc_errors:
        sys.exit(f"ERC: {erc_errors} ошибок — netlist не создан, см. {name}.erc")

    skidl.generate_netlist(file_=str(out / f"{name}.net"))
    print(f"netlist: {out / (name + '.net')}")

    if args.sch:
        skidl.generate_schematic(
            filepath=str(out / "sch"), top_name=name, title=title or name
        )
        print(f"schematic: {out / 'sch' / (name + '.kicad_sch')}")

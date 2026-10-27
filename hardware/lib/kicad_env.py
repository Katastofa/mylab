"""Настройка окружения SKiDL под установленный KiCad.

Импортируйте этот модуль ДО skidl: он находит библиотеки символов KiCad
и выставляет переменные окружения, которые SKiDL читает при импорте.

Версия KiCad задаётся переменной SKIDL_KICAD (по умолчанию 9).
"""

import os
import sys
from pathlib import Path

KICAD_VERSION = os.environ.get("SKIDL_KICAD", "9")

# Типичные места установки библиотек KiCad (KiCad N.0).
_CANDIDATES = [
    "/usr/share/kicad",  # Linux (apt, flatpak-экспорт)
    "/usr/local/share/kicad",
    f"C:/Program Files/KiCad/{KICAD_VERSION}.0/share/kicad",  # Windows
    "/Applications/KiCad/KiCad.app/Contents/SharedSupport",  # macOS
]


def _find_share():
    for var in (f"KICAD{KICAD_VERSION}_SYMBOL_DIR", "KICAD_SYMBOL_DIR"):
        if os.environ.get(var):
            return Path(os.environ[var]).parent
    for c in _CANDIDATES:
        if (Path(c) / "symbols").is_dir():
            return Path(c)
    return None


share = _find_share()
if share is None:
    sys.exit(
        "Не найдены библиотеки символов KiCad. Укажите путь вручную, например:\n"
        f"  export KICAD{KICAD_VERSION}_SYMBOL_DIR=/path/to/kicad/symbols"
    )

# Заполняем переменные для всех версий, чтобы SKiDL не шумел предупреждениями.
for prefix in ["KICAD"] + [f"KICAD{v}" for v in range(5, 11)]:
    os.environ.setdefault(f"{prefix}_SYMBOL_DIR", str(share / "symbols"))
    os.environ.setdefault(f"{prefix}_FOOTPRINT_DIR", str(share / "footprints"))

import skidl  # noqa: E402

TOOL = getattr(skidl, f"KICAD{KICAD_VERSION}")
skidl.set_default_tool(TOOL)

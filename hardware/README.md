# Платы: SKiDL + KiCad

Схема пишется кодом на Python ([SKiDL](https://github.com/devbisme/skidl)),
а KiCad используется для разводки платы и выпуска файлов на производство.

```
boards/<плата>/<плата>.py ──SKiDL──▶ build/<плата>.net ──импорт──▶ <плата>.kicad_pcb ──▶ gerbers
          (источник правды)     │      (netlist)                      (разводка руками)
                                └──▶ build/sch/*.kicad_sch  (схема только для просмотра)
```

Что лежит в git:

| Файл                    | Кто правит        | Зачем                                   |
|-------------------------|-------------------|-----------------------------------------|
| `boards/*/*.py`         | человек           | схема: компоненты, цепи, футпринты      |
| `lib/blocks.py`         | человек           | переиспользуемые блоки (`@subcircuit`)  |
| `boards/*/*.kicad_pcb`  | человек, в KiCad  | расстановка и трассировка               |
| `boards/*/*.kicad_pro`  | KiCad             | настройки проекта (правила DRC и т. п.) |
| `build/`                | генерируется      | netlist, схема, gerbers — не коммитим   |

## Установка

1. KiCad 9 (подойдёт и 8): https://www.kicad.org/download/
2. Python-зависимости:
   ```sh
   cd hardware
   python3 -m venv .venv && . .venv/bin/activate   # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. Библиотеки символов KiCad ищутся автоматически (`lib/kicad_env.py`).
   Если не нашлись — укажите путь вручную:
   ```sh
   export KICAD9_SYMBOL_DIR="/path/to/kicad/symbols"
   ```
   Для другой версии KiCad: `export SKIDL_KICAD=8`.

## Цикл работы

1. **Правим схему** в `boards/<плата>/<плата>.py`.
2. **Собираем**:
   ```sh
   cd boards/usb_c_3v3
   python usb_c_3v3.py --sch
   ```
   Запускается ERC (при ошибках netlist не создаётся), затем пишутся
   `build/usb_c_3v3.net` и схема `build/sch/usb_c_3v3.kicad_sch`.
3. **Обновляем плату**: открываем `usb_c_3v3.kicad_pro` → PCB Editor →
   `File → Import → Netlist…` → выбираем `build/usb_c_3v3.net` →
   *Link footprints using: Symbol UUIDs* (по умолчанию) → `Update PCB`.
   Новые компоненты появятся рядом с платой, удалённые пропадут,
   расставленные останутся на месте.
4. **Разводим** в KiCad, проверяем DRC, коммитим `.py` и `.kicad_pcb` вместе.
5. **Производство**: `make fab` (или артефакт CI) → `build/fab/` с gerbers,
   сверловкой, файлом расстановки и DRC-отчётом.

Сгенерированную схему не редактируем: при следующей сборке она перезапишется.
Она нужна, чтобы глазами проверить связи и приложить PDF к ревью.

### Почему расстановка не слетает

У каждого блока и компонента есть `tag`. Из цепочки тегов
(`usb/r_cc1`, `ldo/c_out`…) SKiDL строит стабильный UUID, и KiCad сопоставляет
футпринты по нему, а не по позиционному обозначению. Поэтому:

- теги задаём всегда и не меняем без нужды — смена тега = «новый» компонент;
- R1/C3 могут перенумероваться — это нормально.

## Новая плата

```sh
mkdir boards/my_board
cp boards/usb_c_3v3/usb_c_3v3.py boards/my_board/my_board.py
```

Правим схему, собираем, затем в KiCad: `File → New Project` в
`boards/my_board/` с именем `my_board`, открываем PCB Editor, рисуем контур
на слое `Edge.Cuts` и импортируем netlist (шаг 3).

## Как писать схему

```python
from skidl import Net, Part, subcircuit

@subcircuit
def indicator_led(vcc, gnd, r_value="1k", color="green"):
    led = Part("Device", "LED", value=color,
               footprint="LED_SMD:LED_0603_1608Metric", tag="led")
    vcc & resistor(r_value, tag="r") & led["A K"] & gnd   # последовательная цепочка

indicator_led(v3v3, gnd, tag="pwr_led")
```

- `Part("Библиотека", "Символ", footprint="Библиотека:Футпринт")` — имена те же,
  что в KiCad (Symbol Editor / Footprint Editor).
- `net += part["PIN"]` — подключить вывод к цепи; `a & b & c` — последовательно.
- Пины можно звать по имени (`"VO"`) или номеру (`1`).
- Посмотреть выводы символа:
  `python -c "import sys; sys.path.insert(0,'lib'); import kicad_env; from skidl import *; print(Part('Regulator_Linear','AMS1117-3.3',dest=TEMPLATE))"`

## CI

`.github/workflows/hardware.yml` на каждый push в `hardware/` собирает все
платы в контейнере `kicad/kicad:9.0`: ERC, netlist, схема (PDF), DRC-отчёт,
gerbers. Всё это лежит в артефакте `hardware-build` у прогона.
DRC пока не валит сборку (пример ещё не разведён) — когда плата будет готова,
уберите `|| true` у `pcb drc` в `Makefile` и добавьте `--exit-code-violations`.

## Пример: `boards/usb_c_3v3`

USB-C (только питание, 5 В) → AMS1117-3.3 → 3.3 В, светодиод питания,
гребёнка `+5V / +3V3 / GND / GND`. Футпринты расставлены, контур 36×22 мм
нарисован — осталось развести дорожки.

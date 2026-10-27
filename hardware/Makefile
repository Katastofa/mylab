# SKiDL + KiCad: сборка всех плат из hardware/boards/<имя>/<имя>.py
#
#   make            — ERC + netlist + схема для всех плат
#   make fab        — + DRC и файлы для производства (нужен kicad-cli 8+)
#   make BOARDS=usb_c_3v3 fab   — только одна плата

PYTHON ?= python3
BOARDS ?= $(notdir $(wildcard boards/*))

.PHONY: all fab clean $(BOARDS)

all: $(BOARDS)

$(BOARDS):
	cd boards/$@ && $(PYTHON) $@.py --sch

fab: all
	@for b in $(BOARDS); do \
	  d=boards/$$b; pcb=$$d/$$b.kicad_pcb; out=$$d/build/fab; \
	  [ -f $$pcb ] || { echo "$$b: нет $$pcb, пропускаю fab"; continue; }; \
	  mkdir -p $$out/gerbers; \
	  kicad-cli sch export pdf -o $$d/build/$$b-schematic.pdf $$d/build/sch/$$b.kicad_sch; \
	  kicad-cli pcb drc -o $$out/drc.rpt $$pcb || true; \
	  kicad-cli pcb export gerbers -o $$out/gerbers/ $$pcb; \
	  kicad-cli pcb export drill -o $$out/gerbers/ $$pcb; \
	  kicad-cli pcb export pos --format csv --units mm -o $$out/$$b-pos.csv $$pcb; \
	  kicad-cli pcb render -o $$out/$$b-top.png $$pcb 2>/dev/null || true; \
	  ( cd $$out && zip -qr $$b-gerbers.zip gerbers ); \
	  echo "$$b: $$out"; \
	done

clean:
	rm -rf boards/*/build boards/*/*.erc boards/*/*.log boards/*/*_sklib.py

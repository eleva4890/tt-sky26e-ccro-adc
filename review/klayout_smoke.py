"""Opened through KLayout's GUI entry point, with the exact launcher arguments."""
from pathlib import Path
import pya
review=Path(__file__).resolve().parent
view=pya.Application.instance().main_window().current_view()
cv=view.active_cellview()
assert cv.cell.name=="tt_um_eleva_ccro_adc" and cv.layout().dbu==0.001
db=view.rdb(0)
assert db and db.num_items()==17
print(f"GUI PASS  cell={cv.cell.name} dbu_um={cv.layout().dbu} markers={db.num_items()}")


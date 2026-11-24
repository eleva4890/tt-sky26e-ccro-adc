"""Extend the four low-Vt implant wells at their top and bottom edges (lvtn.10)."""
import os

import pya

layout = pya.Layout()
layout.read(os.environ["ADC_SOURCE_GDS"])
cell = layout.cell("eleva_adc_analog")
well = layout.layer(64, 20)
lvtn = pya.Region(cell.begin_shapes_rec(layout.layer(125, 44))).merged()
before = pya.Region(cell.begin_shapes_rec(well)).merged()
assert layout.dbu == 0.001  # All coordinates below are cell-local nanometres.

for x in (91100, 103100):
    for y in (12600, 21600):
        implant = pya.Box(x, y, x + 6500, y + 6400)
        if not (pya.Region(implant) - lvtn).is_empty():
            raise ValueError(f"Missing expected LV implant at {implant}")
        for lower, upper in ((implant.bottom - 450, implant.bottom),
                             (implant.top, implant.top + 450)):
            cell.shapes(well).insert(pya.Box(implant.left - 450, lower,
                                              implant.right + 450, upper))

after = pya.Region(cell.begin_shapes_rec(well)).merged()
added = after - before
if added.area() != 10360000 or added.count() != 8 or before.count() != after.count():
    raise ValueError("Unexpected change to well area, patch count or well connectivity")

options = pya.SaveLayoutOptions()
options.gds2_write_timestamps = False
layout.write(os.environ["ADC_OUTPUT_GDS"], options)
cell.write(os.environ["ADC_ANALOG_GDS"], options)

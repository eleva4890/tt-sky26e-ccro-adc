"""Separate neighbouring MIM bottom-plate feeds while preserving capacitor/oscillator geometry."""
import os
import pya

db=pya.Layout()
db.read(os.environ["ADC_SOURCE_GDS"])
analog=db.cell("eleva_adc_analog")
plates=[s.box for s in analog.shapes(db.layer(89,44)).each() if s.is_box() and s.box.width()==4500]
assert len(plates)==64,len(plates)
for plate in plates:
    x,y=plate.center().x,plate.center().y
    # M3 stems carry each oscillator output from the plate to its M2 bus.
    stems=[s for s in analog.shapes(db.layer(70,20)).each_overlapping(plate) if s.is_box()
           and s.box.center().x==x and s.box.width()==500 and s.box.height()>4500]
    if len(stems)!=1:raise ValueError((plate, [str(s) for s in stems]))
    stem=stems[0]
    up=stem.box.center().y>y
    vy=stem.box.top-250 if up else stem.box.bottom+250
    shift=-1350 if up else 1350
    for layer,dt,size in ((69,20,640),(69,44,200),(70,20,640)):
        cut=pya.Box(x-size//2,vy-size//2,x+size//2,vy+size//2)
        shapes=[s for s in analog.shapes(db.layer(layer,dt)).each_overlapping(cut)
                if s.is_box() and s.box==cut]
        if len(shapes)!=1:raise ValueError((cut,layer,dt,len(shapes)))
        shapes[0].box=cut.moved(shift,0)
    stem.box=stem.box.moved(shift,0)
    # The moved contact must still land on the original output bus.
    metal=analog.shapes(db.layer(69,20))
    metal.insert(pya.Box(min(x,x+shift)-180,vy-180,max(x,x+shift)+180,vy+180))
print("Separated",len(plates),"MIM bottom-plate feed contacts")
out=pya.SaveLayoutOptions()
out.gds2_write_timestamps=False
db.write(os.environ["ADC_OUTPUT_GDS"],out)
if os.environ.get("ADC_ANALOG_GDS"): analog.write(os.environ["ADC_ANALOG_GDS"],out)

"""Embed the complete native Xschem sheets as vector PDF forms."""
from reportlab.graphics import renderPDF
from reportlab.lib.pagesizes import A3, landscape
from reportlab.pdfbase.pdfmetrics import stringWidth
from svglib.svglib import svg2rlg


SHEETS = {"front": (25, 9), "beta_ref": (26, 9), "stage": (27, 10), "cvsl": (28, 10)}


class CircuitFigures:
    def __init__(self, canvas, assets):
        self.canvas = canvas
        self.assets = assets

    def place(self, name, target):
        drawing = svg2rlg(str(self.assets / f"xschem_{name}.svg"))
        if drawing is None:
            raise ValueError(f"Unable to load Xschem sheet {name}")
        x, y, w, h = target
        factor = min(w / drawing.width, h / drawing.height)
        c = self.canvas
        c.saveState()
        c.translate(x + (w-drawing.width*factor)/2, y + (h-drawing.height*factor)/2)
        c.scale(factor, factor)
        renderPDF.draw(drawing, c, 0, 0)
        c.restoreState()

    def appendix(self, doc, entries):
        from pdf_report import H, INK, MUTE, RULE, TEAL

        doc.endpage()
        if [row[0] for row in entries] != list(SHEETS):
            raise ValueError("Expected one full schematic for each of the four circuit figures")
        c = self.canvas
        for name, title, key, back in entries:
            page, parent = SHEETS[name]
            width, height = A3 if name == "front" else landscape(A3)
            c.setPageSize((width, height))
            c.bookmarkPage(f"p{page}")
            c.addOutlineEntry(f"{page:02d}  {title}", f"p{page}", 0)
            c.saveState()
            c.translate(0, height - H)
            doc.txt(38, 30, f"APPENDIX A  /  XSCHEM  /  review/xschem/{name}.sch", 10, "JB", TEAL)
            doc.right(width - 38, 30, f"SKY26e   /   {page:02d} · {doc.total_pages}", 9, "JB", MUTE)
            doc.rule(38, 41, width - 38, 41)
            doc.txt(38, 71, title, 20, "JB", INK)
            bottom = doc.p(38, 94, key, width - 76, 11, 16, MUTE)
            doc.rule(38, height - 43, width - 38, height - 43, RULE)
            doc.txt(38, height - 25, back, 10, "JB", TEAL)
            c.restoreState()
            c.linkRect("", f"p{parent}", (38, 19, 38 + stringWidth(back,"JB",10), 39),
                       relative=0, thickness=0)
            self.place(name, (38, 51, width - 76, height - bottom - 61))
            c.showPage()

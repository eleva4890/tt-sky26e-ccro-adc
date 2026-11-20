"""Five review panels in tile coordinates, drawn from the hash-checked released GDS."""
from layout_atlas import Atlas, FE, OUT, PALETTE, Patch, label, plt


def build():
    atlas = Atlas()
    fig = plt.figure(figsize=(9.2, 8.5), layout="constrained")
    grid = fig.add_gridspec(3, 2, height_ratios=(1.0, 0.75, 1.1))
    panels = [
        (grid[0, 0], "A   Tail sources · P side", (1, 11, 40, 35), FE),
        (grid[0, 1], "B   Rotated input quad", (87, 11, 112, 29.5), FE),
        (grid[1, 0], "C   Four resistor bodies", (6, 0, 120, 10.85), ("POLY", "TAP", "R-ID")),
        (grid[1, 1], "C   Paired rail MIM", (109, 9, 161, 36), ("M3", "M4", "CAPM")),
        (grid[2, 0], "D   Folded P ring", (0, 53.9, 78.7, 97.8), ("M2", "CAPM")),
        (grid[2, 1], "E   CVSL bank · four sites", (0, 99, 20.2, 121), FE),
    ]
    axes = []
    for position, title, box, layers in panels:
        ax = fig.add_subplot(position)
        atlas.mask(ax, title, box, layers)
        ax.set_title(title, fontsize=12, pad=6)
        ax.set_xlabel("")
        ax.set_ylabel("")
        ax.tick_params(labelsize=9)
        axes.append(ax)
    axes[2].set_yticks([0, 10])
    for x, y, name in [(105.3,15.83,"P"),(93.3,15.83,"N"),(105.3,24.83,"N"),(93.3,24.83,"P")]:
        label(axes[1], x, y, name)
    for x, net in [(123.5,"rp"),(148.7,"rn")]:
        label(axes[3], x, 22.7, net)
    for i in range(8):
        label(axes[4], 4.85+i*9.85, 65.5, str(2*i))
        label(axes[4], 4.85+i*9.85, 86.5, str(2*i+1) if i<7 else "D")
    names = list(dict.fromkeys(layer for _, _, _, layers in panels for layer in layers))
    fig.legend(handles=[Patch(color=PALETTE[name][2], label=name) for name in names],
               loc="outside lower center", ncols=5, frameon=False, fontsize=10)
    fig.savefig(OUT/"atlas_review.png", dpi=190, facecolor="white", bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    build()

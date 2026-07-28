from PIL import Image, ImageDraw, ImageFont

# Create image
img_size = (1200, 1200)
img = Image.new("RGB", img_size, "white")
draw = ImageDraw.Draw(img)

# Load font
try:
    font = ImageFont.truetype("DejaVuSans-Bold.ttf", 32)
except:
    print("Font: load_default() used")
    font = ImageFont.load_default(14)

# Color palette for pieces
colors = {
    "BS": "#FFD1DC",   # light pink
    "DN": "#C1E1C1",   # light green
    "CV": "#ADD8E6",   # light blue
    "BM": "#FFFACD",   # lemon
    "IN": "#E6E6FA",   # lavenderf
    "FT": "#F5DEB3",   # wheat
    "TP": "#FFB347",   # orange
}

# Helper to draw labeled rounded rectangle
def draw_piece(draw, xy, label, fill):
    x0, y0, x1, y1 = xy
    draw.rounded_rectangle(xy, radius=20, fill=fill, outline="black", width=3)
    lines = label.split("\n")
    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        tx = x0 + (x1 - x0 - w) / 2
        ty = y0 + (y1 - y0 - h) / 2 - 20 + i * 40
        draw.text((tx, ty), line, fill="black", font=font)

# Helper to draw arrow with label
def draw_arrow(draw, start, end, label, textpos):
    linewidth = 6
    arrowpush = 2
    draw.line([start, end], fill="black", width=linewidth)
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    length = (dx**2 + dy**2) ** 0.5
    if length == 0:
        return
    ux, uy = dx / length, dy / length
    px, py = -uy, ux
    arrow_size = 25
    dirx = dx/length
    diry = dy/length
    p1 = (end[0] - ux * arrow_size + px * arrow_size / 2 + arrowpush*dirx*linewidth,
          end[1] - uy * arrow_size + py * arrow_size / 2+ arrowpush*diry*linewidth)
    p2 = (end[0] - ux * arrow_size - px * arrow_size / 2+ arrowpush*dirx*linewidth,
          end[1] - uy * arrow_size - py * arrow_size / 2+ arrowpush*diry*linewidth)
    enda = (end[0]+ arrowpush*dirx*linewidth,
            end[1]+ arrowpush*diry*linewidth)
    draw.polygon([enda, p1, p2], fill="black")

    # Label
    lx = (start[0] + end[0]) / 2 + textpos[0]
    ly = (start[1] + end[1]) / 2 + textpos[1]
    draw.text((lx, ly), label, fill="black", font=font)

# Piece positions (scaled for 1200×1200)
positions = {
    "BS": (500, 50, 700, 200),
    "DN": (500, 260, 700, 410),
    "CV1": (230, 50, 380, 200),
    "CV2": (820, 50, 970, 200),
    "BM": (200, 500, 350, 650),
    "IN": (850, 500, 1000, 650),
    "FT": (200, 700, 350, 850),
    "TP": (900, 700, 1000, 850),

}

# Draw pieces
draw_piece(draw, positions["BS"], "BS\nBattleship", colors["BS"])
draw_piece(draw, positions["DN"], "DN\nDreadnought", colors["DN"])
draw_piece(draw, positions["CV1"], "CV\nCorvette", colors["CV"])
draw_piece(draw, positions["CV2"], "CV\nCorvette", colors["CV"])
draw_piece(draw, positions["BM"], "BM\nBomber", colors["BM"])
draw_piece(draw, positions["IN"], "IN\nInterceptor", colors["IN"])
draw_piece(draw, positions["FT"], "FT\nFighter", colors["FT"])
draw_piece(draw, positions["TP"], "TP\nTorpedo", colors["TP"])

# Arrows (all with one‑line descriptions)

# 1) BS -> DN (demotion)
draw_arrow(draw, (600, 200), (600, 260), "Battleship demotion", (9, -10))

# 2) BS -> CV + CV (decoupling)
draw_arrow(draw, (500, 100), (380, 100), "Decoupling", (-35, 3))
draw_arrow(draw, (700, 100), (820, 100), "Decoupling", (-35, 3))

# 3) DN -> IN (replace), DN -> BM (create)
draw_arrow(draw, (700, 335), (850, 575), "Replace with Interceptor", (-50, -120))
draw_arrow(draw, (500, 335), (350, 575), "Create Bomber", (15, -22))

# 4) DN -> BM (replace), DN -> IN (create)
draw_arrow(draw, (500, 335), (208, 575), "Replace with Bomber", (-150, -10))
draw_arrow(draw, (700, 335), (992, 575), "Create Interceptor", (55, 20))

# 5) BM + IN -> DN (coupling)
draw_arrow(draw, (350, 575), (600, 409), "Coupling (BM to DN)", (5, 0))
draw_arrow(draw, (850, 575), (600, 409), "Couple (IN to DN)", (-92, -80))

# 6) IN + enemy BM -> DN (boarding)
draw_arrow(draw, (857, 645), (600, 409), "Boarding (enemy BM)", (-139, 0))

# 7) CV + CV -> BS (promotion)
draw_arrow(draw, (380, 150), (500, 150), "Coupling to BS", (-50, 3))
draw_arrow(draw, (820, 150), (700, 150), "Coupling to BS", (-40, 3))

# 8) FT -> TP (promote)
draw_arrow(draw, (350, 775), (900, 775), "Fighter promotion", (-30, 10))

# Save
img.save("galactic_promotions_1200.png")
print("Saved 1200×1200 color diagram.")
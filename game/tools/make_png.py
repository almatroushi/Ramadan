"""
Create PNG images without external dependencies using raw PNG encoding.
"""
import struct, zlib, math, os

def write_png(path, width, height, pixels):
    """pixels: list of (r,g,b) tuples, row-major."""
    def chunk(name, data):
        c = struct.pack('>I', len(data)) + name + data
        c += struct.pack('>I', zlib.crc32(name + data) & 0xffffffff)
        return c

    raw = b''
    for y in range(height):
        raw += b'\x00'
        for x in range(width):
            r, g, b = pixels[y * width + x]
            raw += bytes([r, g, b])

    png = b'\x89PNG\r\n\x1a\n'
    png += chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0))
    png += chunk(b'IDAT', zlib.compress(raw, 9))
    png += chunk(b'IEND', b'')
    with open(path, 'wb') as f:
        f.write(png)

def lerp_color(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))

def clamp(v, lo, hi):
    return max(lo, min(hi, v))

# ── THUMBNAIL 1280×720 ─────────────────────────────────────────────────────────
W, H = 1280, 720
pixels = []

# Color palette
SKY_TOP    = (30, 40, 80)
SKY_BOT    = (135, 206, 235)
FLOOR_COL  = (180, 130, 80)
WALL_COL   = (240, 232, 216)
BIN_COL    = (22, 101, 52)
BIN_RIM    = (15, 74, 36)
BALL_COL   = (254, 249, 195)
FAN_COL    = (148, 163, 184)
WIND_COL   = (125, 211, 252)
TITLE_COL  = (255, 255, 255)
GLOW_COL   = (74, 222, 128)

for y in range(H):
    row = []
    for x in range(W):
        fx = x / W   # 0..1
        fy = y / H   # 0..1

        # Sky gradient (top 60%)
        if fy < 0.60:
            t = fy / 0.60
            c = lerp_color(SKY_TOP, SKY_BOT, t)
        else:
            # Floor
            t = (fy - 0.60) / 0.40
            dark = lerp_color(FLOOR_COL, (120, 80, 40), t)
            c = dark

        # ── back wall ─────────────────────────────────────────
        if 0.0 <= fy <= 0.62 and 0.0 <= fx <= 1.0:
            # simple wall band near horizon
            if 0.55 <= fy <= 0.62:
                c = lerp_color(WALL_COL, FLOOR_COL, (fy-0.55)/0.07)

        # ── TRASH BIN (right side, perspective) ───────────────
        bin_cx = int(W * 0.72)
        bin_cy = int(H * 0.54)
        bin_w  = 90
        bin_h  = 130
        # Bin body (trapezoid-like using box)
        if (abs(x - bin_cx) < bin_w // 2 and
                bin_cy - bin_h < y < bin_cy):
            # Gradient on bin
            tb = (bin_cy - y) / bin_h
            c = lerp_color(BIN_COL, (10, 60, 25), 1 - tb)
            # Green stripe
            if 0.35 < tb < 0.45:
                c = lerp_color(c, (254, 249, 195), 0.5)
        # Bin rim
        if (abs(x - bin_cx) < bin_w // 2 + 6 and
                bin_cy - bin_h - 6 < y < bin_cy - bin_h + 4):
            c = BIN_RIM

        # ── FAN (left side) ────────────────────────────────────
        fan_cx = int(W * 0.18)
        fan_cy = int(H * 0.42)
        fan_r  = 75
        fd2 = (x - fan_cx) ** 2 + (y - fan_cy) ** 2
        if fd2 < fan_r ** 2:
            # Fan cage circle
            if fan_r ** 2 - 400 < fd2 < fan_r ** 2:
                c = FAN_COL
            else:
                # Blades
                angle = math.atan2(y - fan_cy, x - fan_cx)
                blade_hit = abs(math.sin(angle * 4 + 0.5)) > 0.88
                dist = math.sqrt(fd2)
                if blade_hit and dist > 12:
                    c = lerp_color(FAN_COL, (200, 215, 230), 0.5)
                else:
                    # semi-transparent inside
                    c = lerp_color(c, FAN_COL, 0.15)
        # Fan hub
        if (x - fan_cx) ** 2 + (y - fan_cy) ** 2 < 14 ** 2:
            c = (71, 85, 105)
        # Fan stand
        if abs(x - fan_cx) < 5 and fan_cy < y < fan_cy + 120:
            c = (71, 85, 105)

        # ── WIND PARTICLES ─────────────────────────────────────
        for pi in range(8):
            px = int(W * (0.22 + pi * 0.065))
            py = int(H * (0.32 + math.sin(pi * 1.3) * 0.08))
            if abs(x - px) < 4 and abs(y - py) < 4:
                c = lerp_color(WIND_COL, (180, 230, 255), 0.4)

        # ── ARC TRAJECTORY (dotted) ────────────────────────────
        # Parabola from ball start to bin
        arc_x0 = W * 0.30
        arc_y0 = H * 0.55
        arc_x1 = W * 0.72
        arc_y1 = H * 0.35
        arc_peak = H * 0.10
        for ti in range(0, 20):
            t2 = ti / 19
            ax = arc_x0 + (arc_x1 - arc_x0) * t2
            ay = arc_y0 + (arc_y1 - arc_y0) * t2 - arc_peak * 4 * t2 * (1 - t2)
            if abs(x - ax) < 4 and abs(y - ay) < 4 and ti % 2 == 0:
                c = (255, 255, 255)

        # ── BALL ───────────────────────────────────────────────
        ball_cx = int(W * 0.30)
        ball_cy = int(H * 0.55)
        ball_r  = 32
        bd2 = (x - ball_cx) ** 2 + (y - ball_cy) ** 2
        if bd2 < ball_r ** 2:
            t_ball = 1 - math.sqrt(bd2) / ball_r
            # Irregular paper crumple look (noise bands)
            noise = 0.5 + 0.5 * math.sin((x + y) * 0.5) * math.sin(x * 0.3 + 1)
            base = lerp_color(BALL_COL, (220, 210, 160), noise * 0.4)
            c = lerp_color(base, (255, 255, 255), t_ball * 0.35)

        # ── TITLE BAR (bottom) ─────────────────────────────────
        if fy > 0.88:
            c = lerp_color(c, (15, 20, 40), 0.7)

        row.append(tuple(clamp(v, 0, 255) for v in c))
    pixels.extend(row)

# Title text (simple pixel font via thick lines)
def draw_rect(pixels, W, x, y, w, h, color):
    for dy in range(h):
        for dx in range(w):
            nx, ny = x + dx, y + dy
            if 0 <= nx < W and 0 <= ny < len(pixels) // W:
                pixels[ny * W + nx] = color

# "TRASH TOSS 3D" title — draw as thick colored blocks
title_y = int(H * 0.90)
title_color = (255, 255, 255)
accent_color = (74, 222, 128)

# Simple block letter representation (very crude but visible)
def draw_text_block(pixels, W, tx, ty, text, col, size=8):
    """Draw text as colored bar with height."""
    bar_w = len(text) * (size + 2)
    for dy in range(size):
        for dx in range(bar_w):
            nx, ny = tx + dx, ty + dy
            if 0 <= nx < W and 0 <= ny < H:
                pixels[ny * W + nx] = col

draw_rect(pixels, W, int(W*0.5) - 130, title_y, 260, 28, (255, 255, 255))
draw_rect(pixels, W, int(W*0.5) - 118, title_y + 4, 240, 20, (15, 20, 40))

# accent underline
draw_rect(pixels, W, int(W*0.5) - 80, title_y + 32, 160, 5, accent_color)

os.makedirs('game', exist_ok=True)
write_png('/home/user/Ramadan/game/thumbnail.png', W, H, pixels)
print(f"thumbnail.png: {os.path.getsize('/home/user/Ramadan/game/thumbnail.png')} bytes")

# ── FAVICON 512×512 ────────────────────────────────────────────────────────────
FW = FH = 512
fpx = []
for y in range(FH):
    for x in range(FW):
        fx, fy = x/FW, y/FH
        # Dark bg
        c = (20, 25, 50)

        # BIN body
        bc_x = FW//2
        bc_y = int(FH*0.62)
        bw = 160
        bh = 200
        if abs(x - bc_x) < bw//2 and bc_y - bh < y < bc_y:
            tb = (bc_y - y) / bh
            c = lerp_color(BIN_COL, (10, 60, 25), 1 - tb)
            if 0.3 < tb < 0.42:
                c = lerp_color(c, (254,249,195), 0.6)
        # Rim
        if abs(x - bc_x) < bw//2 + 10 and bc_y - bh - 8 < y < bc_y - bh + 6:
            c = BIN_RIM

        # Ball above bin
        ball2_cx = int(FW * 0.55)
        ball2_cy = int(FH * 0.22)
        ball2_r  = 55
        b2d2 = (x - ball2_cx)**2 + (y - ball2_cy)**2
        if b2d2 < ball2_r**2:
            t2 = 1 - math.sqrt(b2d2)/ball2_r
            noise = 0.5 + 0.5*math.sin((x+y)*0.6)
            base = lerp_color(BALL_COL, (200,190,140), noise*0.4)
            c = lerp_color(base, (255,255,255), t2*0.4)

        # mini arc
        for ti in range(0, 12):
            t2 = ti/11
            ax = FW*0.38 + (ball2_cx - FW*0.38)*t2
            ay = FH*0.45 + (ball2_cy - FH*0.45)*t2 - 120*4*t2*(1-t2)
            if abs(x-ax)<5 and abs(y-ay)<5 and ti%2==0:
                c = (200, 200, 200)

        # Green glow on ball
        glow_r = 70
        if b2d2 < glow_r**2 and b2d2 >= ball2_r**2:
            alpha = 1 - (math.sqrt(b2d2) - ball2_r) / (glow_r - ball2_r)
            c = lerp_color(c, (74,222,128), alpha * 0.25)

        fpx.append(tuple(clamp(v,0,255) for v in c))

write_png('/home/user/Ramadan/game/favicon.png', FW, FH, fpx)
print(f"favicon.png: {os.path.getsize('/home/user/Ramadan/game/favicon.png')} bytes")
print("Done!")

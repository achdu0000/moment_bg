from PIL import Image, ImageDraw
import os
import math

bg_black = (0, 0, 0)
bg_white = (255, 255, 255)
sq_black = (38, 38, 38)
sq_white = (255 - sq_black[0], 255 - sq_black[1], 255 - sq_black[2])
gua_black = (
    (bg_black[0] + sq_black[0]) // 2,
    (bg_black[1] + sq_black[1]) // 2,
    (bg_black[2] + sq_black[2]) // 2,
)
gua_white = (
    (bg_white[0] + sq_white[0]) // 2,
    (bg_white[1] + sq_white[1]) // 2,
    (bg_white[2] + sq_white[2]) // 2,
)
yin = bg_black
yang = bg_white


def create_background(width, height):
    bg = Image.new("RGBA", (width, height), bg_black)
    left_half = Image.new("RGBA", (width // 2, height), bg_white)
    bg.paste(left_half, (0, 0))
    return bg


def create_center_square(size):
    square = Image.new("RGBA", (size, size), sq_white)
    left_half = Image.new("RGBA", (size // 2, size), sq_black)
    square.paste(left_half, (0, 0))
    return square


def create_center_yinyang_shade(size, eye_size):
    return create_center_yinyang(size, eye_size, flip_L_R=1, opacity=64)


def create_center_yinyang(size, eye_size, rotation=0, flip_L_R=0, opacity=255):
    yy = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(yy)

    draw.pieslice((0, 0, size, size), start=90, end=270, fill=yang)
    draw.pieslice((0, 0, size, size), start=270, end=450, fill=yin)

    draw.pieslice(
        (size // 4, 0, size - size // 4, size // 2), start=270, end=450, fill=yang
    )
    draw.pieslice(
        (size // 4, size // 2, size - size // 4, size), start=90, end=270, fill=yin
    )

    draw.ellipse(
        (
            size // 2 - eye_size // 2,
            size // 4 - eye_size // 2,
            size // 2 + eye_size // 2,
            size // 4 + eye_size // 2,
        ),
        fill=yin,
    )
    draw.ellipse(
        (
            size // 2 - eye_size // 2,
            size - size // 4 - eye_size // 2,
            size // 2 + eye_size // 2,
            size - size // 4 + eye_size // 2,
        ),
        fill=yang,
    )
    if rotation != 0:
        rotation = rotation % 360
        yy = yy.rotate(rotation)
    if flip_L_R != 0:
        yy = yy.transpose(Image.FLIP_LEFT_RIGHT)
    if opacity != 255:
        _, _, _, a = yy.split()
        a = a.point(lambda p: p * opacity // 255)
        yy.putalpha(a)

    return yy


def create_center_gua(size, out_len, in_len):
    edge_num = 8
    degree_each = 360 / edge_num
    degree = degree_each / 2
    out_d = out_len / 2 / math.tan(math.radians(degree))
    in_d = in_len / 2 / math.tan(math.radians(degree))
    draw_width = int((out_d - in_d) / 6.5)

    cx, cy = size // 2, size // 2

    points_in, points_mid, points_out = [], [], []
    r_in = (in_d + (out_d - in_d) / 4) * math.cos(math.radians(degree))
    r_mid = (in_d + (out_d - in_d) * 7 / 12) * math.cos(math.radians(degree))
    r_out = (in_d + (out_d - in_d) * 11 / 12) * math.cos(math.radians(degree))

    for i in range(edge_num):
        angle = math.radians(i * 360 / edge_num - degree)
        points_in.append((cx + r_in * math.cos(angle), cy + r_in * math.sin(angle)))
        points_mid.append((cx + r_mid * math.cos(angle), cy + r_mid * math.sin(angle)))
        points_out.append((cx + r_out * math.cos(angle), cy + r_out * math.sin(angle)))

    gua_left = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw_left = ImageDraw.Draw(gua_left)

    draw_left.polygon(points_in, fill=None, outline=gua_white, width=draw_width)
    draw_left.polygon(points_mid, fill=None, outline=gua_white, width=draw_width)
    draw_left.polygon(points_out, fill=None, outline=gua_white, width=draw_width)

    gua_right = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw_right = ImageDraw.Draw(gua_right)

    draw_right.polygon(points_in, fill=None, outline=gua_black, width=draw_width)
    draw_right.polygon(points_mid, fill=None, outline=gua_black, width=draw_width)
    draw_right.polygon(points_out, fill=None, outline=gua_black, width=draw_width)

    mask = Image.new("L", (size, size), 0)
    draw_mask = ImageDraw.Draw(mask)
    draw_mask.rectangle([cx, 0, size, size], fill=255)
    # left: gua_white, right: gua_black
    gua = Image.composite(gua_right, gua_left, mask=mask)

    alpha = gua.getchannel("A")
    mask = Image.new("L", (size, size), 0)
    draw_mask = ImageDraw.Draw(mask)

    # make border
    ofs = 3
    for i in range(edge_num):
        draw_mask.pieslice(
            [0, 0, size, size],
            degree - ofs + i * 360 / edge_num,
            degree + ofs + i * 360 / edge_num,
            fill=255,
        )

    r_in = r_in - 5
    r_mid = r_mid - 5

    # make 8 gua

    # East ☳ 震
    draw_mask.pieslice(
        [0, 0, size, size],
        degree_each * 4 - ofs,
        degree_each * 4 + ofs,
        fill=255,
        outline=None,
    )
    draw_mask.pieslice(
        [cx - r_in, cy - r_in, cx + r_in, cy + r_in],
        degree_each * 4 - ofs * 1.5,
        degree_each * 4 + ofs * 1.5,
        fill=0,
        outline=None,
    )

    # Eash-South ☴ 巽
    draw_mask.pieslice(
        [cx - r_in, cy - r_in, cx + r_in, cy + r_in],
        degree_each * 5 - ofs,
        degree_each * 5 + ofs,
        fill=255,
        outline=None,
    )

    # South ☲ 离
    draw_mask.pieslice(
        [cx - r_mid, cy - r_mid, cx + r_mid, cy + r_mid],
        degree_each * 6 - ofs,
        degree_each * 6 + ofs,
        fill=255,
        outline=None,
    )
    draw_mask.pieslice(
        [cx - r_in, cy - r_in, cx + r_in, cy + r_in],
        degree_each * 6 - ofs * 1.5,
        degree_each * 6 + ofs * 1.5,
        fill=0,
        outline=None,
    )

    # South-West ☷ 坤
    draw_mask.pieslice(
        [0, 0, size, size],
        degree_each * 7 - ofs,
        degree_each * 7 + ofs,
        fill=255,
        outline=None,
    )

    # West ☱ 兑
    draw_mask.pieslice(
        [0, 0, size, size],
        degree_each * 0 - ofs,
        degree_each * 0 + ofs,
        fill=255,
        outline=None,
    )
    draw_mask.pieslice(
        [cx - r_mid, cy - r_mid, cx + r_mid, cy + r_mid],
        degree_each * 0 - ofs * 1.5,
        degree_each * 0 + ofs * 1.5,
        fill=0,
        outline=None,
    )

    # North-West ☰ 乾
    # nothing to do :)
    # degree_each * 1

    # North ☵ 坎
    draw_mask.pieslice(
        [0, 0, size, size],
        degree_each * 2 - ofs,
        degree_each * 2 + ofs,
        fill=255,
        outline=None,
    )
    draw_mask.pieslice(
        [cx - r_mid, cy - r_mid, cx + r_mid, cy + r_mid],
        degree_each * 2 - ofs * 1.5,
        degree_each * 2 + ofs * 1.5,
        fill=0,
        outline=None,
    )
    draw_mask.pieslice(
        [cx - r_in, cy - r_in, cx + r_in, cy + r_in],
        degree_each * 2 - ofs,
        degree_each * 2 + ofs,
        fill=255,
        outline=None,
    )

    # North-East ☶ 艮
    draw_mask.pieslice(
        [cx - r_mid, cy - r_mid, cx + r_mid, cy + r_mid],
        degree_each * 3 - ofs,
        degree_each * 3 + ofs,
        fill=255,
        outline=None,
    )

    alpha.paste(0, mask=mask)
    gua.putalpha(alpha)

    return gua


def paste_centered(canvas, *overlays):
    for overlay in overlays:
        canvas_width, canvas_height = canvas.size
        overlay_width, overlay_height = overlay.size
        x = (canvas_width - overlay_width) // 2
        y = (canvas_height - overlay_height) // 2
        canvas.paste(overlay, (x, y), mask=overlay.split()[3])


def main(output_filename):
    scale = 10
    canvas_width, canvas_height = 1920 * scale, 1080 * scale
    sq_size = 500 * scale
    yy_shade_size = int(500 * 1.41421356 * scale)
    yy_size = 200 * scale
    gua_maxsize = sq_size
    gua_out_len = 210 * scale
    gua_in_len = 120 * scale

    bg = create_background(canvas_width, canvas_height)
    sq = create_center_square(sq_size)
    yy_shade = create_center_yinyang_shade(yy_shade_size, yy_shade_size // 8)
    yy = create_center_yinyang(yy_size, yy_size // 8)
    gua = create_center_gua(gua_maxsize, gua_out_len, gua_in_len)

    paste_centered(bg, sq, yy_shade, yy, gua)

    de_scale = 10
    bg = bg.resize(
        (canvas_width // de_scale, canvas_height // de_scale), Image.Resampling.LANCZOS
    )
    bg.save(f"{canvas_width // de_scale}x{canvas_height // de_scale}{output_filename}")

if __name__ == "__main__":
    main("bg.png")

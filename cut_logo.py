import numpy as np
from PIL import Image

def extract_circle(input_path, output_path, radius):
    img = Image.open(input_path).convert('RGBA')
    img_arr = np.array(img)               # (H, W, R, G, B, A)
    height, width = img_arr.shape[:2]

    cx = (width - 1) / 2.0
    cy = (height - 1) / 2.0

    out_size = int(2 * radius)

    out_arr = np.zeros((out_size, out_size, 4), dtype=np.uint8)

    y_out, x_out = np.indices((out_size, out_size))
    dx = x_out - radius
    dy = y_out - radius
    mask_circle = (dx**2 + dy**2) <= radius**2

    x_orig = np.round(cx + dx).astype(int)
    y_orig = np.round(cy + dy).astype(int)


    mask_inbounds = (x_orig >= 0) & (x_orig < width) & (y_orig >= 0) & (y_orig < height)

    valid = mask_circle & mask_inbounds

    out_arr[y_out[valid], x_out[valid]] = img_arr[y_orig[valid], x_orig[valid]]

    out_img = Image.fromarray(out_arr, 'RGBA')
    out_img.save(output_path, 'PNG')


# 使用示例
if __name__ == '__main__':
    extract_circle('1920X1080bg.png', 'logo500x500.png', 250)
    extract_circle('1920X1080bg.png', 'logo707x707.png', 250*1.41421356)
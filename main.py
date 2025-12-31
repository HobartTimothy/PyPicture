import os
import cv2
import numpy as np
from tosvg import to_svg

if __name__ == "__main__":
    # 请替换为你的图片路径
    input_img = "E:\\redis.jpg"
    output_svg = "E:\\output_color.svg"

    if not os.path.exists(input_img):
        dummy_img = np.zeros((100, 100, 3), dtype=np.uint8)
        cv2.circle(dummy_img, (50, 50), 40, (0, 0, 255), -1)
        cv2.imwrite(input_img, dummy_img)

    to_svg.image_to_svg_color(input_img, output_svg)
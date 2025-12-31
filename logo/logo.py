import os
import locale
import platform
from PIL import Image, ImageDraw, ImageFont, ImageColor


def _draw_centered(draw, text, font, fill, width, height):

    draw.text((width / 2, height / 2), text, font=font, fill=fill, anchor="mm", align="center")

def _draw_corner(draw, text, font, fill, width, height):

    padding = width // 30
    bbox = draw.multiline_textbbox((0, 0), text, font=font)
    text_w, text_h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x = width - text_w - padding
    y = height - text_h - padding
    draw.text((x, y), text, font=font, fill=fill, align="right")

def _draw_tiled(layer, text, font, fill, angle, width, height):

    # 创建单个文字块
    draw_temp = ImageDraw.Draw(layer)
    bbox = draw_temp.multiline_textbbox((0, 0), text, font=font)
    # 增加间距 (gap)，避免文字太拥挤
    text_w = bbox[2] - bbox[0] + int(width * 0.1)
    text_h = bbox[3] - bbox[1] + int(height * 0.1)

    txt_img = Image.new('RGBA', (text_w, text_h), (255, 255, 255, 0))
    d = ImageDraw.Draw(txt_img)
    d.text((text_w / 2, text_h / 2), text, font=font, fill=fill, anchor="mm", align="center")

    rotated_txt = txt_img.rotate(angle, expand=1, resample=Image.Resampling.BICUBIC)
    r_w, r_h = rotated_txt.size

    # 铺满
    for y in range(-r_h, height + r_h, r_h):
        for x in range(-r_w, width + r_w, r_w):
            layer.paste(rotated_txt, (x, y), rotated_txt)


def _get_best_font():
    """
    自动检测系统语言并加载对应字体
    """

    # 获取系统语言，例如 'zh_CN', 'en_US' -> 提取前两位 'zh', 'en'
    system = platform.system()

    try:
        lang_code, _ = locale.getdefaultlocale()
        lang = lang_code.split('_')[0].lower() if lang_code else 'en'
    except:
        lang = 'en'

    print(f"🌍 检测到系统语言: {lang}, 操作系统: {system}")

    # 字体映射表 {OS: {lang: [优先级列表]}}
    font_map = {
        "Windows": {
            "zh": ["C:/Windows/Fonts/msyh.ttc", "C:/Windows/Fonts/simsun.ttc"],  # 雅黑, 宋体
            "ja": ["C:/Windows/Fonts/msgothic.ttc", "C:/Windows/Fonts/meiryo.ttc"],  # 明朝,由
            "ko": ["C:/Windows/Fonts/malgun.ttf"],  # Malgun Gothic
            "default": ["C:/Windows/Fonts/arial.ttf", "C:/Windows/Fonts/tahoma.ttf"]
        },
        "Darwin": {  # MacOS
            "zh": ["/System/Library/Fonts/PingFang.ttc", "/System/Library/Fonts/STHeiti Light.ttc"],
            "ja": ["/System/Library/Fonts/Hiragino Sans GB.ttc"],
            "default": ["/Library/Fonts/Arial.ttf", "/System/Library/Fonts/Helvetica.ttc"]
        },
        "Linux": {
            "zh": ["/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",  "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf"],
            "default": ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]
        }
    }

    # 获取当前系统的字体列表
    os_fonts = font_map.get(system, {})

    # 获取当前语言的候选列表，如果没有则取 default
    candidates = os_fonts.get(lang, os_fonts.get("default", []))

    # 如果语言特定字体没找到，尝试回退到 default
    if lang != "default":
        candidates += os_fonts.get("default", [])

    # 遍历检查文件是否存在
    for p in candidates:
        if os.path.exists(p):
            return p

    print("⚠️ 警告：未找到匹配字体，使用 PIL 默认字体（可能不支持中文）")
    return None


class Watermark:
    """
    水印类，用于给图片添加水印。
    """

    def __init__(self, font_path=None):
        """
        初始化：自动检测系统语言并加载对应字体
        """

        self.font_path = font_path or _get_best_font()
        print(f"🔤 已加载字体: {self.font_path}")

    def add(self, image_path, output_path, text, style='tile', color='#FFFFFF', opacity=100, angle=30):
        """
        给图片添加水印
        :param image_path: 图片路径
        :param output_path: 输出路径
        :param text: 水印文字
        :param style: 水印样式，可选 'tile' (平铺), 'center' (居中), 'bottom_right' (右下角)
        :param color: 水印颜色，默认为白色
        :param opacity: 水印透明度，0-~，默认为 100
        :param angle: 水印旋转角度，默认为 30
        """

        try:
            img = Image.open(image_path).convert("RGBA")
            width, height = img.size

            # 1. 解析颜色并结合透明度
            # ImageColor.getrgb 会把 hex/name 转为 (r, g, b)
            rgb = ImageColor.getrgb(color)
            # 组合成 (r, g, b, a)
            fill_color = rgb + (opacity,)

            watermark_layer = Image.new("RGBA", img.size, (255, 255, 255, 0))
            draw = ImageDraw.Draw(watermark_layer)

            # 2. 动态计算字体大小
            scale_factor = 25 if style == 'tile' else 10
            font_size = max(20, width // scale_factor)

            try:
                font = ImageFont.truetype(self.font_path, font_size)
            except:
                font = ImageFont.load_default()

            # 3. 绘制
            if style == 'tile':
                _draw_tiled(watermark_layer, text, font, fill_color, angle, width, height)
            elif style == 'center':
                _draw_centered(draw, text, font, fill_color, width, height)
            else:  # bottom_right
                _draw_corner(draw, text, font, fill_color, width, height)

            # 4. 保存
            combined = Image.alpha_composite(img, watermark_layer)
            combined = combined.convert("RGB")
            combined.save(output_path, quality=95)
            print(f"✅ 完成: {output_path} | 颜色: {color}")

        except Exception as e:
            print(f"❌ 错误: {e}")


# ================= 测试区域 =================
#
# if __name__ == "__main__":
#     # 无需传参，自动根据你的电脑语言选字体
#     wm = Watermark()
#
#     # 1. 红色警告水印 (Hex颜色)
#     wm.add("input.jpg", "out_red.jpg", "机密\nTOP SECRET",  style='tile', color='#FF0000', opacity=60)
#
#     # 2. 黑色版权水印 (英文颜色名)
#     wm.add("input.jpg", "out_black.jpg", "© 2025 My Studio", style='bottom_right', color='black', opacity=180)
#
#     # 3. 蓝色居中水印
#     wm.add("input.jpg", "out_blue.jpg", "SAMPLE", style='center', color='#0000FF', opacity=80)
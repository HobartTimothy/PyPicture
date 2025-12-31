from PIL import Image
from pathlib import Path

def expand_to_square(img, background_color=(0, 0, 0, 0)):
    """
    将图片填充为正方形，背景透明，保持原图比例不拉伸。
    """

    width, height = img.size
    if width == height:
        return img

    # 计算新的正方形边长（取长宽中的最大值）
    new_size = max(width, height)

    # 创建一个新的透明背景图
    new_img = Image.new('RGBA', (new_size, new_size), background_color)

    # 计算粘贴位置，使原图居中
    paste_x = (new_size - width) // 2
    paste_y = (new_size - height) // 2

    new_img.paste(img, (paste_x, paste_y))
    return new_img


def process_logo(input_path_str, output_dir_str="output_icons"):
    """
    读取图片，保持比例缩放并导出多种尺寸。
    """

    input_path = Path(input_path_str)
    output_dir = Path(output_dir_str)

    # 1. 检查文件是否存在
    if not input_path.exists():
        print(f"❌ 错误: 找不到文件 {input_path}")
        return

    # 2. 创建输出目录（如果不存在）
    output_dir.mkdir(parents=True, exist_ok=True)

    # 定义目标尺寸
    target_sizes = [16, 32, 48, 64, 80, 128, 216, 512, 1024]

    try:
        with Image.open(input_path) as img:
            print(f"📂 正在处理: {input_path.name}")

            # 3. 统一转换为 RGBA (处理透明度)
            img = img.convert("RGBA")

            # 4. 先将原图处理成正方形（加透明填充），防止后续缩放变形
            square_img = expand_to_square(img)

            for size in target_sizes:
                # 5. 高质量缩放
                # 注意：LANCZOS 是 ANTIALIAS 的现代替代品
                resized_img = square_img.resize((size, size), Image.Resampling.LANCZOS)

                # 构建输出文件名
                output_filename = f"{input_path.stem}-{size}.png"
                save_path = output_dir / output_filename

                resized_img.save(save_path)
                print(f"   ✅ 已生成: {save_path}")

            print(f"🎉 全部完成！图片保存在 '{output_dir}' 文件夹中。")
    except Exception as e:
        print(f"❌ 处理出错: {e}")
import os
from vtracer import convert_image_to_svg_py


def image_to_svg_color(input_path, output_path):
    # 1. 获取绝对路径 (解决路径找不到的问题的关键)
    abs_input = os.path.abspath(input_path)
    abs_output = os.path.abspath(output_path)

    # 2. 打印路径进行调试
    print(f"输入文件绝对路径: {abs_input}")

    # 3. 在调用库之前，先用 Python 检查文件是否存在
    if not os.path.exists(abs_input):
        print(f"❌ 错误: Python 找不到文件: {abs_input}")
        print("请检查文件名是否正确，或者文件是否在正确的文件夹内。")
        return

    print(f"正在转换 -> {abs_output} ...")

    try:
        convert_image_to_svg_py(
            abs_input,  # 传入绝对路径
            abs_output,  # 传入绝对路径
            colormode='color',
            hierarchical='stacked',
            mode='spline',
            filter_speckle=4,
            color_precision=6,
            layer_difference=16,
            corner_threshold=60,
            length_threshold=10,
            max_iterations=10,
            splice_threshold=45,
            path_precision=8
        )
        print("✅ 转换成功！")

    except Exception as e:
        print(f"❌ 转换过程中发生错误: {e}")

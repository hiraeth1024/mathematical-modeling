import pandas as pd
import matplotlib.pyplot as plt
import os

import matplotlib.pyplot as plt

import matplotlib.font_manager as fm

# 自动查找可用中文字体

font_candidates = [

    "SimHei",

    "Microsoft YaHei",

    "PingFang SC",

    "Noto Sans CJK SC",

    "Noto Sans CJK JP",

    "WenQuanYi Zen Hei",

    "Arial Unicode MS"

]

available_fonts = {f.name for f in fm.fontManager.ttflist}

selected_font = None

for font in font_candidates:

    if font in available_fonts:

        selected_font = font

        break

if selected_font:

    plt.rcParams["font.sans-serif"] = [selected_font]

    plt.rcParams["axes.unicode_minus"] = False

    print(f"使用字体：{selected_font}")

else:

    plt.rcParams["font.sans-serif"] = ["DejaVu Sans"]

    plt.rcParams["axes.unicode_minus"] = False

    print("未找到中文字体，建议将图标题改为英文，或安装 Noto Sans CJK 字体")

# ======================
# 1. 读取数据
# ======================
file_path = "/Users/hybuzhy/Documents/Mathematical modeling/附件1.布伦特原油期货主力合约价格数据.csv"
df = pd.read_csv(file_path)

# 创建输出目录
output_dir = "results/paper_figures"
os.makedirs(output_dir, exist_ok=True)

# 设置中文字体
plt.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei", "PingFang SC"]
plt.rcParams["axes.unicode_minus"] = False


# ======================
# 2. 缺失值统计图
# ======================
missing_count = df.isnull().sum()

plt.figure(figsize=(9, 5))
plt.bar(missing_count.index, missing_count.values)

plt.title("布伦特原油价格数据缺失值统计图", fontsize=14)
plt.xlabel("字段名称", fontsize=12)
plt.ylabel("缺失值数量", fontsize=12)
plt.xticks(rotation=45, ha="right")
plt.tight_layout()

plt.savefig(
    f"{output_dir}/fig3_1_missing_values.png",
    dpi=300,
    bbox_inches="tight"
)
plt.close()

dsadad
# ======================
# 3. 自动识别收盘价字段
# ======================
possible_close_cols = ["收盘价", "收盘", "close", "Close", "CLOSE", "close_price"]

close_col = None
for col in possible_close_cols:
    if col in df.columns:
        close_col = col
        break

if close_col is None:
    raise ValueError(f"未找到收盘价字段，请检查字段名。当前字段为：{list(df.columns)}")

# 转换为数值型
df[close_col] = pd.to_numeric(df[close_col], errors="coerce")


# ======================
# 4. 收盘价箱线图
# ======================
plt.figure(figsize=(6, 5))
plt.boxplot(
    df[close_col].dropna(),
    vert=True,
    patch_artist=True,
    labels=["收盘价"]
)

plt.title("布伦特原油收盘价箱线图", fontsize=14)
plt.ylabel("价格（美元/桶）", fontsize=12)
plt.tight_layout()

plt.savefig(
    f"{output_dir}/fig3_2_close_price_boxplot.png",
    dpi=300,
    bbox_inches="tight"
)
plt.close()


print("图像已生成：")
print(f"{output_dir}/fig3_1_missing_values.png")
print(f"{output_dir}/fig3_2_close_price_boxplot.png")
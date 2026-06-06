from graphviz import Digraph

dot = Digraph(
    name="problem2_simple_flowchart",
    format="png",
    encoding="utf-8"
)

# 图形整体设置
dot.attr(
    rankdir="TB",
    bgcolor="white",
    splines="ortho",
    nodesep="0.5",
    ranksep="0.6",
    dpi="300"          # 输出 300 DPI
)

# 节点样式
dot.attr(
    "node",
    shape="rect",
    style="rounded,filled",
    fontname="Microsoft YaHei",
    fontsize="12",
    color="#4A6FA5",
    fillcolor="#EAF2FB",
    penwidth="1.4"
)

# 边样式
dot.attr(
    "edge",
    fontname="Microsoft YaHei",
    fontsize="11",
    color="#555555",
    arrowsize="0.8"
)

# 节点
dot.node("A", "确定研究对象\n90—180天中长期封锁情景", fillcolor="#D6EAF8")
dot.node("B", "提取关键影响因素\n供给缺口、库存、增产、需求弹性")
dot.node("C", "构建中长期供需调节模型")
dot.node("D", "设定供需均衡条件\n有效供给 = 有效需求")
dot.node("E", "求解油价平衡点\n或平衡区间")
dot.node("F", "判断库存阈值\n识别价格跳变风险", shape="diamond", fillcolor="#FCF3CF")
dot.node("G", "输出油价预测结果\n并分析影响因素", fillcolor="#D5F5E3")

# 连线
dot.edge("A", "B")
dot.edge("B", "C")
dot.edge("C", "D")
dot.edge("D", "E")
dot.edge("E", "F")
dot.edge("F", "G")

# 输出 300DPI PNG
dot.render("问题二_简化思路流程图_300dpi", cleanup=True)

print("已生成：问题二_简化思路流程图_300dpi.png")
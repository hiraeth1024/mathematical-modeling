% Problem 2 paper figures.
% This script draws the figures needed by Section 5 of the paper:
%   Fig. 5-1 price paths under three scenarios
%   Fig. 5-2 supply adjustment decomposition under the baseline scenario
%   Fig. 5-3 inventory depletion and risk premium under the pessimistic scenario
%   Fig. 5-4 long-run demand elasticity and equilibrium points
%   Fig. 5-5 equilibrium price, risk premium, and jump-risk judgment for Section 5.3
%   Fig. 5-6 factor impacts on the day-180 equilibrium price for Section 5.4
%   Fig. 5-7 medium-term oil price equilibrium interval for Section 5.4
%
% Run from any working directory:
%   run("/Users/hybuzhy/Documents/Mathematical modeling/代码/问题二/code/problem2_paper_figures.m")

clear; clc;

scriptDir = fileparts(mfilename("fullpath"));
problemDir = fileparts(scriptDir);
resultsDir = fullfile(problemDir, "results");
figDir = fullfile(resultsDir, "paper_figures_matlab");

if ~exist(figDir, "dir")
    mkdir(figDir);
end

set(groot, "defaultAxesFontName", "Helvetica");
set(groot, "defaultTextFontName", "Helvetica");
set(groot, "defaultAxesFontSize", 12);

scenarioFiles = [
    "problem2_optimistic_path.csv"
    "problem2_baseline_path.csv"
    "problem2_pessimistic_path.csv"
];
scenarioLabels = ["乐观情景", "基准情景", "悲观情景"];
scenarioColors = [
    0.1725, 0.6275, 0.1725
    0.1216, 0.4667, 0.7059
    0.8392, 0.1529, 0.1569
];

optimistic = readtable(fullfile(resultsDir, scenarioFiles(1)));
baseline = readtable(fullfile(resultsDir, scenarioFiles(2)));
pessimistic = readtable(fullfile(resultsDir, scenarioFiles(3)));

%% 图5-1 三种情景下90-180天油价预测路径
figure("Position", [100, 100, 960, 560], "Color", "w");
hold on;
tables = {optimistic, baseline, pessimistic};
for i = 1:numel(tables)
    T = tables{i};
    plot(T.day, T.price, "LineWidth", 2.0, "Color", scenarioColors(i, :));
end
hold off;
grid on;
box on;
xlabel("封锁后天数");
ylabel("油价（美元/桶）");
title("图5-1 三种情景下90-180天油价预测路径");
legend(scenarioLabels, "Location", "northwest");
xlim([90, 180]);
ylim([70, 180]);
exportgraphics(gcf, fullfile(figDir, "fig5_1_price_paths.png"), "Resolution", 300);
exportgraphics(gcf, fullfile(figDir, "fig5_1_price_paths.pdf"), "ContentType", "vector");

%% 图5-2 基准情景下中长期供给调节分解
figure("Position", [100, 100, 960, 560], "Color", "w");
Y = [baseline.bypass, baseline.extra_output, baseline.strategic_release, baseline.commercial_draw];
area(baseline.day, Y, "LineStyle", "none");
grid on;
box on;
xlabel("封锁后天数");
ylabel("调节量（百万桶/日）");
title("图5-2 基准情景下中长期供给调节分解");
legend(["绕道运输", "其他产油国增产", "战略储备释放", "商业库存释放"], "Location", "northwest");
xlim([90, 180]);
exportgraphics(gcf, fullfile(figDir, "fig5_2_supply_adjustment.png"), "Resolution", 300);
exportgraphics(gcf, fullfile(figDir, "fig5_2_supply_adjustment.pdf"), "ContentType", "vector");

%% 图5-3 悲观情景下库存消耗与风险溢价
figure("Position", [100, 100, 960, 560], "Color", "w");
yyaxis left;
plot(pessimistic.day, pessimistic.commercial_stock, "LineWidth", 2.0, "Color", [0.1216, 0.4667, 0.7059]);
ylabel("商业库存（百万桶）");
ylim([0, max(pessimistic.commercial_stock) * 1.1]);

yyaxis right;
plot(pessimistic.day, pessimistic.risk_premium, "LineWidth", 2.0, "Color", [0.8392, 0.1529, 0.1569]);
ylabel("风险溢价（美元/桶）");
ylim([0, max(pessimistic.risk_premium) * 1.25]);

grid on;
box on;
xlabel("封锁后天数");
title("图5-3 悲观情景下库存消耗与风险溢价");
xlim([90, 180]);
legend(["商业库存", "风险溢价"], "Location", "northeast");
exportgraphics(gcf, fullfile(figDir, "fig5_3_stock_risk.png"), "Resolution", 300);
exportgraphics(gcf, fullfile(figDir, "fig5_3_stock_risk.pdf"), "ContentType", "vector");

%% 图5-4 长期需求弹性下的供需平衡点
P0 = 75;
D0 = 100;
epsilon = -0.18;
Q = 86:0.25:100;
P = P0 .* (Q ./ D0) .^ (1 ./ epsilon);

figure("Position", [100, 100, 960, 560], "Color", "w");
plot(Q, P, "k", "LineWidth", 2.0);
hold on;

eqSupply = [
    optimistic.effective_supply(end)
    baseline.effective_supply(end)
    pessimistic.effective_supply(end)
];
eqPrice = [
    optimistic.equilibrium_price(end)
    baseline.equilibrium_price(end)
    pessimistic.equilibrium_price(end)
];

for i = 1:3
    xline(eqSupply(i), "--", "Color", scenarioColors(i, :), "LineWidth", 1.4);
    scatter(eqSupply(i), eqPrice(i), 64, scenarioColors(i, :), "filled");
    text(eqSupply(i) + 0.15, eqPrice(i) + 3, ...
        sprintf("%s %.1f", scenarioLabels(i), eqPrice(i)), ...
        "Color", scenarioColors(i, :), "FontSize", 11);
end

hold off;
grid on;
box on;
xlabel("有效供给/需求（百万桶/日）");
ylabel("油价（美元/桶）");
title("图5-4 长期需求弹性下的供需平衡点");
legend(["长期需求曲线", "乐观情景", "基准情景", "悲观情景"], "Location", "northeast");
xlim([86, 100]);
ylim([70, 190]);
exportgraphics(gcf, fullfile(figDir, "fig5_4_elasticity_equilibrium.png"), "Resolution", 300);
exportgraphics(gcf, fullfile(figDir, "fig5_4_elasticity_equilibrium.pdf"), "ContentType", "vector");

%% 图5-5 5.3节油价平衡点与跳变风险组合图
summaryScenario = scenarioLabels;
equilibriumPrice = [
    optimistic.equilibrium_price(end)
    baseline.equilibrium_price(end)
    pessimistic.equilibrium_price(end)
];
riskPremium = [
    optimistic.risk_premium(end)
    baseline.risk_premium(end)
    pessimistic.risk_premium(end)
];
predictedPrice = [
    optimistic.price(end)
    baseline.price(end)
    pessimistic.price(end)
];

figure("Position", [100, 100, 1240, 560], "Color", "w");


% 左图：第180天价格分解，突出悲观情景风险溢价导致实际价格跳升
subplot("Position", [0.07, 0.14, 0.40, 0.72]);
barData = [equilibriumPrice, riskPremium, predictedPrice];
b = bar(barData, "grouped");
b(1).FaceColor = [0.1216, 0.4667, 0.7059];
b(2).FaceColor = [0.8392, 0.1529, 0.1569];
b(3).FaceColor = [0.2500, 0.2500, 0.2500];
grid on;
box on;
set(gca, "XTickLabel", summaryScenario);
ylabel("价格（美元/桶）");
title("（a）第180天平衡价、风险溢价与预测价");
legend(["供需均衡价", "库存风险溢价", "实际预测价"], "Location", "northwest");
ylim([0, max(predictedPrice) * 1.18]);

for i = 1:numel(predictedPrice)
    text(i + 0.23, predictedPrice(i) + 4, sprintf("%.1f", predictedPrice(i)), ...
        "HorizontalAlignment", "center", "FontSize", 10, "Color", [0.25, 0.25, 0.25]);
end

% 右图：悲观情景库存阈值与风险溢价，同图判断跳变风险出现时间
subplot("Position", [0.57, 0.14, 0.38, 0.72]);
yyaxis left;
plot(pessimistic.day, pessimistic.commercial_stock, "LineWidth", 2.0, "Color", [0.1216, 0.4667, 0.7059]);
hold on;
yline(90, "--", "库存阈值 I_{min}=90", "LineWidth", 1.5, "Color", [0.35, 0.35, 0.35], ...
    "LabelHorizontalAlignment", "left");
ylabel("商业库存（百万桶）");
ylim([0, max(pessimistic.commercial_stock) * 1.1]);

crossIdx = find(pessimistic.commercial_stock < 90, 1, "first");
if ~isempty(crossIdx)
    crossDay = pessimistic.day(crossIdx);
    xline(crossDay, ":", sprintf("第%.0f天跌破阈值", crossDay), ...
        "LineWidth", 1.5, "Color", [0.2, 0.2, 0.2], "LabelOrientation", "horizontal");
end

yyaxis right;
plot(pessimistic.day, pessimistic.risk_premium, "LineWidth", 2.0, "Color", [0.8392, 0.1529, 0.1569]);
ylabel("风险溢价（美元/桶）");
ylim([0, max(pessimistic.risk_premium) * 1.25]);
hold off;
grid on;
box on;
xlabel("封锁后天数");
title("（b）库存阈值触发后的价格跳变风险");
xlim([90, 180]);

exportgraphics(gcf, fullfile(figDir, "fig5_5_equilibrium_jump_risk.png"), "Resolution", 300);
exportgraphics(gcf, fullfile(figDir, "fig5_5_equilibrium_jump_risk.pdf"), "ContentType", "vector");

%% 图5-6 不同调节因素对第180天油价的影响
baseEffSupply = baseline.effective_supply(end);
baseEqPrice = baseline.equilibrium_price(end);
factorNames = ["绕道运输", "其他产油国增产", "战略储备释放", "商业库存释放"];
factorQty = [
    baseline.bypass(end)
    baseline.extra_output(end)
    baseline.strategic_release(end)
    baseline.commercial_draw(end)
];
priceWithoutFactor = P0 .* ((baseEffSupply - factorQty) ./ D0) .^ (1 ./ epsilon);
priceImpact = priceWithoutFactor - baseEqPrice;

figure("Position", [100, 100, 960, 560], "Color", "w");
barh(1:numel(factorNames), priceImpact, 0.62, "FaceColor", [0.1216, 0.4667, 0.7059]);
grid on;
box on;
set(gca, "YTick", 1:numel(factorNames), "YTickLabel", factorNames);
xlabel("若该因素缺失导致的平衡价上升幅度（美元/桶）");
ylabel("调节因素");
title("图5-6 不同调节因素对第180天油价的影响");
xlim([0, max(priceImpact) * 1.25]);
for i = 1:numel(priceImpact)
    text(priceImpact(i) + 0.8, i, sprintf("+%.1f", priceImpact(i)), ...
        "VerticalAlignment", "middle", "FontSize", 11);
end
exportgraphics(gcf, fullfile(figDir, "fig5_6_factor_price_impact.png"), "Resolution", 300);
exportgraphics(gcf, fullfile(figDir, "fig5_6_factor_price_impact.pdf"), "ContentType", "vector");

%% 图5-7 三情景油价平衡区间分析
day180Predicted = [
    optimistic.price(end)
    baseline.price(end)
    pessimistic.price(end)
];
day180Equilibrium = [
    optimistic.equilibrium_price(end)
    baseline.equilibrium_price(end)
    pessimistic.equilibrium_price(end)
];

figure("Position", [100, 100, 960, 560], "Color", "w");
hold on;
bar(1:3, day180Predicted, 0.52, "FaceColor", [0.70, 0.70, 0.70], "EdgeColor", [0.25, 0.25, 0.25]);
plot(1:3, day180Equilibrium, "o-", "LineWidth", 2.0, "MarkerSize", 7, "Color", [0.1216, 0.4667, 0.7059]);
yline(105.62, "--", "基准平衡点约105-106美元/桶", ...
    "LineWidth", 1.4, "Color", [0.1216, 0.4667, 0.7059], "LabelHorizontalAlignment", "left");
hold off;
grid on;
box on;
set(gca, "XTick", 1:3, "XTickLabel", scenarioLabels);
ylabel("油价（美元/桶）");
title("图5-7 三情景下中长期油价平衡区间");
legend(["第180天预测价", "供需均衡价"], "Location", "northwest");
ylim([70, max(day180Predicted) * 1.18]);
for i = 1:3
    text(i, day180Predicted(i) + 5, sprintf("%.1f", day180Predicted(i)), ...
        "HorizontalAlignment", "center", "FontSize", 11);
end
exportgraphics(gcf, fullfile(figDir, "fig5_7_equilibrium_interval.png"), "Resolution", 300);
exportgraphics(gcf, fullfile(figDir, "fig5_7_equilibrium_interval.pdf"), "ContentType", "vector");

fprintf("MATLAB figures written to:\n%s\n", figDir);

% Chapter 3 data-quality figures for Brent crude oil price data.
% Generated figures:
%   图3-1 布伦特原油价格数据缺失值统计图
%   图3-2 布伦特原油收盘价箱线图
%   图3-3 布伦特原油交易日期间隔统计图
%   图3-4 标准化后主要价格指标对比图
%   图3-5 布伦特原油收盘价走势分析图
%
% Run:
%   run("/Users/hybuzhy/Documents/Mathematical modeling/代码/问题二/code/chapter3_data_quality_figures.m")

clear; clc;

scriptDir = fileparts(mfilename("fullpath"));
problemDir = fileparts(scriptDir);
rootDir = fileparts(fileparts(problemDir));
csvPath = fullfile(rootDir, "附件1.布伦特原油期货主力合约价格数据.csv");
outDir = fullfile(problemDir, "results", "chapter3_figures_matlab");

if ~exist(outDir, "dir")
    mkdir(outDir);
end

opts = detectImportOptions(csvPath, "Encoding", "UTF-8");
opts = setvaropts(opts, opts.VariableNames, "TreatAsMissing", ["NA", ""]);
T = readtable(csvPath, opts);

% Use Chinese labels for paper figures.
fieldNames = ["交易日期", "合约代码", "前收盘价", "开盘价", "最高价", "最低价", "收盘价"];
rawNames = ["time", "thscode", "preClose", "open", "high", "low", "close"];

if isdatetime(T.time)
    tradeDate = T.time;
else
    tradeDate = datetime(string(T.time), "InputFormat", "yyyy/M/d");
end
[tradeDate, sortIdx] = sort(tradeDate);
T = T(sortIdx, :);

%% 图3-1 布伦特原油价格数据缺失值统计图
missingCounts = zeros(1, numel(rawNames));
for i = 1:numel(rawNames)
    missingCounts(i) = sum(ismissing(T.(rawNames(i))));
end

figure("Position", [100, 100, 980, 560], "Color", "w");
b = bar(missingCounts, 0.58);
b.FaceColor = [0.1216, 0.4667, 0.7059];
grid on;
box on;
set(gca, "XTick", 1:numel(fieldNames), "XTickLabel", fieldNames);
xtickangle(25);
ylabel("缺失值数量");
xlabel("字段名称");
title("图3-1 布伦特原油价格数据缺失值统计图");
ylim([0, max([1, missingCounts]) * 1.25]);

for i = 1:numel(missingCounts)
    text(i, missingCounts(i) + 0.04 * max([1, missingCounts]), ...
        sprintf("%d", missingCounts(i)), ...
        "HorizontalAlignment", "center", "FontSize", 11);
end

exportgraphics(gcf, fullfile(outDir, "fig3_1_missing_values.png"), "Resolution", 300);
exportgraphics(gcf, fullfile(outDir, "fig3_1_missing_values.pdf"), "ContentType", "vector");

%% 图3-2 布伦特原油收盘价箱线图
closePrice = T.close;
closePrice = closePrice(~ismissing(closePrice));

q1 = localPercentile(closePrice, 25);
q2 = localPercentile(closePrice, 50);
q3 = localPercentile(closePrice, 75);
iqrValue = q3 - q1;
lowerFence = q1 - 1.5 * iqrValue;
upperFence = q3 + 1.5 * iqrValue;
whiskerLow = min(closePrice(closePrice >= lowerFence));
whiskerHigh = max(closePrice(closePrice <= upperFence));
outlierMask = closePrice < lowerFence | closePrice > upperFence;
outlierValues = closePrice(outlierMask);
outlierCount = numel(outlierValues);

figure("Position", [100, 100, 760, 580], "Color", "w");
hold on;
grid on;
box on;

% Manually draw a boxplot using only base MATLAB graphics.
boxX = 1;
boxWidth = 0.34;
capWidth = 0.24;
rectangle("Position", [boxX - boxWidth / 2, q1, boxWidth, q3 - q1], ...
    "FaceColor", [0.9569, 0.6980, 0.5137], ...
    "EdgeColor", [0.2, 0.2, 0.2], ...
    "LineWidth", 1.6);
plot([boxX - boxWidth / 2, boxX + boxWidth / 2], [q2, q2], ...
    "Color", [0.75, 0.0, 0.0], "LineWidth", 2.2);
plot([boxX, boxX], [q3, whiskerHigh], "Color", [0.2, 0.2, 0.2], "LineWidth", 1.5);
plot([boxX, boxX], [q1, whiskerLow], "Color", [0.2, 0.2, 0.2], "LineWidth", 1.5);
plot([boxX - capWidth / 2, boxX + capWidth / 2], [whiskerHigh, whiskerHigh], ...
    "Color", [0.2, 0.2, 0.2], "LineWidth", 1.5);
plot([boxX - capWidth / 2, boxX + capWidth / 2], [whiskerLow, whiskerLow], ...
    "Color", [0.2, 0.2, 0.2], "LineWidth", 1.5);

if outlierCount > 0
    jitter = mod((1:outlierCount)' - 1, 9) - 4;
    jitter = jitter * 0.012;
    scatter(boxX + jitter, outlierValues, 18, ...
        "MarkerEdgeColor", [0.1216, 0.4667, 0.7059], ...
        "MarkerFaceColor", "w", ...
        "LineWidth", 1.0);
end

xlim([0.45, 1.55]);
ylim([min(closePrice) - 0.10 * (max(closePrice) - min(closePrice)), ...
    max(closePrice) + 0.10 * (max(closePrice) - min(closePrice))]);
set(gca, "XTick", 1, "XTickLabel", {'收盘价'});
ylabel("价格（美元/桶）");
title("图3-2 布伦特原油收盘价箱线图");

annotationText = sprintf("Q1=%.2f, 中位数=%.2f, Q3=%.2f, 异常点=%d个", ...
    q1, q2, q3, outlierCount);
text(1, min(closePrice) - 0.06 * (max(closePrice) - min(closePrice)), annotationText, ...
    "HorizontalAlignment", "center", "FontSize", 10);
hold off;

exportgraphics(gcf, fullfile(outDir, "fig3_2_close_boxplot.png"), "Resolution", 300);
exportgraphics(gcf, fullfile(outDir, "fig3_2_close_boxplot.pdf"), "ContentType", "vector");

%% 图3-3 布伦特原油交易日期间隔统计图
dateIntervals = days(diff(tradeDate));
intervalCounts = [
    sum(dateIntervals == 1)
    sum(dateIntervals == 2)
    sum(dateIntervals == 3)
    sum(dateIntervals >= 4)
];
intervalLabels = ["1天", "2天", "3天", "4天及以上"];

figure("Position", [100, 100, 860, 520], "Color", "w");
b = bar(intervalCounts, 0.58);
b.FaceColor = [0.4667, 0.6745, 0.1882];
grid on;
box on;
set(gca, "XTick", 1:numel(intervalLabels), "XTickLabel", intervalLabels);
xlabel("相邻交易记录日期间隔");
ylabel("出现次数");
title("图3-3 布伦特原油交易日期间隔统计图");
ylim([0, max(intervalCounts) * 1.18]);
for i = 1:numel(intervalCounts)
    text(i, intervalCounts(i) + 0.03 * max(intervalCounts), ...
        sprintf("%d", intervalCounts(i)), ...
        "HorizontalAlignment", "center", "FontSize", 11);
end
exportgraphics(gcf, fullfile(outDir, "fig3_3_date_interval_counts.png"), "Resolution", 300);
exportgraphics(gcf, fullfile(outDir, "fig3_3_date_interval_counts.pdf"), "ContentType", "vector");

%% 图3-4 标准化后主要价格指标对比图
priceNames = ["open", "high", "low", "close"];
priceLabels = ["开盘价", "最高价", "最低价", "收盘价"];
Z = zeros(height(T), numel(priceNames));
for i = 1:numel(priceNames)
    x = T.(priceNames(i));
    Z(:, i) = (x - min(x)) ./ (max(x) - min(x));
end

figure("Position", [100, 100, 980, 560], "Color", "w");
plot(tradeDate, Z, "LineWidth", 1.1);
grid on;
box on;
xlabel("交易日期");
ylabel("Min-Max标准化值");
title("图3-4 标准化后主要价格指标对比图");
legend(priceLabels, "Location", "northwest");
exportgraphics(gcf, fullfile(outDir, "fig3_4_normalized_price_indicators.png"), "Resolution", 300);
exportgraphics(gcf, fullfile(outDir, "fig3_4_normalized_price_indicators.pdf"), "ContentType", "vector");

%% 图3-5 布伦特原油收盘价走势分析图
figure("Position", [100, 100, 980, 560], "Color", "w");
plot(tradeDate, T.close, "LineWidth", 1.3, "Color", [0.1216, 0.4667, 0.7059]);
grid on;
box on;
xlabel("交易日期");
ylabel("收盘价（美元/桶）");
title("图3-5 布伦特原油收盘价走势分析图");

[minClose, minIdx] = min(T.close);
[maxClose, maxIdx] = max(T.close);
hold on;
scatter(tradeDate(minIdx), minClose, 50, [0.4667, 0.6745, 0.1882], "filled");
scatter(tradeDate(maxIdx), maxClose, 50, [0.8392, 0.1529, 0.1569], "filled");
text(tradeDate(minIdx), minClose, sprintf("  最低 %.2f", minClose), ...
    "VerticalAlignment", "top", "FontSize", 10);
text(tradeDate(maxIdx), maxClose, sprintf("  最高 %.2f", maxClose), ...
    "VerticalAlignment", "bottom", "FontSize", 10);
hold off;
exportgraphics(gcf, fullfile(outDir, "fig3_5_close_price_trend.png"), "Resolution", 300);
exportgraphics(gcf, fullfile(outDir, "fig3_5_close_price_trend.pdf"), "ContentType", "vector");

fprintf("缺失值统计：\n");
for i = 1:numel(rawNames)
    fprintf("  %s: %d\n", fieldNames(i), missingCounts(i));
end
fprintf("收盘价箱线图统计：Q1=%.2f, Median=%.2f, Q3=%.2f, Outliers=%d\n", ...
    q1, q2, q3, outlierCount);
fprintf("交易日期范围：%s 至 %s，共 %d 条记录\n", ...
    datestr(tradeDate(1), "yyyy-mm-dd"), datestr(tradeDate(end), "yyyy-mm-dd"), height(T));
fprintf("MATLAB figures written to:\n%s\n", outDir);

function value = localPercentile(x, p)
    x = sort(x(:));
    n = numel(x);
    if n == 0
        error("Cannot compute percentile of an empty vector.");
    end
    pos = 1 + (n - 1) * p / 100;
    lo = floor(pos);
    hi = ceil(pos);
    if lo == hi
        value = x(lo);
    else
        value = x(lo) * (hi - pos) + x(hi) * (pos - lo);
    end
end

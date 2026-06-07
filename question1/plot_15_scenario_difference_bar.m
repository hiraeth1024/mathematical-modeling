clear; clc; close all;

data = readtable('scenario_summary.csv', 'TextType', 'string');

baseIdx = data.scenario == "baseline";
basePeak = data.peak_price(baseIdx);
baseLate = data.late_mean(baseIdx);
baseEnd = data.end_price(baseIdx);

compareMask = data.scenario ~= "baseline";
compareData = data(compareMask, :);

labels = strings(height(compareData), 1);
labels(compareData.scenario == "no_buffer") = "No Buffer";
labels(compareData.scenario == "supply_buffer_only") = "Supply Buffer Only";
labels(compareData.scenario == "no_inventory_buffer") = "No Inventory Buffer";
labels(compareData.scenario == "no_late_demand_cut") = "No Late Demand Cut";

peakDiff = compareData.peak_price - basePeak;
lateDiff = compareData.late_mean - baseLate;
endDiff = compareData.end_price - baseEnd;

Y = [peakDiff, lateDiff, endDiff];

fig = figure;
bar(Y, 'grouped');
grid on;
box on;

ax = gca;
ax.XTick = 1:height(compareData);
ax.XTickLabel = labels;
ax.FontSize = 11;
ax.LineWidth = 1.1;
ax.GridColor = [0.82, 0.82, 0.82];
ax.GridAlpha = 0.9;
xtickangle(20);

legend({'Peak Price Difference', 'Late-May Mean Difference', 'End Price Difference'}, ...
    'Location', 'northwest');

title('Differences Relative to Baseline Scenario', 'FontSize', 15, 'FontWeight', 'bold');
xlabel('Scenario', 'FontSize', 12, 'FontWeight', 'bold');
ylabel('Difference (USD/barrel)', 'FontSize', 12, 'FontWeight', 'bold');

saveas(fig, 'plot_15_scenario_difference_bar.png');

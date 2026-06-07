clear; clc; close all;

data = readtable('scenario_paths.csv', 'TextType', 'string');
data.date = datetime(data.date, 'InputFormat', 'yyyy-MM-dd');

baseline = data(data.scenario == "baseline", :);

baseSupplyAfterDisruption = 10000 - baseline.L_t;
reservePart = baseline.R_t;
inventoryPart = baseline.C_t;
bypassPart = baseline.B_t;

fig = figure;
hold on;

stackData = [baseSupplyAfterDisruption, reservePart, inventoryPart, bypassPart];
area(baseline.date, stackData, 'LineStyle', 'none');

ax = gca;
ax.ColorOrder = [
    0.75 0.30 0.30
    0.20 0.45 0.85
    0.15 0.65 0.35
    0.90 0.60 0.15
];

hold on;
plot(baseline.date, baseline.S_t, ...
    'k-', ...
    'LineWidth', 2.0, ...
    'DisplayName', 'Effective Supply S_t');

xline(datetime(2026, 2, 28), '--k', 'Conflict Start', ...
    'LineWidth', 1.2, ...
    'LabelVerticalAlignment', 'bottom', ...
    'LabelHorizontalAlignment', 'left');

legend({'Base Supply after Disruption', 'Reserve Release R_t', 'Inventory Release C_t', 'Bypass Recovery B_t', 'Effective Supply S_t'}, ...
    'Location', 'eastoutside');

apply_plot_style(fig, ax, 'Composition of Effective Supply', 'Supply (10^4 barrels/day)');

saveas(fig, 'plot_10_supply_stack.png');

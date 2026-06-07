clear; clc; close all;

data = readtable('scenario_paths.csv', 'TextType', 'string');
data.date = datetime(data.date, 'InputFormat', 'yyyy-MM-dd');

baseline = data(data.scenario == "baseline", :);

fig = figure;
hold on;

plot(baseline.date, baseline.inventory, ...
    'LineWidth', 2.2, ...
    'Color', [0.10, 0.55, 0.35], ...
    'DisplayName', 'Remaining Commercial Inventory');

xline(datetime(2026, 2, 28), '--k', 'Conflict Start', ...
    'LineWidth', 1.2, ...
    'LabelVerticalAlignment', 'bottom', ...
    'LabelHorizontalAlignment', 'left');

legend('Location', 'northeast');
ax = gca;
apply_plot_style(fig, ax, 'Dynamic Evolution of Commercial Inventory', 'Inventory (10^4 barrels)');

saveas(fig, 'plot_08_inventory_curve.png');

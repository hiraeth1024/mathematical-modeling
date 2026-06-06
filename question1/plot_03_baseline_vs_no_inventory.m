clear; clc; close all;

data = readtable('scenario_paths.csv', 'TextType', 'string');
data.date = datetime(data.date, 'InputFormat', 'yyyy-MM-dd');

isBaseline = data.scenario == "baseline";
isNoInventory = data.scenario == "no_inventory_buffer";

baseline = data(isBaseline, :);
noInventory = data(isNoInventory, :);

fig = figure;
hold on;

plot(baseline.date, baseline.price, ...
    'LineWidth', 2.2, ...
    'Color', [0.10, 0.35, 0.80], ...
    'DisplayName', 'Baseline Scenario');

plot(noInventory.date, noInventory.price, ...
    '--', ...
    'LineWidth', 2.2, ...
    'Color', [0.10, 0.65, 0.35], ...
    'DisplayName', 'No-Inventory-Buffer Scenario');

xline(datetime(2026, 2, 28), '--k', 'Conflict Start', ...
    'LineWidth', 1.2, ...
    'LabelVerticalAlignment', 'bottom', ...
    'LabelHorizontalAlignment', 'left');

legend('Location', 'northwest');

ax = gca;
apply_plot_style(fig, ax, 'Baseline vs No-Inventory-Buffer Scenario', 'Price (USD/barrel)');

saveas(fig, 'plot_03_baseline_vs_no_inventory.png');

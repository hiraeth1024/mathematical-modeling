clear; clc; close all;

data = readtable('scenario_paths.csv', 'TextType', 'string');
data.date = datetime(data.date, 'InputFormat', 'yyyy-MM-dd');

isBaseline = data.scenario == "baseline";
isNoBuffer = data.scenario == "no_buffer";

baseline = data(isBaseline, :);
noBuffer = data(isNoBuffer, :);

fig = figure;
hold on;

plot(baseline.date, baseline.price, ...
    'LineWidth', 2.2, ...
    'Color', [0.10, 0.35, 0.80], ...
    'DisplayName', 'Baseline Scenario');

plot(noBuffer.date, noBuffer.price, ...
    '--', ...
    'LineWidth', 2.2, ...
    'Color', [0.85, 0.25, 0.10], ...
    'DisplayName', 'No-Buffer Scenario');

xline(datetime(2026, 2, 28), '--k', 'Conflict Start', ...
    'LineWidth', 1.2, ...
    'LabelVerticalAlignment', 'bottom', ...
    'LabelHorizontalAlignment', 'left');

legend('Location', 'northwest');

ax = gca;
apply_plot_style(fig, ax, 'Baseline vs No-Buffer Scenario', 'Price (USD/barrel)');

saveas(fig, 'plot_02_baseline_vs_no_buffer.png');

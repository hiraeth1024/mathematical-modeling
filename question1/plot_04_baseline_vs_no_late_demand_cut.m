clear; clc; close all;

data = readtable('scenario_paths.csv', 'TextType', 'string');
data.date = datetime(data.date, 'InputFormat', 'yyyy-MM-dd');

isBaseline = data.scenario == "baseline";
isNoLateCut = data.scenario == "no_late_demand_cut";

baseline = data(isBaseline, :);
noLateCut = data(isNoLateCut, :);

fig = figure;
hold on;

plot(baseline.date, baseline.price, ...
    'LineWidth', 2.2, ...
    'Color', [0.10, 0.35, 0.80], ...
    'DisplayName', 'Baseline Scenario');

plot(noLateCut.date, noLateCut.price, ...
    '--', ...
    'LineWidth', 2.2, ...
    'Color', [0.55, 0.20, 0.75], ...
    'DisplayName', 'No-Late-Demand-Cut Scenario');

xline(datetime(2026, 2, 28), '--k', 'Conflict Start', ...
    'LineWidth', 1.2, ...
    'LabelVerticalAlignment', 'bottom', ...
    'LabelHorizontalAlignment', 'left');

legend('Location', 'northwest');

ax = gca;
apply_plot_style(fig, ax, 'Baseline vs No-Late-Demand-Cut Scenario', 'Price (USD/barrel)');

saveas(fig, 'plot_04_baseline_vs_no_late_demand_cut.png');

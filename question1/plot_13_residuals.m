clear; clc; close all;

data = readtable('final_fine_best_simulation.csv', 'TextType', 'string');
data.date = datetime(data.date, 'InputFormat', 'yyyy-MM-dd');

simPrice = data.sim_price;
actualPrice = data.actual_close;
validActual = ~ismissing(actualPrice);

residuals = simPrice(validActual) - actualPrice(validActual);
residualDates = data.date(validActual);

fig = figure;
hold on;

bar(residualDates, residuals, 0.70, ...
    'FaceColor', [0.72, 0.75, 0.80], ...
    'EdgeColor', [0.35, 0.35, 0.35], ...
    'DisplayName', 'Residuals');

yline(0, '--', ...
    'Color', [0.25, 0.25, 0.25], ...
    'LineWidth', 1.2, ...
    'DisplayName', 'Zero Line');

xline(datetime(2026, 2, 28), '--k', 'Conflict Start', ...
    'LineWidth', 1.2, ...
    'LabelVerticalAlignment', 'bottom', ...
    'LabelHorizontalAlignment', 'left');

legend('Location', 'northwest');
ax = gca;
apply_plot_style(fig, ax, 'Model Residuals over Time', 'Residual (USD/barrel)');

saveas(fig, 'plot_13_residuals.png');

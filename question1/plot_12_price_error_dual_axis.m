clear; clc; close all;

data = readtable('final_fine_best_simulation.csv', 'TextType', 'string');
data.date = datetime(data.date, 'InputFormat', 'yyyy-MM-dd');

simPrice = data.sim_price;
actualPrice = data.actual_close;
validActual = ~ismissing(actualPrice);

errorSeries = nan(height(data), 1);
errorSeries(validActual) = simPrice(validActual) - actualPrice(validActual);

fig = figure;

yyaxis left
hold on;
plot(data.date, simPrice, ...
    'LineWidth', 2.2, ...
    'Color', [0.10, 0.35, 0.80], ...
    'DisplayName', 'Model Price');
plot(data.date(validActual), actualPrice(validActual), ...
    'o-', ...
    'LineWidth', 1.6, ...
    'MarkerSize', 5.0, ...
    'Color', [0.85, 0.25, 0.10], ...
    'MarkerFaceColor', [0.85, 0.25, 0.10], ...
    'DisplayName', 'Actual Price');
ylabel('Price (USD/barrel)', 'FontSize', 12, 'FontWeight', 'bold');

yyaxis right
hold on;
bar(data.date(validActual), errorSeries(validActual), 0.65, ...
    'FaceColor', [0.75, 0.75, 0.75], ...
    'EdgeColor', [0.45, 0.45, 0.45], ...
    'DisplayName', 'Error (Model - Actual)');
ylabel('Error (USD/barrel)', 'FontSize', 12, 'FontWeight', 'bold');

xline(datetime(2026, 2, 28), '--k', 'Conflict Start', ...
    'LineWidth', 1.2, ...
    'LabelVerticalAlignment', 'bottom', ...
    'LabelHorizontalAlignment', 'left');

ax = gca;
grid on;
box on;
ax.FontSize = 11;
ax.LineWidth = 1.1;
ax.GridColor = [0.82, 0.82, 0.82];
ax.GridAlpha = 0.9;
ax.Layer = 'top';
xtickformat('yyyy-MM-dd');
xtickangle(30);

title('Actual Price, Model Price and Daily Error', 'FontSize', 15, 'FontWeight', 'bold');
xlabel('Date', 'FontSize', 12, 'FontWeight', 'bold');
legend('Location', 'northwest');

saveas(fig, 'plot_12_price_error_dual_axis.png');

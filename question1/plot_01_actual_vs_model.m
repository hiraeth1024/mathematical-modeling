clear; clc; close all;

data = readtable('final_fine_best_simulation.csv', 'TextType', 'string');
data.date = datetime(data.date, 'InputFormat', 'yyyy-MM-dd');

simPrice = data.sim_price;
actualPrice = data.actual_close;

validActual = ~ismissing(actualPrice);

fig = figure('Color', 'w', 'Position', [100, 100, 1100, 520]);
hold on;
grid on;
box on;

plot(data.date, simPrice, ...
    'LineWidth', 2.2, ...
    'Color', [0.10, 0.35, 0.80], ...
    'DisplayName', 'Model Price');

plot(data.date(validActual), actualPrice(validActual), ...
    'o-', ...
    'LineWidth', 1.8, ...
    'MarkerSize', 5.5, ...
    'Color', [0.85, 0.25, 0.10], ...
    'MarkerFaceColor', [0.85, 0.25, 0.10], ...
    'DisplayName', 'Actual Price');

xline(datetime(2026, 2, 28), '--k', 'Conflict Start', ...
    'LineWidth', 1.2, ...
    'LabelVerticalAlignment', 'bottom', ...
    'LabelHorizontalAlignment', 'left');

title('Brent Crude Oil: Actual vs Model Price', 'FontSize', 15, 'FontWeight', 'bold');
xlabel('Date', 'FontSize', 12);
ylabel('Price (USD/barrel)', 'FontSize', 12);
legend('Location', 'northwest');

ax = gca;
ax.FontSize = 11;
ax.LineWidth = 1;

xtickformat('yyyy-MM-dd');
xtickangle(30);

saveas(fig, 'plot_01_actual_vs_model.png');

clear; clc; close all;

data = readtable('scenario_paths.csv', 'TextType', 'string');
data.date = datetime(data.date, 'InputFormat', 'yyyy-MM-dd');

baseline = data(data.scenario == "baseline", :);

P0 = 73.21;
epsilon = -0.05;

panicMultiplier = 1 + baseline.F_t;
priceElasticityFactor = (baseline.price ./ P0) .^ epsilon;
demandCutFactor = 1 - baseline.Q_t;
effectiveDemand = baseline.D_t;

fig = figure('Color', 'w', 'Position', [100, 100, 1120, 760]);

ax1 = subplot(2, 1, 1);
hold on;
plot(baseline.date, panicMultiplier, ...
    'LineWidth', 2.0, ...
    'Color', [0.85, 0.25, 0.10], ...
    'DisplayName', '1 + F_t');
plot(baseline.date, priceElasticityFactor, ...
    'LineWidth', 2.0, ...
    'Color', [0.10, 0.35, 0.80], ...
    'DisplayName', '(P_t / P_0)^\epsilon');
plot(baseline.date, demandCutFactor, ...
    '--', ...
    'LineWidth', 2.0, ...
    'Color', [0.55, 0.20, 0.75], ...
    'DisplayName', '1 - Q_t');
xline(datetime(2026, 2, 28), '--k', 'Conflict Start', ...
    'LineWidth', 1.2, ...
    'LabelVerticalAlignment', 'bottom', ...
    'LabelHorizontalAlignment', 'left');
legend('Location', 'eastoutside');
style_axis(ax1, 'Demand-Side Component Evolution', 'Multiplier / Factor');

ax2 = subplot(2, 1, 2);
hold on;
plot(baseline.date, effectiveDemand, ...
    'LineWidth', 2.3, ...
    'Color', [0.10, 0.60, 0.30], ...
    'DisplayName', 'Effective Demand D_t');
xline(datetime(2026, 2, 28), '--k', 'Conflict Start', ...
    'LineWidth', 1.2, ...
    'LabelVerticalAlignment', 'bottom', ...
    'LabelHorizontalAlignment', 'left');
legend('Location', 'eastoutside');
style_axis(ax2, 'Effective Demand Evolution', 'Demand (10^4 barrels/day)');

saveas(fig, 'plot_11_demand_components.png');

function style_axis(ax, chartTitle, yLabelText)
    grid(ax, 'on');
    box(ax, 'on');
    ax.FontSize = 11;
    ax.LineWidth = 1.1;
    ax.GridColor = [0.82, 0.82, 0.82];
    ax.GridAlpha = 0.9;
    ax.Layer = 'top';
    title(ax, chartTitle, 'FontSize', 14, 'FontWeight', 'bold');
    xlabel(ax, 'Date', 'FontSize', 11, 'FontWeight', 'bold');
    ylabel(ax, yLabelText, 'FontSize', 11, 'FontWeight', 'bold');
    xtickformat(ax, 'yyyy-MM-dd');
    xtickangle(ax, 25);
end

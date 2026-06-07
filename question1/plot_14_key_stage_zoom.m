clear; clc; close all;

data = readtable('final_fine_best_simulation.csv', 'TextType', 'string');
data.date = datetime(data.date, 'InputFormat', 'yyyy-MM-dd');

simPrice = data.sim_price;
actualPrice = data.actual_close;
validActual = ~ismissing(actualPrice);

fig = figure('Color', 'w', 'Position', [80, 80, 1200, 850]);
tiledlayout(3,1, 'Padding', 'compact', 'TileSpacing', 'compact');

windows = {
    datetime(2026,3,1), datetime(2026,3,12), 'Early Shock Stage';
    datetime(2026,4,7), datetime(2026,4,24), 'Mid-April Correction Stage';
    datetime(2026,5,20), datetime(2026,5,29), 'Late-May Retreat Stage'
};

for i = 1:3
    nexttile;
    startDate = windows{i,1};
    endDate = windows{i,2};
    stageTitle = windows{i,3};

    idx = data.date >= startDate & data.date <= endDate;
    idxActual = validActual & data.date >= startDate & data.date <= endDate;

    hold on;
    plot(data.date(idx), simPrice(idx), ...
        'LineWidth', 2.2, ...
        'Color', [0.10, 0.35, 0.80], ...
        'DisplayName', 'Model Price');

    plot(data.date(idxActual), actualPrice(idxActual), ...
        'o-', ...
        'LineWidth', 1.6, ...
        'MarkerSize', 5.0, ...
        'Color', [0.85, 0.25, 0.10], ...
        'MarkerFaceColor', [0.85, 0.25, 0.10], ...
        'DisplayName', 'Actual Price');

    grid on;
    box on;
    title(stageTitle, 'FontSize', 13, 'FontWeight', 'bold');
    xlabel('Date', 'FontSize', 11, 'FontWeight', 'bold');
    ylabel('Price (USD/barrel)', 'FontSize', 11, 'FontWeight', 'bold');
    legend('Location', 'best');

    ax = gca;
    ax.FontSize = 10.5;
    ax.LineWidth = 1.0;
    ax.GridColor = [0.82, 0.82, 0.82];
    ax.GridAlpha = 0.9;
    xtickformat('yyyy-MM-dd');
    xtickangle(25);
end

saveas(fig, 'plot_14_key_stage_zoom.png');

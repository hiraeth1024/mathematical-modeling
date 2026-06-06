function apply_plot_style(fig, ax, chartTitle, yLabelText)
    set(fig, 'Color', 'w', 'Position', [100, 100, 1120, 560]);

    grid(ax, 'on');
    box(ax, 'on');
    ax.FontSize = 11;
    ax.LineWidth = 1.1;
    ax.GridColor = [0.82, 0.82, 0.82];
    ax.GridAlpha = 0.9;
    ax.MinorGridAlpha = 0.35;
    ax.XColor = [0.20, 0.20, 0.20];
    ax.YColor = [0.20, 0.20, 0.20];
    ax.Layer = 'top';

    title(ax, chartTitle, 'FontSize', 15, 'FontWeight', 'bold');
    xlabel(ax, 'Date', 'FontSize', 12, 'FontWeight', 'bold');
    ylabel(ax, yLabelText, 'FontSize', 12, 'FontWeight', 'bold');

    xtickformat(ax, 'yyyy-MM-dd');
    xtickangle(ax, 30);
end

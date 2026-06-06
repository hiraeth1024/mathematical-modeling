clear; clc; close all;

symbolData = {
    't', '冲突后的第 t 天', '天';
    'P_t', '第 t 天国际原油价格', '美元/桶';
    'P_0', '基准日原油价格', '美元/桶';
    'S_0', '战前基准供给', '万桶/日';
    'D_0', '战前基准需求', '万桶/日';
    'S_t', '第 t 天有效供给', '万桶/日';
    'D_t', '第 t 天有效需求', '万桶/日';
    'L_t', '供应中断量', '万桶/日';
    'R_t', '战略储备释放量', '万桶/日';
    'C_t', '商业库存释放量', '万桶/日';
    'B_t', '绕道运输恢复量', '万桶/日';
    'F_t', '前期恐慌需求放大项', '无量纲';
    'Q_t', '后期需求收缩项', '无量纲';
    'I_t', '第 t 天末剩余商业库存', '万桶';
    'g_t', '归一化供需缺口', '无量纲';
    '\epsilon', '短期需求价格弹性', '无量纲';
    '\beta', '价格调整强度参数', '无量纲'
};

symbolTable = cell2table(symbolData, ...
    'VariableNames', {'Symbol', 'Meaning', 'Unit'});

fig = figure('Color', 'w', 'Position', [120, 80, 980, 520]);

uitable('Data', table2cell(symbolTable), ...
    'ColumnName', symbolTable.Properties.VariableNames, ...
    'Units', 'normalized', ...
    'Position', [0.02, 0.04, 0.96, 0.88], ...
    'FontSize', 11, ...
    'ColumnWidth', {120, 520, 160}, ...
    'RowName', []);

annotation('textbox', [0.02, 0.92, 0.96, 0.06], ...
    'String', 'Symbol Description Table', ...
    'LineStyle', 'none', ...
    'FontSize', 15, ...
    'FontWeight', 'bold', ...
    'HorizontalAlignment', 'center');

saveas(fig, 'plot_06_symbol_table.png');

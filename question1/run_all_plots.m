clear; clc; close all;

scripts = {
    'plot_01_actual_vs_model.m'
    'plot_02_baseline_vs_no_buffer.m'
    'plot_03_baseline_vs_no_inventory.m'
    'plot_04_baseline_vs_no_late_demand_cut.m'
    'plot_05_scenario_summary_table.m'
    'plot_06_symbol_table.m'
};

for i = 1:numel(scripts)
    fprintf('Running %s ...\n', scripts{i});
    run(scripts{i});
end

fprintf('\nAll figures and tables have been generated successfully.\n');

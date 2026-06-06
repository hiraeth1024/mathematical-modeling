# 历史调参归档

本目录保存的是**最终没有作为主模型保留**的调参与试验过程文件。

这些文件不代表无效，它们的作用主要是：

1. 记录尝试过哪些参数方向
2. 说明哪些结构后来被放弃
3. 为论文中的“模型改进过程”提供证据

## 归档内容概览

### 1. 基准仿真

- `run_baseline_simulation.py`
- `baseline_simulation.csv`

### 2. 粗校准

- `coarse_calibration.py`
- `coarse_calibration_results.csv`
- `coarse_best_summary.txt`
- `coarse_best_simulation.csv`

### 3. 后期回落定向调参

- `late_stage_calibration.py`
- `late_stage_calibration_results.csv`
- `late_stage_best_summary.txt`
- `late_stage_best_simulation.csv`

### 4. 联合精调

- `joint_refined_calibration.py`
- `joint_refined_calibration_results.csv`
- `joint_refined_best_summary.txt`
- `joint_refined_best_simulation.csv`

### 5. 两阶段 `L_t` 结构测试

- `two_stage_L_calibration.py`
- `two_stage_L_calibration_results.csv`
- `two_stage_L_best_summary.txt`
- `two_stage_L_best_simulation.csv`

### 6. 两阶段 `F_t` 结构测试

- `two_stage_F_calibration.py`
- `two_stage_F_calibration_results.csv`
- `two_stage_F_best_summary.txt`
- `two_stage_F_best_simulation.csv`

### 7. 两阶段 `L_t + F_t` 联合再平衡

- `joint_two_stage_rebalance.py`
- `joint_two_stage_rebalance_results.csv`
- `joint_two_stage_rebalance_best_summary.txt`
- `joint_two_stage_rebalance_best_simulation.csv`

### 8. 只调 `R_t / C_t / beta` 的深度校准

- `narrow_deep_calibration.py`
- `narrow_deep_calibration_results.csv`
- `narrow_deep_best_summary.txt`
- `narrow_deep_best_simulation.csv`

### 9. 引入 `Q_t` 之前的后期需求收缩测试

- `late_demand_destruction_calibration.py`
- `late_demand_destruction_results.csv`
- `late_demand_destruction_best_summary.txt`
- `late_demand_destruction_best_simulation.csv`

## 使用建议

如果只是继续做论文，不必先看这里，优先看根目录中的：

- [FINAL_MODEL.md](<D:\codespace\mathematical-modeling\FINAL_MODEL.md>)
- [final_fine_calibration.py](<D:\codespace\mathematical-modeling\final_fine_calibration.py>)
- [final_fine_best_summary.txt](<D:\codespace\mathematical-modeling\final_fine_best_summary.txt>)
- [final_fine_best_simulation.csv](<D:\codespace\mathematical-modeling\final_fine_best_simulation.csv>)

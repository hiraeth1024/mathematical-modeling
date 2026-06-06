# 最终模型说明

## 1. 最终保留的模型结构

当前最终保留的短期冲击模型采用以下结构：

1. 供应中断项 `L_t` 使用两阶段台阶下降
2. 恐慌需求项 `F_t` 使用单阶段衰减
3. 供给缓冲项包括：
   - 战略储备释放 `R_t`
   - 商业库存释放 `C_t`
   - 绕道运输恢复 `B_t`
4. 在需求端新增后期需求收缩项 `Q_t`
5. 价格使用归一化供需缺口更新

## 2. 最终推荐文件

- 模型脚本：[final_fine_calibration.py](<D:\codespace\mathematical-modeling\final_fine_calibration.py>)
- 最终参数摘要：[final_fine_best_summary.txt](<D:\codespace\mathematical-modeling\final_fine_best_summary.txt>)
- 最终模拟结果：[final_fine_best_simulation.csv](<D:\codespace\mathematical-modeling\final_fine_best_simulation.csv>)
- 全部候选结果：[final_fine_calibration_results.csv](<D:\codespace\mathematical-modeling\final_fine_calibration_results.csv>)

## 3. 当前最优参数

- `beta = 0.079`
- `tau_R = 10`
- `R_max = 525`
- `C_max = 400`
- `k_C = 0.003`
- `tau_Q = 62`
- `Q_max = 0.08`
- `k_Q = 0.08`

## 4. 当前结果摘要

- `SSE = 2369.6983`
- 峰值 `107.6916`
- 中期均值 `107.1365`
- 5 月下旬均值 `96.1669`
- `2026-05-29` 模拟价格 `93.6200`

## 5. 使用建议

如果后续继续写论文，优先使用：

1. [FINAL_MODEL.md](<D:\codespace\mathematical-modeling\FINAL_MODEL.md>) 说明模型结构
2. [final_fine_best_summary.txt](<D:\codespace\mathematical-modeling\final_fine_best_summary.txt>) 引用参数
3. [final_fine_best_simulation.csv](<D:\codespace\mathematical-modeling\final_fine_best_simulation.csv>) 出图和做对比表
4. [findings.md](<D:\codespace\mathematical-modeling\findings.md>) 回看完整推导和调参逻辑

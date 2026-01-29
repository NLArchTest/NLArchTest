# 进行配对比较分析
import itertools

# 获取所有工具组合
tools = ['JArchitect', 'ArchUnit', 'NLArchTest', 'NLArchTest'] 
tool_combinations = list(itertools.combinations(tools, 2))

# 存储所有p值用于FDR校正
all_p_values = []
all_comparisons = []

# 对每个指标进行配对比较
pairwise_results = {}

for metric in metrics_data.keys():
    pairwise_results[metric] = {}
    print(f"\n【{metric}】配对比较结果：")
    
    for tool1, tool2 in tool_combinations:
        # 检查工具是否存在于当前指标中
        if tool1 in metrics_data[metric] and tool2 in metrics_data[metric]:
            # 提取两个工具的数据
            data1 = metrics_data[metric][tool1]
            data2 = metrics_data[metric][tool2]
            
            # 进行配对t检验
            try:
                t_stat, p_val = stats.ttest_rel(data1, data2)
                pairwise_results[metric][f"{tool1} vs {tool2}"] = {
                    't_statistic': t_stat,
                    'p_value': p_val
                }
                
                print(f"{tool1} vs {tool2}: t={t_stat:.3f}, p={p_val:.3f}")
                
                # 保存p值用于后续FDR校正
                all_p_values.append(p_val)
                all_comparisons.append((metric, tool1, tool2, p_val))
                
            except Exception as e:
                print(f"{tool1} vs {tool2}: 无法计算 (Error: {e})")

# 进行FDR校正
from statsmodels.stats.multitest import fdrcorrection

# 对所有p值进行FDR校正
rejected, corrected_p_values = fdrcorrection(all_p_values, alpha=0.05)

print("\n" + "="*50)
print("FDR校正结果：")
print("="*50)

# 显示校正后的显著结果
significant_results = []
for i, (metric, tool1, tool2, original_p) in enumerate(all_comparisons):
    if rejected[i]:
        significant_results.append({
            'Metric': metric,
            'Comparison': f"{tool1} vs {tool2}",
            'Original p-value': original_p,
            'Corrected p-value': corrected_p_values[i]
        })
        print(f"{metric}: {tool1} vs {tool2} - 原始p={original_p:.3f}, 校正后p={corrected_p_values[i]:.3f} (显著)")

print(f"\n总共 {len(all_comparisons)} 个比较，其中 {sum(rejected)} 个在校正后仍然显著。")
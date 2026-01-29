# 对每个指标进行混合效应模型分析
results = {}

for metric in metrics_data.keys():
    # 筛选当前指标的数据
    metric_data = long_df[long_df['Metric'] == metric].copy()
    
    # 确保数据类型正确
    metric_data['Value'] = pd.to_numeric(metric_data['Value'])
    
    try:
        # 拟合混合效应模型
        # 工具作为固定效应，参与者作为随机效应
        model = mixedlm("Value ~ Tool", metric_data, groups=metric_data["Participant"])
        fitted_model = model.fit()
        
        # 保存结果
        results[metric] = {
            'model': fitted_model,
            'summary': fitted_model.summary()
        }
        
        print(f"\n【{metric}】混合效应模型分析结果：")
        fixed_effect_table = fitted_model.summary().tables[1]
        print(fixed_effect_table)
        
    except Exception as e:
        print(f"\n【{metric}】分析时出错：{e}")
        results[metric] = {'error': str(e)}
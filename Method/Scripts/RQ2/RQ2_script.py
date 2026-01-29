#!/usr/bin/env python3
import subprocess
import os
import sys
import csv
import json
from pathlib import Path

# 配置路径（根据实际情况修改）
DomainAwareLLMtranslator_dir = Path("/data1/Lnike123/Work/playground/DomainAwareLLMtranslator")
input_csv = Path("/data1/Lnike123/Work/playground/Experiment/RQ1/input.csv")
output_csv = Path("/data1/Lnike123/Work/playground/Experiment/RQ1/output.csv")

def process_nl_input(nl_input: str) -> tuple:
    """处理单个自然语言输入，返回(DSL, API, attempts)或失败标记"""
    try:
        os.chdir(DomainAwareLLMtranslator_dir)
        
        # 清理可能存在的旧api.json
        api_json = DomainAwareLLMtranslator_dir / "api.json"
        if api_json.exists():
            api_json.unlink()
        
        # 执行DomainAwareLLMtranslator命令
        result = subprocess.run(
            ["./DomainAwareLLMtranslator", "--nl", nl_input],
            cwd=DomainAwareLLMtranslator_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # 检查命令执行状态
        if result.returncode != 0:
            raise RuntimeError(f"DomainAwareLLMtranslator执行失败，退出码: {result.returncode}\n{result.stderr}")
        
        # 验证api.json生成
        if not api_json.exists():
            raise FileNotFoundError("API文件未生成")
        
        # 读取并解析JSON
        with open(api_json, 'r') as f:
            data = json.load(f)
        
        # 提取关键字段
        dsl = data.get("DSL", "").strip()
        api = data.get("result", "")
        attempts = data.get("attempts", 0)  # 默认值设为0
        
        # 处理API字段格式
        if isinstance(api, list):
            api = ",".join(map(str, api)).strip()
        elif isinstance(api, str):
            api = api.strip()
        
        # 验证必要字段
        if not dsl or not api:
            raise ValueError("DSL或API字段为空")
            
        return (dsl, api, attempts)
    
    except Exception as e:
        print(f"处理失败: {str(e)}", file=sys.stderr)
        return ("Trains Failed", "Trains Failed", "Trains Failed")

def main():
    # 读取输入文件
    try:
        with open(input_csv, 'r') as f:
            reader = csv.reader(f)
            nl_inputs = [row[0].strip() for row in reader if row]
    except FileNotFoundError:
        print(f"错误：输入文件 {input_csv} 未找到", file=sys.stderr)
        sys.exit(1)
    
    # 处理所有输入
    results = []
    for idx, nl in enumerate(nl_inputs, 1):
        print(f"处理中 ({idx}/{len(nl_inputs)}): {nl[:50]}...")
        results.append(process_nl_input(nl))
    
    # 写入输出文件
    with open(output_csv, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["DSL", "API", "Attempts"])  # 新增Attempts列
        for dsl, api, attempts in results:
            writer.writerow([dsl, api, attempts])
    
    print(f"处理完成，共处理 {len(nl_inputs)} 条输入")
    print(f"结果已保存至: {output_csv.absolute()}")

if __name__ == "__main__":
    main()
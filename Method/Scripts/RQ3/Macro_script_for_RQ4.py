#!/usr/bin/env python3
import subprocess
import os
import sys
import csv
import shutil
from pathlib import Path

# 常量路径设置
DomainAwareLLMtranslator_dir = Path("/data1/Lnike123/Work/playground/DomainAwareLLMtranslator")
input_csv = Path("/data1/Lnike123/Work/playground/Experiment/RQ4/dataset/RQ4Rule-input.csv")
experiment_dir = Path("/data1/Lnike123/Work/playground/Experiment/RQ4")
api_json_name = "api.json"

# 3 个 project 名称
projects = ["junit4", "junit5", "plain"]

def process_single_rule(rule_name: str, nl_input: str, project_name: str):
    try:
        print(f"[INFO] 处理规则 {rule_name} for project {project_name}")

        # 切换至 DomainAwareLLMtranslator 目录并清除旧的 api.json
        os.chdir(DomainAwareLLMtranslator_dir)
        api_json = DomainAwareLLMtranslator_dir / api_json_name
        if api_json.exists():
            api_json.unlink()

        # 执行 DomainAwareLLMtranslator 命令
        result = subprocess.run(
            ["./DomainAwareLLMtranslator", "--nl", nl_input],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        if result.returncode != 0:
            raise RuntimeError(f"DomainAwareLLMtranslator 执行失败：{result.stderr}")

        if not api_json.exists():
            raise FileNotFoundError(f"{api_json_name} 未生成")

        # 复制 api.json 到 RQ4 目录并重命名
        dest_filename = f"{project_name}_{rule_name}_api.json"
        dest_path = experiment_dir / dest_filename
        shutil.copy(api_json, dest_path)
        print(f"[INFO] 已复制 {api_json_name} 为 {dest_path}")

        # 构造 Java 命令并执行
        os.chdir(experiment_dir)
        java_cmd = [
            "java", "-jar", "./script/libs/archunit-1.4.0-SNAPSHOT.jar",
            f"./dataset/ArchUnit-Examples-main/example-{project_name}/build/classes",
            "./data/LineageOS-16.0/finalownership.csv",
            f"{project_name}_{rule_name}",
            "./script/libs/enre.json",
            "./ignores.txt",
            f"./{dest_filename}",
            "java"
        ]
        subprocess.run(java_cmd, check=True)
        print(f"[INFO] 已完成 Java 执行：{rule_name} on {project_name}")

    except Exception as e:
        print(f"[ERROR] {rule_name} on {project_name} 失败：{e}", file=sys.stderr)

def main():
    if not input_csv.exists():
        print(f"[ERROR] 输入文件不存在: {input_csv}", file=sys.stderr)
        sys.exit(1)

    # 读取输入的 <ruleName, naturalLanguage>
    with open(input_csv, 'r') as f:
        reader = csv.reader(f)
        rules = [(row[0].strip(), row[1].strip()) for row in reader if len(row) >= 2]

    # 对每一个项目执行三次处理
    for project in projects:
        print(f"\n[INFO] ========== 运行项目 {project} ==========")
        for rule_name, nl in rules:
            process_single_rule(rule_name, nl, project)

if __name__ == "__main__":
    main()

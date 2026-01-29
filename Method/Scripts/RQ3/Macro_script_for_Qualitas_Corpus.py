#!/usr/bin/env python3
import subprocess
import os
import sys
import csv
import shutil
from pathlib import Path

# 常量路径设置
DomainAwareLLMtranslator_dir = Path("/data1/Lnike123/Work/playground/DomainAwareLLMtranslator")
experiment_dir = Path("/data1/Lnike123/Work/playground/Experiment/RQ4")
input_csv = experiment_dir / "dataset" / "RQ4Rule-input-for-opensource.csv"
api_json_dir = experiment_dir / "api_jsons"
opensource_dir = experiment_dir / "dataset" / "opensource"

# 确保必要目录存在
if not input_csv.exists():
    print(f"[ERROR] 输入 CSV 文件不存在: {input_csv}", file=sys.stderr)
    sys.exit(1)

if not opensource_dir.exists():
    print(f"[ERROR] opensource 目录不存在: {opensource_dir}", file=sys.stderr)
    sys.exit(1)

# 动态获取项目列表
projects = [p.name for p in opensource_dir.iterdir() if p.is_dir()]
if not projects:
    print(f"[ERROR] 未在 {opensource_dir} 下找到任何项目文件夹", file=sys.stderr)
    sys.exit(1)

# 确保 api_json_dir 存在
api_json_dir.mkdir(parents=True, exist_ok=True)


def process_single_rule(rule_name: str, nl_input: str, project_name: str):
    try:
        print(f"[INFO] 处理规则 {rule_name} for project {project_name}")

        # 切换至 DomainAwareLLMtranslator 目录并清除旧的 api.json
        os.chdir(DomainAwareLLMtranslator_dir)
        api_json = DomainAwareLLMtranslator_dir / "api.json"
        if api_json.exists():
            api_json.unlink()

        # 执行 DomainAwareLLMtranslator 生成 api.json
        result = subprocess.run(
            ["./DomainAwareLLMtranslator", "--nl", nl_input],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if result.returncode != 0:
            raise RuntimeError(f"DomainAwareLLMtranslator 执行失败：{result.stderr}")
        if not api_json.exists():
            raise FileNotFoundError(f"{api_json} 未生成")

        # 复制并重命名到 api_json_dir
        dest_filename = f"{project_name}_{rule_name}_api.json"
        dest_path = api_json_dir / dest_filename
        shutil.copy(api_json, dest_path)
        print(f"[INFO] 已复制 api.json 为 {dest_path}")

        # 切换至 experiment_dir 执行 ArchUnit
        os.chdir(experiment_dir)
        java_cmd = [
            "java", "-jar", "./script/libs/archunit-1.4.0-SNAPSHOT.jar",
            f"./dataset/opensource/{project_name}",
            "./data/LineageOS-16.0/finalownership.csv",
            f"{project_name}_{rule_name}",
            "./script/libs/enre.json",
            "./ignores.txt",
            str(dest_path),
            "java"
        ]
        subprocess.run(java_cmd, check=True)
        print(f"[INFO] Java 执行完成：{rule_name} on {project_name}")

    except Exception as e:
        print(f"[ERROR] {rule_name} on {project_name} 失败：{e}", file=sys.stderr)


def main():
    # 读取输入 CSV
    with open(input_csv, 'r') as f:
        reader = csv.reader(f)
        rules = [(row[0].strip(), row[1].strip()) for row in reader if len(row) >= 2]

    # 对每个项目和每个规则执行
    for project in projects:
        print(f"\n[INFO] ===== 运行项目 {project} =====")
        for rule_name, nl in rules:
            process_single_rule(rule_name, nl, project)

if __name__ == "__main__":
    main()

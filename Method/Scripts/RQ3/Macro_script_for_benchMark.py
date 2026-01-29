#!/usr/bin/env python3
import subprocess
import os
import sys
from pathlib import Path

# 常量路径设置
experiment_dir = Path("/data1/Lnike123/Work/playground/Experiment/RQ4")
api_json_dir = experiment_dir / "dataset" /"APICASE_for_makingBenchmarkC_1 - opensource"     # 指向存放 *_api.json 文件的目录
opensource_dir = experiment_dir / "dataset" /"opensource"

# 从 opensource_dir 下提取项目名称
if not opensource_dir.exists():
    print(f"[ERROR] opensource 目录不存在: {opensource_dir}", file=sys.stderr)
    sys.exit(1)
projects = [p.name for p in opensource_dir.iterdir() if p.is_dir()]
if not projects:
    print(f"[ERROR] 未在 {opensource_dir} 下找到任何项目文件夹", file=sys.stderr)
    sys.exit(1)


def process_existing_api_json(api_json_path: Path, project_name: str):
    try:
        # 提取 rule_name（去掉后缀 _api）
        rule_name = api_json_path.stem.replace("_api", "")

        print(f"[INFO] 处理 {api_json_path.name} for project {project_name}")

        # 切换至 experiment_dir 执行 Java 命令
        os.chdir(experiment_dir)
        java_cmd = [
            "java", "-jar", "./script/libs/archunit-1.4.0-SNAPSHOT.jar",
            f"./dataset/opensource/{project_name}",
            "./data/LineageOS-16.0/finalownership.csv",
            f"{project_name}_{rule_name}",
            "./script/libs/enre.json",
            "./ignores.txt",
            str(api_json_path),              # 使用 API JSON 文件的实际路径
            "java"
        ]
        subprocess.run(java_cmd, check=True)
        print(f"[INFO] Java 执行完成：{rule_name} on {project_name}")

    except Exception as e:
        print(f"[ERROR] 执行失败 {api_json_path.name} on {project_name}：{e}", file=sys.stderr)


def main():
    # 检查 API JSON 目录
    if not api_json_dir.exists():
        print(f"[ERROR] API JSON 文件夹不存在: {api_json_dir}", file=sys.stderr)
        sys.exit(1)

    # 收集所有 *_api.json 文件
    api_json_files = list(api_json_dir.glob("*Rule*_api.json"))
    if not api_json_files:
        print(f"[ERROR] 未找到任何匹配的 *_api.json 文件", file=sys.stderr)
        sys.exit(1)

    # 针对每个项目和每个规则执行 ArchUnit
    for project in projects:
        print(f"\n[INFO] ===== 处理项目 {project} =====")
        for api_json_file in api_json_files:
            process_existing_api_json(api_json_file, project)

if __name__ == "__main__":
    main()

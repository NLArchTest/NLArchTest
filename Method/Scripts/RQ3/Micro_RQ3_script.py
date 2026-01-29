#!/usr/bin/env python3
import subprocess
import os
import sys
import csv
import shutil
from pathlib import Path

# 配置路径（根据实际情况修改）
DomainAwareLLMtranslator_dir = Path("/data1/Lnike123/Work/playground/DomainAwareLLMtranslator")
input_csv = Path("/data1/Lnike123/Work/playground/Experiment/RQ3/RQ3_input.csv")
experiment_dir = Path("/data1/Lnike123/Work/playground/Experiment/RQ3")

# 确保实验目录存在
experiment_dir.mkdir(parents=True, exist_ok=True)


def process_rule(rule_name: str, nl_input: str):
    
    try:
        # 1. 在 DomainAwareLLMtranslator_dir 下生成 api.json
        os.chdir(DomainAwareLLMtranslator_dir)
        api_json = DomainAwareLLMtranslator_dir / "api.json"
        if api_json.exists():
            api_json.unlink()

        result = subprocess.run(
            ["./DomainAwareLLMtranslator", "--nl", nl_input],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if result.returncode != 0:
            print(f"[ERROR] DomainAwareLLMtranslator 执行失败 ({rule_name})，退出码: {result.returncode}\n{result.stderr}", file=sys.stderr)
            return

        # 2. 验证并复制 api.json
        if not api_json.exists():
            print(f"[ERROR] DomainAwareLLMtranslator 未生成 api.json ({rule_name})", file=sys.stderr)
            return

        target_json = experiment_dir / f"{rule_name}_api.json"
        shutil.copy(api_json, target_json)
        print(f"[INFO] 已复制 api.json -> {target_json}")

        # 3. 切换到 experiment_dir 并运行 archunit
        cmd = [
            "java", "-jar", "./script/libs/archunit-1.4.0-SNAPSHOT.jar",
            f"./mini-dataset/{rule_name}",
            "./data/LineageOS-16.0/finalownership.csv",
            rule_name,
            "./script/libs/enre.json",
            "./ignores.txt",
            f"./{rule_name}_api.json"
        ]
        result = subprocess.run(cmd, cwd=experiment_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode != 0:
            print(f"[ERROR] ArchUnit 执行失败 ({rule_name})，退出码: {result.returncode}\n{result.stderr}", file=sys.stderr)
        else:
            print(f"[INFO] ArchUnit 执行成功 ({rule_name})")

    except Exception as e:
        print(f"[ERROR] 处理失败 ({rule_name}): {e}", file=sys.stderr)


def main():
    # 读取输入文件，格式: ruleName, naturalLanguage
    if not input_csv.exists():
        print(f"[ERROR] 输入文件未找到: {input_csv}", file=sys.stderr)
        sys.exit(1)

    with input_csv.open('r', newline='') as f:
        reader = csv.reader(f)
        for idx, row in enumerate(reader, 1):
            if len(row) < 2:
                print(f"[WARNING] 跳过无效行 {idx}: {row}")
                continue
            rule_name, nl_input = row[0].strip(), row[1].strip()
            print(f"\n[PROCESS] ({idx}) {rule_name}: {nl_input[:50]}...")
            process_rule(rule_name, nl_input)

    print("\n[ALL DONE] 所有任务处理完成。")


if __name__ == "__main__":
    main()

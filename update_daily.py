#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
南方电网 daily3 每日更新提交脚本
用法（在 csg-power-daily3 仓库目录内执行）：
    python update_daily.py ["自定义提交说明"]

行为：
  1. 读取 GitHub Token（优先环境变量 GH_TOKEN，其次 ../csg_token.txt 或 ./csg_token.txt）
  2. 配置 git 远程为 https://<token>@github.com/hxj0515/csg-power-daily3.git
  3. git add -A 并提交（提交信息含当日北京时间）
  4. 推送到 origin 默认分支

注意：Token 仅用于本次推送，不会被写入仓库任何文件。
"""
import os, sys, subprocess, datetime

REPO = "hxj0515/csg-power-daily3"
REPO_DIR = os.path.dirname(os.path.abspath(__file__))

def get_token():
    if os.environ.get("GH_TOKEN"):
        return os.environ["GH_TOKEN"]
    for p in [os.path.join(REPO_DIR, "..", "csg_token.txt"),
              os.path.join(REPO_DIR, "csg_token.txt"),
              r"E:\workbuddy\2026-08-13-10-26-24\csg_token.txt"]:
        try:
            if os.path.exists(p):
                return open(p, "r", encoding="utf-8").read().strip()
        except Exception:
            pass
    return None

def bj_now():
    d = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8)))
    return d

def run(cmd, **kw):
    print("+", " ".join(cmd) if isinstance(cmd, list) else cmd)
    return subprocess.run(cmd, cwd=REPO_DIR, capture_output=True, **kw)

def main():
    token = get_token()
    if not token:
        print("ERROR: 未找到 GH_TOKEN（环境变量或 token 文件）。")
        sys.exit(1)
    msg = sys.argv[1] if len(sys.argv) > 1 else None
    if not msg:
        d = bj_now()
        msg = f"daily: 南方电网动态 {d.strftime('%Y-%m-%d')}"
    # git 配置（若存在则跳过）
    run(["git", "config", "user.name", "csg-daily-bot"], check=False)
    run(["git", "config", "user.email", "bot@csg-daily.local"], check=False)
    # 远程带 token
    remote = f"https://{token}@github.com/{REPO}.git"
    run(["git", "remote", "set-url", "origin", remote], check=False)
    run(["git", "add", "-A"])
    # 若无可提交则退出
    st = run(["git", "status", "--porcelain"])
    if not st.stdout.decode("utf-8", "ignore").strip():
        print("无变更，跳过提交。")
        return
    run(["git", "commit", "-m", msg])
    run(["git", "push", "origin", "HEAD"])
    print("已推送：", msg)

if __name__ == "__main__":
    main()

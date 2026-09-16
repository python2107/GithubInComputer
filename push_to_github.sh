#!/usr/bin/env bash
set -e

# 推送 tkinter-github 项目到 GitHub
# 用法：在本地有网络环境的机器上运行
#   chmod +x push_to_github.sh
#   ./push_to_github.sh <你的GitHub用户名> [仓库名]

USERNAME="${1:-}"
REPO_NAME="${2:-tkinter-github}"
TOKEN_FILE="$HOME/.config/tkinter-github/config.json"

if [ -z "$USERNAME" ]; then
    echo "用法: $0 <GitHub用户名> [仓库名]"
    echo "示例: $0 octocat tkinter-github"
    exit 1
fi

if ! command -v gh >/dev/null 2>&1; then
    echo "请先安装 GitHub CLI (gh): https://cli.github.com/"
    exit 1
fi

if [ ! -f "$TOKEN_FILE" ]; then
    echo "未找到 token 配置文件: $TOKEN_FILE"
    echo "请先在应用里保存 GitHub Personal Access Token"
    exit 1
fi

TOKEN=$(python3 -c "import json; print(json.load(open('$TOKEN_FILE'))['token'])" 2>/dev/null)
if [ -z "$TOKEN" ]; then
    echo "配置文件中没有 token，请先在应用里登录"
    exit 1
fi

# 登录 gh CLI
echo "$TOKEN" | gh auth login --with-token --hostname github.com

# 在 GitHub 上创建仓库
gh repo create "$REPO_NAME" --public --source=. --remote=origin --push || {
    echo "仓库可能已经存在，尝试添加远程地址..."
    git remote remove origin 2>/dev/null || true
    git remote add origin "https://github.com/$USERNAME/$REPO_NAME.git"
}

# 推送代码
git push -u origin main

echo "推送完成: https://github.com/$USERNAME/$REPO_NAME"

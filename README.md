# tkinter GitHub 本地版

一个使用 Python + tkinter 构建的 GitHub 桌面客户端，页面结构与核心功能对标 GitHub.com。支持通过 Personal Access Token 连接 GitHub API，并支持 SSH key 配置用于本地 git 操作。

## 特性

- **22 个完整页面**：登录/配置、Dashboard、仓库列表、仓库主页、代码浏览、提交历史、Issues、Issue 详情、Pull Requests、PR 详情、用户 Profile、Copilot、Stars、Explore、Releases、Actions、Organization、Repo Settings、搜索、通知、Insights、设置。
- GitHub REST API 调用，支持 Token 认证。
- 仓库操作：创建仓库、Star/Unstar、Watch/Unwatch、Fork、删除仓库、修改描述。
- 本地 Git 操作：Push、Pull、Fetch，支持 SSH key 认证。
- 深色 / 浅色主题切换。
- 异步加载，UI 不阻塞。

## 目录结构

```
tkinter-github/
├── main.py              # 应用入口
├── config.py            # 配置持久化
├── theme.py             # 主题/样式系统
├── api/                 # GitHub API 客户端
├── git/                 # 本地 git 操作
├── views/               # 所有页面
├── widgets/             # 共享组件
├── assets/              # 图标/字体资源（预留）
├── requirements.txt
└── README.md
```

## 运行

```bash
# 安装依赖
pip install -r requirements.txt

# 启动应用
python main.py
```

## 首次使用

1. 启动后进入 **Login / Settings** 页面。
2. 输入你的 GitHub **Personal access token**（需要 `repo`、`user`、`notifications` 等权限）。
3. 点击 **Sign in**，验证通过后会跳转到 Dashboard。
4. 左侧导航可切换页面；顶部搜索栏可搜索仓库或用户。

## 配置

配置保存在 `~/.config/tkinter-github/config.json`：

```json
{
  "token": "ghp_xxx",
  "ssh_key_path": "",
  "theme": "dark",
  "username": ""
}
```

## 注意事项

- 这是桌面原生 UI，视觉风格尽量接近 GitHub，但不会与 github.com 像素级一致。
- GitHub API 有速率限制；请妥善保管 Token。
- GitHub Copilot 的核心聊天/补全能力没有公开 REST API，因此 Copilot 页面为配置/占位页。
- 写操作（创建仓库、Star、Fork、Push 等）会真实影响你的 GitHub 账户，请谨慎使用。

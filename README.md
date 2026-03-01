# 科技资讯每日推送

自动抓取过去24小时的科技资讯，通过Server酱推送到微信。

## 功能特点

- 抓取多个科技新闻源的最新资讯
- 自动过滤24小时内的资讯
- 支持手动触发和定时运行
- 通过Server酱推送到微信

## 快速开始

### 1. 配置Server酱

1. 访问 [Server酱官网](https://sct.ftqq.com/)
2. 使用微信扫码登录
3. 在「消息通道」中选择「微信推送」并绑定
4. 获取你的 SendKey

### 2. 配置GitHub Secrets

在你的GitHub仓库中设置 Secrets：

1. 进入仓库 → Settings → Secrets and variables → Actions
2. 点击 "New repository secret"
3. 名称: `SERVERCHAN_KEY`
4. 值: 你的Server酱SendKey

### 3. 定时任务

工作流会在每天 **北京时间 9:30** 自动运行。

> 注：GitHub Actions使用UTC时间，9:30北京时间 = 1:30 UTC

## 本地测试

```bash
# 安装依赖
pip install -r requirements.txt

# 设置环境变量
export SERVERCHAN_KEY="你的SendKey"

# 运行脚本
python fetch_news.py
```

## RSS订阅源

默认包含以下科技新闻源：
- 36氪
- 科技日报
- 爱范儿
- 钛媒体
- 雷锋网
- 品玩
- TechCrunch
- The Verge

可以在 `fetch_news.py` 中修改 `RSS_SOURCES` 列表添加更多源。

## 文件结构

```
tech-news-pusher/
├── .github/
│   └── workflows/
│       └── daily-tech-news.yml  # GitHub Actions工作流
├── fetch_news.py                 # Python抓取脚本
├── requirements.txt              # Python依赖
└── README.md                     # 说明文档
```

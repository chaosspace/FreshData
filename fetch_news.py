#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
科技资讯抓取并推送到微信 (Server酱)
"""

import os
import time
import requests
import feedparser
from datetime import datetime, timedelta

# Server酱配置
# 请在GitHub Secrets中设置 SERVERCHAN_KEY
SERVERCHAN_KEY = os.environ.get('SERVERCHAN_KEY', '')

# RSS订阅源列表 (科技类)
RSS_SOURCES = [
    {
        'name': '36氪',
        'url': 'https://www.36kr.com/feed/'
    },
    {
        'name': '科技日报',
        'url': 'http://stdaily.com/kjrb/yaowen.xml'
    },
    {
        'name': '爱范儿',
        'url': 'https://www.ifanr.com/feed'
    },
    {
        'name': '钛媒体',
        'url': 'https://www.tmtpost.com/feed'
    },
    {
        'name': '雷锋网',
        'url': 'https://www.leiphone.com/feed'
    },
    {
        'name': '品玩',
        'url': 'https://www.pingwest.com/feed'
    },
    {
        'name': 'TechCrunch',
        'url': 'https://techcrunch.com/feed/'
    },
    {
        'name': 'The Verge',
        'url': 'https://www.theverge.com/rss/index.xml'
    }
]

# 时间范围：过去24小时
TIME_RANGE_HOURS = 24


def parse_time(time_str):
    """解析RSS中的时间格式"""
    if not time_str:
        return None
    try:
        # 尝试解析RFC 822格式
        dt = datetime.strptime(time_str, '%a, %d %b %Y %H:%M:%S %z')
        return dt.replace(tzinfo=None)
    except:
        pass
    try:
        dt = feedparser.util._parse_date(time_str)
        if dt:
            return dt.replace(tzinfo=None) if dt.tzinfo else dt
    except:
        pass
    return None


def is_within_24_hours(entry):
    """检查文章是否在过去24小时内"""
    # 尝试获取发布时间
    if hasattr(entry, 'published') and entry.published:
        pub_time = parse_time(entry.published)
    elif hasattr(entry, 'updated') and entry.updated:
        pub_time = parse_time(entry.updated)
    else:
        return False

    if pub_time:
        now = datetime.now()
        time_diff = now - pub_time
        return time_diff.total_seconds() <= TIME_RANGE_HOURS * 3600

    return False


def fetch_news():
    """抓取所有RSS源的最新科技资讯"""
    all_news = []
    now = datetime.now()
    cutoff_time = now - timedelta(hours=TIME_RANGE_HOURS)

    print(f"开始抓取科技资讯... (时间范围: 最近24小时)")
    print(f"截止时间: {cutoff_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 50)

    for source in RSS_SOURCES:
        try:
            print(f"正在抓取: {source['name']}...")
            feed = feedparser.parse(source['url'], timeout=10)

            if feed.bozo:
                print(f"  ⚠ {source['name']} 解析异常")
                continue

            source_news = []
            for entry in feed.entries[:10]:  # 每个源取最新10条
                # 检查是否在时间范围内
                if hasattr(entry, 'published') and entry.published:
                    pub_time = parse_time(entry.published)
                elif hasattr(entry, 'updated') and entry.updated:
                    pub_time = parse_time(entry.updated)
                else:
                    pub_time = None

                if pub_time and pub_time >= cutoff_time:
                    source_news.append({
                        'title': entry.title,
                        'link': entry.link,
                        'published': pub_time.strftime('%m-%d %H:%M') if pub_time else '',
                        'source': source['name']
                    })

            if source_news:
                print(f"  ✓ 获取到 {len(source_news)} 条新资讯")
                all_news.extend(source_news)
            else:
                print(f"  ✓ 无新资讯")

        except Exception as e:
            print(f"  ✗ 抓取失败: {str(e)}")
            continue

    # 按时间排序
    all_news.sort(key=lambda x: x['published'], reverse=True)

    print("-" * 50)
    print(f"共获取 {len(all_news)} 条科技资讯")

    return all_news


def format_news_message(news_list):
    """格式化资讯为消息内容"""
    if not news_list:
        return "过去24小时暂无最新科技资讯"

    message_lines = []

    # 按来源分组
    sources = {}
    for news in news_list:
        source = news['source']
        if source not in sources:
            sources[source] = []
        sources[source].append(news)

    # 生成消息
    for source, items in sources.items():
        message_lines.append(f"### 📰 {source}")
        for news in items[:5]:  # 每个来源最多显示5条
            time_info = f" {news['published']}" if news['published'] else ""
            message_lines.append(f"- [{news['title']}]({news['link']}){time_info}")
        message_lines.append("")

    return "\n".join(message_lines)


def send_to_serverchan(title, content):
    """发送到Server酱"""
    if not SERVERCHAN_KEY:
        print("错误: 未配置 SERVERCHAN_KEY")
        print("请在GitHub Secrets中设置 SERVERCHAN_KEY")
        return False

    url = f"https://sctapi.ftqq.com/{SERVERCHAN_KEY}.send"

    data = {
        "title": title,
        "desp": content
    }

    try:
        response = requests.post(url, data=data, timeout=30)
        result = response.json()

        if result.get('code') == 0:
            print("✓ 消息推送成功!")
            return True
        else:
            print(f"✗ 推送失败: {result.get('message')}")
            return False

    except Exception as e:
        print(f"✗ 请求失败: {str(e)}")
        return False


def main():
    """主函数"""
    print("=" * 50)
    print("科技资讯推送机器人")
    print(f"运行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)

    # 抓取资讯
    news_list = fetch_news()

    # 格式化消息
    title = f"科技资讯简报 ({len(news_list)}条)"
    content = format_news_message(news_list)

    # 添加统计信息
    stats = f"\n---\n> 共抓取 {len(news_list)} 条资讯 | 更新时间: {datetime.now().strftime('%H:%M')}"
    content += stats

    # 打印消息预览
    print("\n消息预览:")
    print("-" * 50)
    print(title)
    print(content[:500] + "..." if len(content) > 500 else content)
    print("-" * 50)

    # 发送到微信
    print("\n正在推送到微信...")
    success = send_to_serverchan(title, content)

    if success:
        print("\n✅ 任务完成!")
    else:
        print("\n❌ 任务失败!")
        # 即使失败也退出0，避免GitHub Actions重复运行
        pass

    return 0


if __name__ == "__main__":
    exit(main())

#!/usr/bin/env python3
"""
Scientific Podcast Summary - 自动总结科学播客内容
支持: Huberman Lab, Nature Podcast
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from typing import Optional
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


# ==================== Configuration ====================

DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")

PODCAST_SOURCES = {
    "huberman": {
        "name": "Huberman Lab",
        "base_url": "https://hubermanlab.com",
        "latest_url": "https://hubermanlab.com/category/podcast-episodes/",
    },
    "nature": {
        "name": "Nature Podcast",
        "base_url": "https://www.nature.com",
        "latest_url": "https://www.nature.com/nature/articles?type=podcast",
    },
}

SUMMARY_PROMPT = """你是一个专业的科学播客内容总结助手。请对以下播客内容进行结构化总结。

要求：
1. 提取核心科学主题和关键发现
2. 使用简洁清晰的语言
3. 保留重要的专业术语并适当解释
4. 突出实用的建议或行动指南

请以JSON格式返回：
{
    "title": "播客标题",
    "publish_date": "发布日期",
    "host": "主持人",
    "guests": ["嘉宾1", "嘉宾2"],
    "summary": "核心主题概述 (200-300字)",
    "key_points": ["要点1", "要点2", "要点3"],
    "actionable_tips": ["建议1", "建议2"],
    "resources": [{"title": "资源名", "url": "链接"}]
}

播客内容：
{content}
"""


# ==================== Utils ====================

def log(msg: str, level: str = "info"):
    """打印日志"""
    prefix = {"info": "ℹ️", "success": "✅", "error": "❌", "warn": "⚠️"}.get(level, "ℹ️")
    print(f"{prefix} {msg}", file=sys.stderr if level == "error" else sys.stdout)


def fetch_url(url: str, headers: Optional[dict] = None) -> Optional[str]:
    """获取URL内容"""
    default_headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    }
    if headers:
        default_headers.update(headers)
    
    try:
        resp = requests.get(url, headers=default_headers, timeout=30)
        resp.raise_for_status()
        return resp.text
    except Exception as e:
        log(f"获取URL失败: {url} - {e}", "error")
        return None


def call_llm(prompt: str) -> Optional[str]:
    """调用LLM API"""
    if not OPENAI_API_KEY:
        log("未设置 OPENAI_API_KEY 环境变量", "error")
        return None
    
    try:
        import openai
        client = openai.OpenAI(
            api_key=OPENAI_API_KEY,
            base_url=OPENAI_BASE_URL,
        )
        
        resp = client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[
                {"role": "system", "content": "你是一个专业的科学内容总结助手。"},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
        )
        return resp.choices[0].message.content
    except Exception as e:
        log(f"LLM API调用失败: {e}", "error")
        return None


# ==================== Podcast Parsers ====================

def parse_huberman_episode(html: str, url: str) -> dict:
    """解析 Huberman Lab 页面"""
    soup = BeautifulSoup(html, "html.parser")
    
    # 提取标题
    title_elem = soup.find("h1", class_=re.compile("entry-title|post-title"))
    title = title_elem.get_text(strip=True) if title_elem else "Unknown"
    
    # 提取发布日期
    date_elem = soup.find("time", class_="entry-date")
    publish_date = date_elem.get("datetime", "") if date_elem else ""
    
    # 提取内容
    content_elem = soup.find("div", class_=re.compile("entry-content|post-content"))
    content = ""
    if content_elem:
        # 移除脚本和样式
        for script in content_elem(["script", "style"]):
            script.decompose()
        content = content_elem.get_text(separator="\n", strip=True)
    
    # 提取嘉宾信息 (通常在标题或内容中)
    guests = []
    guest_match = re.search(r"Dr\.\s+([A-Z][a-z]+\s+[A-Z][a-z]+)", title)
    if guest_match:
        guests.append(guest_match.group(0))
    
    return {
        "title": title,
        "publish_date": publish_date,
        "host": "Andrew Huberman",
        "guests": guests,
        "content": content[:15000],  # 限制长度
        "source_url": url,
    }


def parse_nature_podcast(html: str, url: str) -> dict:
    """解析 Nature Podcast 页面"""
    soup = BeautifulSoup(html, "html.parser")
    
    # 提取标题
    title_elem = soup.find("h1") or soup.find("h2", class_=re.compile("title"))
    title = title_elem.get_text(strip=True) if title_elem else "Unknown"
    
    # 提取发布日期
    date_elem = soup.find("time") or soup.find("span", class_=re.compile("date"))
    publish_date = date_elem.get_text(strip=True) if date_elem else ""
    
    # 提取内容
    content_elem = soup.find("div", class_=re.compile("article-body|content"))
    content = ""
    if content_elem:
        for script in content_elem(["script", "style"]):
            script.decompose()
        content = content_elem.get_text(separator="\n", strip=True)
    
    return {
        "title": title,
        "publish_date": publish_date,
        "host": "Nature Podcast",
        "guests": [],
        "content": content[:15000],
        "source_url": url,
    }


def parse_generic_page(html: str, url: str) -> dict:
    """通用页面解析"""
    soup = BeautifulSoup(html, "html.parser")
    
    # 尝试提取标题
    title = "Unknown"
    for selector in ["h1", "h2", "title"]:
        elem = soup.find(selector)
        if elem:
            title = elem.get_text(strip=True)
            break
    
    # 提取正文内容
    content = ""
    for selector in ["article", "main", ".content", "#content", ".post"]:
        elem = soup.find(selector)
        if elem:
            content = elem.get_text(separator="\n", strip=True)
            break
    
    if not content:
        # 退回到提取所有段落
        paragraphs = soup.find_all("p")
        content = "\n\n".join(p.get_text(strip=True) for p in paragraphs[:20])
    
    return {
        "title": title,
        "publish_date": "",
        "host": "",
        "guests": [],
        "content": content[:15000],
        "source_url": url,
    }


# ==================== Feed Discovery ====================

def get_latest_huberman_url() -> Optional[str]:
    """获取最新 Huberman Lab 剧集URL"""
    html = fetch_url(PODCAST_SOURCES["huberman"]["latest_url"])
    if not html:
        return None
    
    soup = BeautifulSoup(html, "html.parser")
    
    # 查找最新剧集链接
    link = soup.find("a", href=re.compile(r"/\d{4}/\d{2}/\d{2}/"))
    if link:
        return link.get("href")
    
    # 备选方案
    for article in soup.find_all("article"):
        link = article.find("a", href=True)
        if link:
            href = link.get("href")
            if "/" in href:
                return urljoin(PODCAST_SOURCES["huberman"]["base_url"], href)
    
    return None


def get_latest_nature_url() -> Optional[str]:
    """获取最新 Nature Podcast 剧集URL"""
    html = fetch_url(PODCAST_SOURCES["nature"]["latest_url"])
    if not html:
        return None
    
    soup = BeautifulSoup(html, "html.parser")
    
    # 查找最新podcast链接
    for link in soup.find_all("a", href=True):
        href = link.get("href", "")
        if "/nature/articles/" in href:
            return urljoin(PODCAST_SOURCES["nature"]["base_url"], href)
    
    return None


# ==================== Summary Generation ====================

def generate_summary(episode_data: dict) -> dict:
    """使用LLM生成总结"""
    prompt = SUMMARY_PROMPT.format(content=episode_data["content"])
    
    response = call_llm(prompt)
    if not response:
        log("LLM生成失败，使用基础提取", "warn")
        return fallback_summary(episode_data)
    
    # 解析JSON响应
    try:
        # 尝试提取JSON块
        json_match = re.search(r'\{[\s\S]*\}', response)
        if json_match:
            summary_data = json.loads(json_match.group())
            summary_data["source_url"] = episode_data.get("source_url", "")
            return summary_data
    except json.JSONDecodeError:
        pass
    
    # 如果JSON解析失败，使用原始响应
    return {
        "title": episode_data.get("title", "Unknown"),
        "publish_date": episode_data.get("publish_date", ""),
        "host": episode_data.get("host", ""),
        "guests": episode_data.get("guests", []),
        "summary": response[:500],
        "key_points": [],
        "actionable_tips": [],
        "resources": [{"title": "原文链接", "url": episode_data.get("source_url", "")}],
        "source_url": episode_data.get("source_url", ""),
    }


def fallback_summary(episode_data: dict) -> dict:
    """LLM失败时的基础提取"""
    content = episode_data.get("content", "")
    
    # 简单提取前几个段落作为关键要点
    paragraphs = [p.strip() for p in content.split("\n\n") if len(p.strip()) > 50][:5]
    
    return {
        "title": episode_data.get("title", "Unknown"),
        "publish_date": episode_data.get("publish_date", ""),
        "host": episode_data.get("host", ""),
        "guests": episode_data.get("guests", []),
        "summary": paragraphs[0] if paragraphs else "",
        "key_points": paragraphs[1:4] if len(paragraphs) > 1 else [],
        "actionable_tips": [],
        "resources": [{"title": "原文链接", "url": episode_data.get("source_url", "")}],
        "source_url": episode_data.get("source_url", ""),
    }


# ==================== Output Formatters ====================

def format_markdown(summary: dict) -> str:
    """格式化为 Markdown"""
    lines = [
        f"# 🎙️ {summary['title']}",
        "",
        f"**发布时间:** {summary.get('publish_date', 'N/A')}",
        f"**主持人:** {summary.get('host', 'N/A')}",
    ]
    
    if summary.get('guests'):
        lines.append(f"**嘉宾:** {', '.join(summary['guests'])}")
    
    lines.extend(["", "---", ""])
    
    # 核心主题
    lines.extend(["## 📝 核心主题", ""])
    lines.append(summary.get('summary', '暂无概述'))
    lines.append("")
    
    # 关键要点
    if summary.get('key_points'):
        lines.extend(["## 🔬 关键要点", ""])
        for i, point in enumerate(summary['key_points'], 1):
            lines.append(f"{i}. {point}")
        lines.append("")
    
    # 实用建议
    if summary.get('actionable_tips'):
        lines.extend(["## 💡 实用建议", ""])
        for tip in summary['actionable_tips']:
            lines.append(f"- {tip}")
        lines.append("")
    
    # 资源链接
    if summary.get('resources'):
        lines.extend(["## 📚 相关资源", ""])
        for res in summary['resources']:
            title = res.get('title', '链接')
            url = res.get('url', '#')
            lines.append(f"- [{title}]({url})")
        lines.append("")
    
    lines.extend(["---", f"\n*生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}*"])
    
    return "\n".join(lines)


def format_json(summary: dict) -> str:
    """格式化为 JSON"""
    summary["generated_at"] = datetime.now().isoformat()
    return json.dumps(summary, ensure_ascii=False, indent=2)


# ==================== Main ====================

def main():
    parser = argparse.ArgumentParser(
        description="自动总结科学播客内容 (Huberman Lab / Nature Podcast)"
    )
    parser.add_argument(
        "--podcast",
        choices=["huberman", "nature"],
        default="huberman",
        help="选择播客源 (默认: huberman)",
    )
    parser.add_argument(
        "--url",
        help="直接提供播客页面URL",
    )
    parser.add_argument(
        "--output", "-o",
        help="输出文件路径",
    )
    parser.add_argument(
        "--format",
        choices=["markdown", "json"],
        default="markdown",
        help="输出格式 (默认: markdown)",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="显示详细日志",
    )
    
    args = parser.parse_args()
    
    # 获取目标URL
    target_url = args.url
    if not target_url:
        log(f"正在获取最新 {PODCAST_SOURCES[args.podcast]['name']} 剧集...")
        if args.podcast == "huberman":
            target_url = get_latest_huberman_url()
        else:
            target_url = get_latest_nature_url()
    
    if not target_url:
        log("无法获取播客URL", "error")
        sys.exit(1)
    
    log(f"解析页面: {target_url}")
    
    # 获取页面内容
    html = fetch_url(target_url)
    if not html:
        sys.exit(1)
    
    # 解析内容
    if args.podcast == "huberman":
        episode_data = parse_huberman_episode(html, target_url)
    elif args.podcast == "nature":
        episode_data = parse_nature_podcast(html, target_url)
    else:
        episode_data = parse_generic_page(html, target_url)
    
    if not episode_data.get("content"):
        log("无法提取页面内容", "error")
        sys.exit(1)
    
    log(f"提取内容长度: {len(episode_data['content'])} 字符")
    
    # 生成总结
    log("正在生成AI总结...")
    summary = generate_summary(episode_data)
    
    # 格式化输出
    if args.format == "json":
        output = format_json(summary)
    else:
        output = format_markdown(summary)
    
    # 输出结果
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        log(f"已保存到: {args.output}", "success")
    else:
        print(output)


if __name__ == "__main__":
    main()

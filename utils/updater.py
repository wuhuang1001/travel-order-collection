"""
版本更新检查模块

功能：
- 读取本地版本（从 pyproject.toml）
- 多源获取远程版本（Gitee → jsDelivr → GitHub）
- 后台异步检查（不阻塞主线程）
- 缓存管理（保存/读取更新状态）
- 手动触发同步检查
"""

import json
import os
import re
import threading
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

import requests

from utils.simple_output import info, success, error

# 配置常量
GITEE_USER = "wuhuang1001"
GITEE_REPO = "tool-versions"
GITEE_FILE = "travel-order-collection.json"
GITHUB_USER = "wuhuang1001"
GITHUB_REPO = "travel-order-collection"

VERSION_SOURCES = [
    {
        "name": "Gitee",
        "url": f"https://gitee.com/{GITEE_USER}/{GITEE_REPO}/raw/main/{GITEE_FILE}",
        "timeout": 3,
    },
    {
        "name": "jsDelivr",
        "url": f"https://cdn.jsdelivr.net/gh/{GITHUB_USER}/{GITHUB_REPO}@main/version.json",
        "timeout": 3,
    },
    {
        "name": "GitHub",
        "url": f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/main/version.json",
        "timeout": 5,
    },
]

CACHE_FILE = ".update_cache.json"
CACHE_EXPIRE_DAYS = 7

# 后台线程锁，防止重复启动
_update_lock = threading.Lock()
_update_thread_started = False


def get_local_version() -> str:
    """
    从 pyproject.toml 读取本地版本号

    Returns:
        str: 本地版本号，如 "0.1.0"
    """
    pyproject_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "pyproject.toml")

    with open(pyproject_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 匹配 version = "x.x.x"
    match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
    if match:
        return match.group(1)

    return "0.0.0"


def compare_versions(v1: str, v2: str) -> int:
    """
    比较两个版本号

    Args:
        v1: 版本号1
        v2: 版本号2

    Returns:
        int: -1 表示 v1 < v2，0 表示相等，1 表示 v1 > v2
    """
    def parse_version(v):
        return [int(x) for x in v.split(".")]

    p1, p2 = parse_version(v1), parse_version(v2)

    # 补齐版本号长度
    max_len = max(len(p1), len(p2))
    p1.extend([0] * (max_len - len(p1)))
    p2.extend([0] * (max_len - len(p2)))

    if p1 < p2:
        return -1
    elif p1 > p2:
        return 1
    return 0


def fetch_remote_version(source: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    从指定源获取远程版本信息

    Args:
        source: 源配置字典，包含 url 和 timeout

    Returns:
        Optional[Dict]: 版本信息字典，失败返回 None
    """
    try:
        response = requests.get(
            source["url"],
            timeout=source["timeout"],
            headers={"User-Agent": "Mozilla/5.0"},
        )
        response.raise_for_status()
        return response.json()
    except Exception:
        return None


def get_remote_version() -> Optional[Dict[str, Any]]:
    """
    按优先级从多个源获取远程版本信息

    Returns:
        Optional[Dict]: 版本信息字典，所有源都失败返回 None
    """
    for source in VERSION_SOURCES:
        result = fetch_remote_version(source)
        if result and "version" in result:
            return result

    return None


def read_cache() -> Optional[Dict[str, Any]]:
    """
    读取本地缓存

    Returns:
        Optional[Dict]: 缓存内容，不存在或过期返回 None
    """
    if not os.path.exists(CACHE_FILE):
        return None

    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            cache = json.load(f)

        # 检查缓存是否过期
        last_check = datetime.fromisoformat(cache.get("last_check", "2000-01-01"))
        if datetime.now() - last_check > timedelta(days=CACHE_EXPIRE_DAYS):
            return None

        return cache
    except Exception:
        return None


def save_cache(data: Dict[str, Any]) -> None:
    """
    保存缓存到本地

    Args:
        data: 要缓存的数据
    """
    data["last_check"] = datetime.now().isoformat()

    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def show_update_notice() -> None:
    """
    显示缓存的更新提示（如果有）
    """
    cache = read_cache()

    if cache and cache.get("has_update"):
        local_version = get_local_version()
        remote_version = cache.get("latest_version", "")

        # 再次检查版本，可能用户已经更新了
        if compare_versions(local_version, remote_version) < 0:
            info(f"发现新版本: v{remote_version} (当前: v{local_version})")
            # if cache.get("changelog"):
                # info(f"    更新内容: {cache['changelog']}")
            # if cache.get("download_url"):
                # info(f"    下载地址: {cache['download_url']}")


def _do_async_check() -> None:
    """
    执行异步检查（内部函数，在后台线程中运行）
    """
    local_version = get_local_version()
    remote_info = get_remote_version()

    if remote_info:
        remote_version = remote_info.get("version", "0.0.0")

        if compare_versions(local_version, remote_version) < 0:
            # 有新版本
            save_cache({
                "has_update": True,
                "latest_version": remote_version,
                "changelog": remote_info.get("changelog", ""),
                "download_url": remote_info.get("download_url", ""),
            })
        else:
            # 无新版本
            save_cache({"has_update": False})


def check_update_async() -> None:
    """
    启动后台异步检查（不阻塞主线程）
    """
    global _update_thread_started

    # 使用锁防止重复启动后台线程
    with _update_lock:
        if _update_thread_started:
            return
        _update_thread_started = True

    thread = threading.Thread(
        target=_do_async_check,
        name="update_check",
        daemon=True,  # 主程序退出时自动终止
    )
    thread.start()


def check_update_sync() -> bool:
    """
    同步检查更新（阻塞，用于 --check-update 参数）

    Returns:
        bool: 是否有新版本
    """
    info("正在检查更新...")

    local_version = get_local_version()
    remote_info = get_remote_version()

    if not remote_info:
        error("无法获取版本信息，请检查网络连接")
        return False

    remote_version = remote_info.get("version", "0.0.0")
    result = compare_versions(local_version, remote_version)

    if result < 0:
        success(f"发现新版本: v{remote_version} (当前: v{local_version})")
        if remote_info.get("changelog"):
            info(f"    更新内容: {remote_info['changelog']}")
        if remote_info.get("download_url"):
            info(f"    下载地址: {remote_info['download_url']}")

        # 保存到缓存
        save_cache({
            "has_update": True,
            "latest_version": remote_version,
            "changelog": remote_info.get("changelog", ""),
            "download_url": remote_info.get("download_url", ""),
        })
        return True
    elif result == 0:
        success(f"当前已是最新版本: v{local_version}")
        save_cache({"has_update": False})
        return False
    else:
        info(f"本地版本 ({local_version}) 比远程版本 ({remote_version}) 新")
        return False

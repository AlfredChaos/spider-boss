"""
Boss直聘爬虫配置文件
"""

import os
from pathlib import Path

# 基础配置
BASE_DIR = Path(__file__).parent
PROJECT_ROOT = BASE_DIR.parent

# 浏览器配置
BROWSER_CONFIG = {
    "headless": False,  # 是否无头模式
    "user_data_dir": str(BASE_DIR / "browser_data"),  # 浏览器数据目录
    "viewport": {"width": 1920, "height": 1080},  # 浏览器窗口大小
    "timeout": 30000,  # 默认超时时间（毫秒）
}

# Boss直聘相关URL
BOSS_URLS = {
    "home": "https://www.zhipin.com/",
    "login": "https://login.zhipin.com/login",
    "job_search": "https://www.zhipin.com/web/geek/job",
    "chat": "https://www.zhipin.com/web/geek/chat",
}

# 登录配置
LOGIN_CONFIG = {
    "auth_file": str(BASE_DIR / "boss_auth.json"),  # 认证状态保存文件
    "max_login_wait": 300,  # 手动登录最大等待时间（秒）
    "auth_expire_days": 7,  # 认证状态过期天数
}

# 反检测配置
ANTI_DETECTION = {
    "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "browser_args": [
        "--no-sandbox",
        "--disable-blink-features=AutomationControlled",
        "--disable-web-security",
        "--disable-features=VizDisplayCompositor",
        "--disable-dev-shm-usage",
    ]
}

# 日志配置
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "log_file": str(BASE_DIR / "boss_spider.log"),
}

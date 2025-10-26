"""
Boss直聘自动登录脚本
使用Playwright实现持久化登录功能
"""

import asyncio
import json
import os
from pathlib import Path
from playwright.async_api import async_playwright
import time


class BossLoginManager:
    def __init__(self, user_data_dir=None):
        """
        初始化Boss登录管理器

        Args:
            user_data_dir (str): 用户数据目录路径，用于保存浏览器状态
        """
        self.base_dir = Path(__file__).parent
        self.user_data_dir = user_data_dir or str(
            self.base_dir / "browser_data")
        self.auth_file = self.base_dir / "boss_auth.json"
        self.boss_url = "https://www.zhipin.com/"
        self.login_url = "https://login.zhipin.com/login"

    async def save_auth_state(self, context):
        """
        保存浏览器认证状态到JSON文件

        Args:
            context: Playwright浏览器上下文
        """
        try:
            # 直接使用 Playwright 的内置方法保存状态到文件
            await context.storage_state(path=str(self.auth_file))
            print(f"✅ 登录状态已保存到: {self.auth_file}")
            return True
        except Exception as e:
            print(f"❌ 保存登录状态失败: {e}")
            return False

    async def load_auth_state(self):
        """
        从JSON文件加载浏览器认证状态

        Returns:
            str | None: 认证状态文件路径，如果文件不存在则返回None
        """
        try:
            if not self.auth_file.exists():
                print("📝 未找到保存的登录状态，需要重新登录")
                return None

            print("✅ 找到已保存的登录状态文件")
            return str(self.auth_file)
        except Exception as e:
            print(f"❌ 加载登录状态失败: {e}")
            return None

    async def is_logged_in_by_cookies(self, context):
        """依据 cookie 判断是否登录（尽量避免误判）。"""
        try:
            cookies = await context.cookies()
            if not cookies:
                return False
            auth_cookie_names = {
                "geek_u", "geek_uid", "zp_token", "sid", "wtk", "boss_token", "boss_u"
            }
            domains = ("zhipin.com", ".zhipin.com")
            for ck in cookies:
                name = ck.get("name", "")
                value = ck.get("value", "")
                domain = ck.get("domain", "")
                if any(d in domain for d in domains) and name in auth_cookie_names and value:
                    return True
            return False
        except Exception:
            return False

    async def is_logged_in_by_local_storage(self, context):
        """依据 localStorage 中的 token/uid 判断是否登录。"""
        try:
            state = await context.storage_state()
            origins = state.get("origins", []) if isinstance(state, dict) else []
            for origin in origins:
                if "zhipin.com" in origin.get("origin", ""):
                    for item in origin.get("localStorage", []) or []:
                        key = item.get("name", "").lower()
                        val = (item.get("value", "") or "").strip()
                        if val and ("token" in key or "uid" in key or "user" in key):
                            return True
            return False
        except Exception:
            return False

    async def verify_auth_by_navigation(self, page):
        """访问受限页面（如聊天页）判断是否跳转登录页面。"""
        try:
            target = "https://www.zhipin.com/web/geek/chat"
            await page.goto(target, wait_until="networkidle")
            # 若仍在聊天页，且未出现登录提示，则认为已登录
            if "/web/geek/chat" in page.url and "login" not in page.url:
                return True
            # 被重定向到登录页
            if "login" in page.url:
                return False
            # 兜底：查找明显的登录入口元素
            login_btn = await page.query_selector('.btn-sign-up, .login-btn, [data-track="login"]')
            return not bool(login_btn)
        except Exception:
            return False

    async def check_login_status(self, page, fast_only=False):
        """
        检查当前页面的登录状态，可选择仅快速检测。
        fast_only=True 时，不进行导航，仅基于 DOM/cookie/storage 判断。
        """
        try:
            await page.wait_for_load_state('domcontentloaded', timeout=10000)
            context = page.context

            # 1) cookie 和 localStorage 快速判断
            if await self.is_logged_in_by_cookies(context):
                print("✅ 通过 cookie 判断已登录")
                return True
            if await self.is_logged_in_by_local_storage(context):
                print("✅ 通过 localStorage 判断已登录")
                return True

            # 2) DOM 兜底（不稳定但无副作用）
            login_btn = await page.query_selector('.btn-sign-up, .login-btn, [data-track="login"]')
            user_info = await page.query_selector('.user-nav, .user-info, .avatar, [data-track="user"]')
            if user_info and not login_btn:
                print("✅ 通过 DOM 判断已登录")
                return True

            if fast_only:
                return False

            # 3) 导航到受限页进行强验证（最可靠）
            if await self.verify_auth_by_navigation(page):
                print("✅ 通过访问受限页面判断已登录")
                return True

            # 4) URL 兜底
            current_url = page.url
            if any(p in current_url for p in ['/web/user/', '/web/geek/', '/web/boss/']) and 'login' not in current_url:
                print("✅ 根据 URL 兜底判断已登录")
                return True

            return False
        except Exception as e:
            print(f"⚠️ 检查登录状态时出错: {e}")
            return False

    async def manual_login(self, page):
        """
        引导用户手动登录

        Args:
            page: Playwright页面对象
        """
        print("\n🔐 请在浏览器中手动完成登录操作...")
        print("📋 登录步骤:")
        print("   1. 输入手机号/邮箱")
        print("   2. 输入密码或验证码")
        print("   3. 完成人机验证（如有）")
        print("   4. 点击登录按钮")
        print("\n⏳ 等待登录完成...")

        # 等待用户手动登录
        max_wait_time = 300  # 5分钟超时
        start_time = time.time()

        while time.time() - start_time < max_wait_time:
            if await self.check_login_status(page, fast_only=True):
                print("🎉 登录成功！")
                return True
            await asyncio.sleep(2)

        print("⏰ 登录超时，请重试")
        return False

    async def auto_login_with_saved_state(self, context, page):
        """
        使用保存的状态自动登录

        Args:
            context: Playwright浏览器上下文
            page: Playwright页面对象

        Returns:
            bool: 是否登录成功
        """
        try:
            print("🔄 尝试使用保存的登录状态...")

            # 访问Boss直聘首页
            await page.goto(self.boss_url, wait_until='networkidle')

            # 检查登录状态
            if await self.check_login_status(page, fast_only=False):
                print("✅ 自动登录成功！")
                return True
            else:
                print("❌ 保存的登录状态无效，需要重新登录")
                return False

        except Exception as e:
            print(f"❌ 自动登录失败: {e}")
            return False

    async def start_browser_session(self, headless=False, save_auth=True):
        """
        启动浏览器会话并处理登录

        Args:
            headless (bool): 是否无头模式运行
            save_auth (bool): 是否保存认证状态

        Returns:
            tuple: (browser, context, page) 或 None
        """
        async with async_playwright() as p:
            try:
                # 尝试加载保存的认证状态文件路径
                auth_state_path = await self.load_auth_state()

                # 启动浏览器（不使用 user_data_dir）
                browser_args = [
                    '--no-sandbox',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-web-security',
                    '--disable-features=VizDisplayCompositor'
                ]
                browser = await p.chromium.launch(
                    headless=headless,
                    args=browser_args
                )

                # 创建浏览器上下文
                context_options = {
                    'viewport': {'width': 1920, 'height': 1080},
                    'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                }

                # 如果有保存的认证状态文件，则使用它
                if auth_state_path:
                    context_options['storage_state'] = auth_state_path

                context = await browser.new_context(**context_options)
                page = await context.new_page()

                # 设置额外的反检测措施
                await page.add_init_script("""
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined,
                    });
                """)

                login_success = False

                # 如果有保存的状态，尝试自动登录
                if auth_state_path:
                    login_success = await self.auto_login_with_saved_state(context, page)

                # 如果自动登录失败，引导手动登录
                if not login_success:
                    await page.goto(self.login_url, wait_until='networkidle')
                    login_success = await self.manual_login(page)

                # 如果登录成功且需要保存状态
                if login_success and save_auth:
                    await self.save_auth_state(context)

                if login_success:
                    print("🚀 浏览器会话已准备就绪！")
                    return browser, context, page
                else:
                    await browser.close()
                    return None

            except Exception as e:
                print(f"❌ 启动浏览器会话失败: {e}")
                return None


async def main():
    """
    主函数 - 演示登录功能
    """
    print("🤖 Boss直聘自动登录助手")
    print("=" * 50)

    # 创建登录管理器
    login_manager = BossLoginManager()

    # 启动浏览器会话
    result = await login_manager.start_browser_session(headless=False)

    if result:
        browser, context, page = result

        print("\n✅ 登录完成！浏览器将保持打开状态...")
        print("💡 您现在可以在浏览器中进行其他操作")
        print("🔄 下次运行时将自动使用保存的登录状态")

        # 保持浏览器打开，等待用户操作
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n👋 正在关闭浏览器...")
            await browser.close()
    else:
        print("❌ 登录失败，请检查网络连接或重试")

if __name__ == "__main__":
    # 运行主函数
    asyncio.run(main())

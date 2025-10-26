#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Boss直聘消息页面爬虫脚本
实现自动化浏览器操作，获取聊天页面HTML内容
"""

import asyncio
import os
import time
from pathlib import Path
from typing import Optional, List, Dict

import requests
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright, Browser, Page, BrowserContext


class BossCaptureSpider:
    """Boss直聘消息页面爬虫类"""

    def __init__(self):
        """初始化爬虫实例"""
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.static_dir = Path(__file__).parent / "static"

        # 确保static目录存在
        self.static_dir.mkdir(exist_ok=True)

    async def start_browser(self) -> None:
        """
        启动浏览器实例
        使用Chromium浏览器，启用头部模式以便用户交互
        """
        try:
            print("🚀 正在启动浏览器...")
            playwright = await async_playwright().start()

            # 启动浏览器，设置为有头模式以便用户登录
            self.browser = await playwright.chromium.launch(
                headless=False,  # 有头模式，方便用户登录
                args=[
                    '--no-sandbox',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-web-security',
                    '--disable-features=VizDisplayCompositor'
                ]
            )

            # 创建浏览器上下文
            self.context = await self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )

            # 创建新页面
            self.page = await self.context.new_page()

            print("✅ 浏览器启动成功")

        except Exception as e:
            print(f"❌ 浏览器启动失败: {e}")
            raise

    async def navigate_to_boss_homepage(self) -> None:
        """
        导航到Boss直聘首页
        """
        try:
            print("🌐 正在导航到Boss直聘首页...")

            # 导航到Boss直聘首页
            await self.page.goto("https://www.zhipin.com/", wait_until="networkidle")

            # 等待页面加载完成
            await self.page.wait_for_load_state("domcontentloaded")

            print("✅ 成功导航到Boss直聘首页")

        except Exception as e:
            print(f"❌ 导航到首页失败: {e}")
            raise

    def wait_for_user_login(self) -> None:
        """
        显示提示信息，等待用户手动登录
        """
        try:
            print("\n" + "="*60)
            print("📝 请在浏览器中手动完成登录操作")
            print("   1. 点击登录按钮")
            print("   2. 输入账号密码或使用其他登录方式")
            print("   3. 完成登录后，请回到此终端")
            print("   4. 按回车键继续执行脚本...")
            print("="*60)

            # 等待用户按回车键
            input("\n按回车键继续...")

            print("✅ 用户确认登录完成，继续执行...")

        except KeyboardInterrupt:
            print("\n❌ 用户中断操作")
            raise
        except Exception as e:
            print(f"❌ 等待用户登录时发生错误: {e}")
            raise

    async def navigate_to_chat_page(self) -> None:
        """
        自动跳转到Boss直聘消息页面
        """
        try:
            print("💬 正在跳转到消息页面...")

            # 跳转到聊天页面
            await self.page.goto("https://www.zhipin.com/web/geek/chat", wait_until="networkidle")

            # 等待页面加载完成
            await self.page.wait_for_load_state("domcontentloaded")

            print("⏳ 等待页面内容完全加载...")

            # 等待加载动画消失，这表示页面内容已经开始渲染
            try:
                await self.page.wait_for_selector(".page-loading", state="hidden", timeout=30000)
                print("✅ 加载动画已消失")
            except Exception as e:
                print(f"⚠️  等待加载动画消失超时: {e}")

            # 等待聊天相关元素出现（多种可能的选择器）
            chat_selectors = [
                ".chat-conversation",  # 聊天对话容器
                ".message-list",       # 消息列表
                ".chat-list",          # 聊天列表
                ".conversation-list",  # 对话列表
                "[class*='chat']",     # 包含chat的类名
                "[class*='message']",  # 包含message的类名
                ".geek-chat",          # geek聊天容器
            ]

            chat_element_found = False
            for selector in chat_selectors:
                try:
                    await self.page.wait_for_selector(selector, timeout=10000)
                    print(f"✅ 找到聊天元素: {selector}")
                    chat_element_found = True
                    break
                except:
                    continue

            if not chat_element_found:
                print("⚠️  未找到明确的聊天元素，继续等待...")

            # 额外等待确保所有动态内容加载完成
            print("⏳ 等待动态内容完全加载...")
            await asyncio.sleep(5)

            # 等待网络请求完成
            await self.page.wait_for_load_state("networkidle")

            print("✅ 成功跳转到消息页面并等待内容加载完成")

        except Exception as e:
            print(f"❌ 跳转到消息页面失败: {e}")
            raise

    async def get_page_cookies(self) -> dict:
        """
        获取当前页面的cookies

        Returns:
            dict: cookies字典
        """
        try:
            cookies = await self.context.cookies()
            cookie_dict = {}
            for cookie in cookies:
                cookie_dict[cookie['name']] = cookie['value']
            return cookie_dict
        except Exception as e:
            print(f"❌ 获取cookies失败: {e}")
            return {}

    async def get_page_content(self) -> str:
        """
        直接从Playwright页面获取HTML内容

        Returns:
            str: 页面HTML内容
        """
        try:
            print("📄 正在获取页面HTML内容...")

            # 直接从当前页面获取HTML内容
            html_content = await self.page.content()

            # 检查内容是否包含实际的聊天数据
            if "加载中" in html_content or len(html_content) < 10000:
                print("⚠️  检测到页面可能仍在加载，再次等待...")

                # 再次等待并尝试获取
                await asyncio.sleep(3)
                await self.page.wait_for_load_state("networkidle")
                html_content = await self.page.content()

            print(f"✅ 成功获取页面HTML内容 (长度: {len(html_content)} 字符)")
            return html_content

        except Exception as e:
            print(f"❌ 获取页面内容失败: {e}")
            raise

    async def save_html_content(self) -> str:
        """
        获取页面HTML内容并保存到文件

        Returns:
            str: 保存的文件路径
        """
        try:
            print("💾 正在保存页面HTML内容...")

            # 获取页面HTML内容
            html_content = await self.get_page_content()

            # 保存HTML文件
            html_file_path = self.static_dir / "chat.html"

            with open(html_file_path, 'w', encoding='utf-8') as f:
                f.write(html_content)

            print(f"✅ HTML内容已保存到: {html_file_path}")
            return str(html_file_path)

        except Exception as e:
            print(f"❌ 保存HTML内容失败: {e}")
            raise

    def parse_html_with_beautifulsoup(self, html_file_path: str) -> BeautifulSoup:
        """
        使用BeautifulSoup解析HTML内容

        Args:
            html_file_path (str): HTML文件路径

        Returns:
            BeautifulSoup: 解析后的soup对象
        """
        try:
            print("🔍 正在使用BeautifulSoup解析HTML内容...")

            with open(html_file_path, 'r', encoding='utf-8') as f:
                html_content = f.read()

            # 创建BeautifulSoup对象
            chat_soup = BeautifulSoup(html_content, 'html.parser')

            print("✅ HTML解析完成")
            print(f"📊 解析统计:")
            print(
                f"   - 页面标题: {chat_soup.title.string if chat_soup.title else '未找到标题'}")
            print(f"   - 总元素数量: {len(chat_soup.find_all())}")
            print(f"   - div元素数量: {len(chat_soup.find_all('div'))}")
            print(f"   - script元素数量: {len(chat_soup.find_all('script'))}")

            return chat_soup

        except Exception as e:
            print(f"❌ HTML解析失败: {e}")
            raise

    def extract_messages(self, chat_soup: BeautifulSoup) -> List[Dict[str, str]]:
        """
        从BeautifulSoup对象中提取所有消息信息（包括已读和未读）
        
        注意：已读和未读状态仅用于记录目的，所有消息都支持相同的操作功能

        Args:
            chat_soup (BeautifulSoup): 解析后的HTML内容

        Returns:
            List[Dict[str, str]]: 所有消息列表，每个消息包含姓名、身份、公司、消息内容和状态标记
        """
        try:
            print("🔍 正在提取所有消息信息...")

            all_messages = []

            # 查找所有联系人项目
            contact_items = chat_soup.find_all('li', {'role': 'listitem'})

            for item in contact_items:
                # 检查是否有未读消息标识
                notice_badge = item.find('span', class_='notice-badge')
                
                # 判断消息状态
                is_unread = notice_badge is not None
                unread_count = notice_badge.get_text(strip=True) if notice_badge else "0"
                status = "未读" if is_unread else "已读"

                # 提取联系人信息
                name_text_elem = item.find('span', class_='name-text')
                name = name_text_elem.get_text(
                    strip=True) if name_text_elem else "未知姓名"

                # 提取公司和身份信息
                name_box = item.find('span', class_='name-box')
                company = "未知公司"
                position = "未知身份"

                if name_box:
                    # 获取name-box下的所有span元素
                    spans = name_box.find_all('span')
                    if len(spans) >= 2:
                        company = spans[1].get_text(strip=True)
                    if len(spans) >= 3:
                        position = spans[2].get_text(strip=True)

                # 提取最后一条消息内容
                last_msg_elem = item.find('span', class_='last-msg-text')
                message_content = last_msg_elem.get_text(
                    strip=True) if last_msg_elem else "无消息内容"

                # 提取时间信息
                time_elem = item.find('span', class_='time')
                message_time = time_elem.get_text(
                    strip=True) if time_elem else "未知时间"

                # 构建消息信息字典（保持原有数据结构，添加状态字段）
                message_info = {
                    'name': name,
                    'company': company,
                    'position': position,
                    'message_content': message_content,
                    'unread_count': unread_count,
                    'time': message_time,
                    'status': status,  # 新增状态字段
                    'is_unread': is_unread  # 新增布尔状态字段，便于程序判断
                }

                all_messages.append(message_info)

            # 统计消息数量
            unread_count = sum(1 for msg in all_messages if msg['is_unread'])
            read_count = len(all_messages) - unread_count
            
            print(f"✅ 成功提取到 {len(all_messages)} 条消息（未读: {unread_count}，已读: {read_count}）")
            return all_messages

        except Exception as e:
            print(f"❌ 提取消息失败: {e}")
            return []

    def print_messages(self, all_messages: List[Dict[str, str]]) -> None:
        """
        格式化打印所有消息信息（包括已读和未读）
        
        注意：显示消息的阅读状态，但所有消息都支持相同的操作功能

        Args:
            all_messages (List[Dict[str, str]]): 所有消息列表
        """
        if not all_messages:
            print("📭 没有找到任何消息")
            return

        # 统计消息数量
        unread_count = sum(1 for msg in all_messages if msg['is_unread'])
        read_count = len(all_messages) - unread_count

        print("\n" + "="*80)
        print(f"📬 消息汇总 (共 {len(all_messages)} 条 | 未读: {unread_count} | 已读: {read_count})")
        print("="*80)

        for i, msg in enumerate(all_messages, 1):
            # 根据状态选择不同的图标
            status_icon = "🔴" if msg['is_unread'] else "✅"
            print(f"\n【消息 {i}】{status_icon} {msg['status']}")
            print(f"👤 联系人姓名: {msg['name']}")
            print(f"🏢 所属公司: {msg['company']}")
            print(f"💼 身份信息: {msg['position']}")
            print(f"💬 消息内容: {msg['message_content']}")
            if msg['is_unread']:
                print(f"🔢 未读数量: {msg['unread_count']}")
            print(f"⏰ 消息时间: {msg['time']}")
            print("-" * 60)

        print("="*80)

    async def click_message(self, message_index: int) -> bool:
        """
        点击指定的消息，打开聊天页面
        
        注意：支持点击所有消息，无论其阅读状态如何

        Args:
            message_index: 消息索引（从0开始）

        Returns:
            bool: 是否成功点击
        """
        try:
            print(f"🖱️  正在点击第 {message_index + 1} 条消息...")

            # 等待联系人列表加载
            await self.page.wait_for_selector(".chat-user", timeout=10000)

            # 获取所有联系人（包括已读和未读）
            all_contacts = await self.page.query_selector_all(".friend-content")

            if not all_contacts or message_index >= len(all_contacts):
                print(f"❌ 未找到第 {message_index + 1} 条消息")
                return False

            # 点击指定的消息
            contact = all_contacts[message_index]
            await contact.click()

            # 等待聊天页面加载
            await self.page.wait_for_timeout(2000)
            print(f"✅ 成功点击第 {message_index + 1} 条消息")
            return True

        except Exception as e:
            print(f"❌ 点击未读消息失败: {e}")
            return False

    async def wait_for_navigation_with_fallback(self, timeout: int = 10000) -> Optional[str]:
        """
        等待页面导航，包含多种监听机制的回退方案
        
        Args:
            timeout: 超时时间（毫秒）
            
        Returns:
            Optional[str]: 新的页面URL，如果导航失败则返回None
        """
        current_url = self.page.url
        
        try:
            # 方案1: 使用wait_for_load_state等待页面加载状态变化
            print("🔄 等待页面加载状态变化...")
            await self.page.wait_for_load_state("domcontentloaded", timeout=timeout)
            
            # 检查URL是否发生变化
            new_url = self.page.url
            if new_url != current_url:
                print(f"✅ 检测到URL变化: {new_url}")
                return new_url
            
            # 如果URL没有变化，等待网络空闲状态
            await self.page.wait_for_load_state("networkidle", timeout=5000)
            final_url = self.page.url
            if final_url != current_url:
                print(f"✅ 网络空闲后检测到URL变化: {final_url}")
                return final_url
                
        except Exception as e:
            print(f"⚠️  页面加载状态监听异常: {e}")
        
        # 方案2: 轮询检查URL变化
        print("🔄 使用轮询方式检查URL变化...")
        start_time = time.time()
        while time.time() - start_time < timeout / 1000:
            await self.page.wait_for_timeout(100)  # 每100ms检查一次，提高响应速度
            current_check_url = self.page.url
            if current_check_url != current_url:
                print(f"✅ 轮询检测到URL变化: {current_check_url}")
                return current_check_url
        
        print("❌ 未检测到页面导航")
        return None

    async def extract_job_link_from_chat(self, max_retries: int = 3) -> Optional[str]:
        """
        通过模拟点击"查看职位"按钮来获取职位详情页URL
        
        Args:
            max_retries: 最大重试次数
            
        Returns:
            Optional[str]: 职位详情页URL，如果操作失败则返回None
        """
        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    print(f"🔄 第 {attempt + 1} 次尝试...")
                    await self.page.wait_for_timeout(2000)  # 重试前等待
                
                print("🔍 正在通过模拟点击获取职位详情...")

                # 等待聊天内容加载
                await self.page.wait_for_timeout(2000)

                # 记录当前页面URL
                current_url = self.page.url
                print(f"📍 当前页面: {current_url}")

                # 验证页面状态
                if not await self._validate_page_state():
                    print("⚠️  页面状态异常，跳过此次尝试")
                    continue

                # 检查iframe和跨域问题（仅在第一次尝试时执行）
                if attempt == 0:
                    iframe_check_result = await self._check_iframe_and_cross_origin_issues()
                    if iframe_check_result["cross_origin_detected"]:
                        print("⚠️  检测到跨域或iframe嵌套问题，这可能影响点击操作")
                    if iframe_check_result["security_errors"]:
                        print("⚠️  检测到安全策略限制，可能影响页面操作")
                        for error in iframe_check_result["security_errors"]:
                            print(f"   - {error}")

                # 首先等待聊天页面完全加载
                await self.page.wait_for_selector(".chat-conversation", timeout=10000)
                
                # 查找"查看职位"按钮的精确选择器（按优先级排序）
                view_job_selectors = [
                    # 最精确的选择器：直接定位包含"查看职位"文本的span元素
                    ".position-content .right-content span:has-text('查看职位')",
                    # 备选：通过父容器定位
                    ".chat-position-content .position-content .right-content span",
                    # 备选：通过埋点属性定位父容器，然后找右侧内容
                    "[ka='geek_chat_job_detail'] .right-content span",
                    # 备选：更宽泛的选择器
                    ".position-main .position-content .right-content span",
                    # 最后备选：整个职位区域（如果找不到具体按钮）
                    ".position-content",
                ]

                job_button = None
                used_selector = None

                # 尝试找到"查看职位"按钮元素
                for selector in view_job_selectors:
                    try:
                        print(f"🔍 尝试选择器: {selector}")
                        
                        # 等待元素出现
                        await self.page.wait_for_selector(selector, timeout=5000)
                        job_button = await self.page.query_selector(selector)
                        
                        if job_button:
                            # 检查元素是否可见和可点击
                            is_visible = await job_button.is_visible()
                            is_enabled = await job_button.is_enabled()
                            
                            # 如果是span元素，检查是否包含"查看职位"文本
                            if selector.endswith("span"):
                                text_content = await job_button.text_content()
                                if text_content and "查看职位" in text_content:
                                    if is_visible and is_enabled:
                                        used_selector = selector
                                        print(f"✅ 找到'查看职位'按钮: {selector}")
                                        print(f"📝 按钮文本: {text_content.strip()}")
                                        break
                                    else:
                                        print(f"⚠️  '查看职位'按钮不可点击: visible={is_visible}, enabled={is_enabled}")
                                else:
                                    print(f"⚠️  元素不包含'查看职位'文本: {text_content}")
                            else:
                                # 对于非span元素（如整个职位区域），直接检查可见性
                                if is_visible and is_enabled:
                                    used_selector = selector
                                    print(f"✅ 找到职位区域: {selector}")
                                    break
                                else:
                                    print(f"⚠️  职位区域不可点击: visible={is_visible}, enabled={is_enabled}")
                    except Exception as e:
                        print(f"⚠️  查找选择器异常 {selector}: {e}")
                        continue

                if not job_button:
                    print("⚠️  未找到'查看职位'按钮或职位信息区域")
                    if attempt < max_retries - 1:
                        continue
                    return None

                # 执行点击操作并监听页面导航
                try:
                    print("🖱️  模拟点击职位区域...")
                    
                    # 滚动到元素可见位置
                    await job_button.scroll_into_view_if_needed()
                    await self.page.wait_for_timeout(800)  # 增加等待时间，确保滚动完成
                    print("✅ 元素已滚动到视图中")
                    
                    # 获取当前页面URL作为基准
                    original_url = self.page.url
                    print(f"📍 当前页面URL: {original_url}")
                    
                    # 记录点击前的页面数量
                    initial_page_count = len(self.context.pages)
                    print(f"📊 点击前页面数量: {initial_page_count}")
                    
                    # 多种点击方式尝试
                    click_success = False
                    
                    # 方式1: 普通点击
                    try:
                        await job_button.click()
                        print("✅ 普通点击执行完成")
                        click_success = True
                    except Exception as click_error:
                        print(f"⚠️  普通点击失败: {click_error}")
                        
                        # 方式2: 强制点击
                        try:
                            await job_button.click(force=True)
                            print("✅ 强制点击执行完成")
                            click_success = True
                        except Exception as force_click_error:
                            print(f"⚠️  强制点击失败: {force_click_error}")
                            
                            # 方式3: JavaScript点击
                            try:
                                await job_button.evaluate("element => element.click()")
                                print("✅ JavaScript点击执行完成")
                                click_success = True
                            except Exception as js_click_error:
                                print(f"⚠️  JavaScript点击失败: {js_click_error}")
                    
                    if not click_success:
                        print("❌ 所有点击方式都失败")
                        if attempt < max_retries - 1:
                            continue
                        return None
                    
                    # 首先检测是否有新标签页打开
                    print("🔍 检测新标签页...")
                    new_tab = await self._detect_new_tab_opened(initial_page_count, timeout=8000)
                    
                    if new_tab:
                        print("✅ 检测到新标签页打开")
                        try:
                            # 切换到新标签页
                            await new_tab.bring_to_front()
                            print("🔄 已切换到新标签页")
                            
                            # 等待新标签页加载完成
                            if await self._wait_for_job_page_load(new_tab):
                                print("✅ 新标签页加载完成")
                                
                                # 获取新标签页的URL
                                job_url = new_tab.url
                                print(f"🎯 职位详情页URL: {job_url}")
                                
                                # 提取职位信息（可选）
                                job_info = await self._extract_job_info_from_page(new_tab)
                                if job_info.get("title"):
                                    print(f"📋 职位标题: {job_info['title']}")
                                
                                # 关闭新标签页并返回原页面
                                await new_tab.close()
                                print("🔙 已关闭新标签页，返回原聊天页面")
                                
                                # 确保回到原始页面
                                await self.page.bring_to_front()
                                
                                return job_url
                            else:
                                print("❌ 新标签页加载失败")
                                await new_tab.close()
                        except Exception as tab_error:
                            print(f"❌ 处理新标签页时出错: {tab_error}")
                            try:
                                await new_tab.close()
                            except:
                                pass
                    else:
                        # 如果没有新标签页，尝试原有的页面跳转检测
                        print("⏳ 未检测到新标签页，尝试检测当前页面跳转...")
                        new_url = await self.wait_for_navigation_with_fallback(timeout=8000)
                        
                        if new_url:
                            print(f"🎯 当前页面跳转到: {new_url}")
                            
                            # 验证是否跳转到职位详情页
                            if "/job_detail/" in new_url or "job" in new_url.lower():
                                print(f"✅ 成功跳转到职位详情页: {new_url}")
                                return new_url
                            else:
                                print(f"⚠️  跳转的页面可能不是职位详情页: {new_url}")
                                return new_url  # 仍然返回URL，让后续处理判断
                        else:
                            print("❌ 页面未发生跳转，也未检测到新标签页")
                        
                        # 检查是否有弹窗或其他阻挡元素
                        try:
                            # 检查是否有遮罩层
                            mask_elements = await self.page.query_selector_all(".mask, .modal, .popup, .overlay")
                            if mask_elements:
                                print(f"⚠️  检测到 {len(mask_elements)} 个可能的遮罩元素")
                            
                            # 检查是否有错误提示
                            error_elements = await self.page.query_selector_all(".error, .warning, .alert")
                            if error_elements:
                                for error_el in error_elements:
                                    error_text = await error_el.text_content()
                                    if error_text and error_text.strip():
                                        print(f"⚠️  页面错误信息: {error_text.strip()}")
                        except Exception as check_error:
                            print(f"⚠️  检查页面状态异常: {check_error}")
                        
                        if attempt < max_retries - 1:
                            continue
                        return None
                        
                except asyncio.TimeoutError as timeout_error:
                    await self._enhanced_error_logging(
                        "点击操作超时", 
                        timeout_error, 
                        {"尝试次数": f"{attempt + 1}/{max_retries}", "使用的选择器": used_selector}
                    )
                    if attempt < max_retries - 1:
                        continue
                    return None
                except Exception as click_error:
                    await self._enhanced_error_logging(
                        "点击操作异常", 
                        click_error, 
                        {"尝试次数": f"{attempt + 1}/{max_retries}", "使用的选择器": used_selector}
                    )
                    if attempt < max_retries - 1:
                        continue
                    return None

            except Exception as e:
                await self._enhanced_error_logging(
                    "模拟点击操作", 
                    e, 
                    {"尝试次数": f"{attempt + 1}/{max_retries}"}
                )
                if attempt < max_retries - 1:
                    continue
                return None
        
        print(f"❌ 经过 {max_retries} 次尝试后仍然失败")
        return None

    async def _validate_page_state(self) -> bool:
        """
        验证页面状态是否正常
        
        Returns:
            bool: 页面状态是否正常
        """
        try:
            # 检查页面是否已加载
            ready_state = await self.page.evaluate("document.readyState")
            if ready_state != "complete":
                print(f"⚠️  页面未完全加载: {ready_state}")
                return False
            
            # 检查是否在聊天页面
            current_url = self.page.url
            if "chat" not in current_url.lower() and "geek" not in current_url.lower():
                print(f"⚠️  当前不在聊天页面: {current_url}")
                return False
            
            return True
            
        except Exception as e:
            print(f"⚠️  页面状态验证异常: {e}")
            return False

    async def _detect_new_tab_opened(self, initial_page_count: int, timeout: int = 10000) -> Optional[Page]:
        """
        检测是否有新标签页打开，并返回新打开的页面对象
        
        Args:
            initial_page_count: 初始页面数量
            timeout: 超时时间（毫秒）
            
        Returns:
            Optional[Page]: 新打开的页面对象，如果没有检测到则返回None
        """
        try:
            print("🔍 正在检测新标签页...")
            start_time = time.time()
            
            while time.time() - start_time < timeout / 1000:
                # 获取当前所有页面
                current_pages = self.context.pages
                current_page_count = len(current_pages)
                
                if current_page_count > initial_page_count:
                    # 找到新打开的页面
                    new_page = current_pages[-1]  # 通常新页面在列表末尾
                    print(f"✅ 检测到新标签页: {new_page.url}")
                    return new_page
                
                await self.page.wait_for_timeout(200)  # 每200ms检查一次
            
            print("❌ 未检测到新标签页打开")
            return None
            
        except Exception as e:
            print(f"❌ 检测新标签页时发生错误: {e}")
            return None

    async def _wait_for_job_page_load(self, job_page: Page, timeout: int = 15000) -> bool:
        """
        等待职位详情页完全加载
        
        Args:
            job_page: 职位详情页面对象
            timeout: 超时时间（毫秒）
            
        Returns:
            bool: 是否成功加载
        """
        try:
            print("⏳ 等待职位详情页加载...")
            
            # 等待页面基本加载完成
            await job_page.wait_for_load_state("domcontentloaded", timeout=timeout)
            
            # 等待职位相关元素出现（多种可能的选择器）
            job_selectors = [
                ".job-detail",           # 职位详情容器
                ".job-primary",          # 职位主要信息
                ".job-sec",              # 职位次要信息
                ".job-banner",           # 职位横幅
                ".detail-content",       # 详情内容
                "[class*='job']",        # 包含job的类名
                ".company-info",         # 公司信息
                ".position-detail"       # 职位详情
            ]
            
            job_element_found = False
            for selector in job_selectors:
                try:
                    await job_page.wait_for_selector(selector, timeout=5000)
                    print(f"✅ 找到职位元素: {selector}")
                    job_element_found = True
                    break
                except:
                    continue
            
            if not job_element_found:
                print("⚠️  未找到明确的职位元素，但页面可能已加载")
            
            # 等待网络请求完成
            await job_page.wait_for_load_state("networkidle", timeout=5000)
            
            print("✅ 职位详情页加载完成")
            return True
            
        except Exception as e:
            print(f"❌ 等待职位详情页加载失败: {e}")
            return False

    async def _extract_job_info_from_page(self, job_page: Page) -> Dict[str, str]:
        """
        从职位详情页提取职位信息
        
        Args:
            job_page: 职位详情页面对象
            
        Returns:
            Dict[str, str]: 包含职位信息的字典
        """
        try:
            print("📄 正在提取职位详情信息...")
            
            job_info = {
                "url": job_page.url,
                "title": "",
                "company": "",
                "salary": "",
                "location": "",
                "experience": "",
                "education": "",
                "description": "",
                "html_content": ""
            }
            
            # 获取页面标题
            try:
                job_info["title"] = await job_page.title()
            except:
                pass
            
            # 获取完整的HTML内容
            try:
                job_info["html_content"] = await job_page.content()
            except:
                pass
            
            # 尝试提取具体的职位信息（根据Boss直聘的页面结构）
            try:
                # 职位名称
                job_title_elem = await job_page.query_selector(".job-name, .position-head h1, .job-title")
                if job_title_elem:
                    job_info["title"] = await job_title_elem.inner_text()
                
                # 公司名称
                company_elem = await job_page.query_selector(".company-name, .company-info h3, .company-title")
                if company_elem:
                    job_info["company"] = await company_elem.inner_text()
                
                # 薪资信息
                salary_elem = await job_page.query_selector(".salary, .job-salary, .position-salary")
                if salary_elem:
                    job_info["salary"] = await salary_elem.inner_text()
                
                # 工作地点
                location_elem = await job_page.query_selector(".job-area, .work-addr, .location")
                if location_elem:
                    job_info["location"] = await location_elem.inner_text()
                
                # 工作经验
                experience_elem = await job_page.query_selector(".job-limit .experience, .job-require .experience")
                if experience_elem:
                    job_info["experience"] = await experience_elem.inner_text()
                
                # 学历要求
                education_elem = await job_page.query_selector(".job-limit .education, .job-require .education")
                if education_elem:
                    job_info["education"] = await education_elem.inner_text()
                
                # 职位描述
                desc_elem = await job_page.query_selector(".job-detail-section, .job-sec .text, .detail-content")
                if desc_elem:
                    job_info["description"] = await desc_elem.inner_text()
                
            except Exception as e:
                print(f"⚠️  提取具体职位信息时发生错误: {e}")
            
            print(f"✅ 成功提取职位信息: {job_info['title']} - {job_info['company']}")
            return job_info
            
        except Exception as e:
            print(f"❌ 提取职位信息失败: {e}")
            return {"url": job_page.url, "error": str(e)}

    async def _check_iframe_and_cross_origin_issues(self) -> Dict[str, any]:
        """
        检查iframe嵌套和跨域问题
        
        Returns:
            Dict[str, any]: 检查结果，包含iframe信息和可能的跨域问题
        """
        result = {
            "has_iframes": False,
            "iframe_count": 0,
            "iframe_sources": [],
            "cross_origin_detected": False,
            "security_errors": []
        }
        
        try:
            # 检查页面中是否有iframe
            iframes = await self.page.query_selector_all("iframe")
            result["iframe_count"] = len(iframes)
            result["has_iframes"] = len(iframes) > 0
            
            if iframes:
                print(f"🔍 检测到 {len(iframes)} 个iframe元素")
                
                for i, iframe in enumerate(iframes):
                    try:
                        # 获取iframe的src属性
                        src = await iframe.get_attribute("src")
                        if src:
                            result["iframe_sources"].append(src)
                            print(f"📄 iframe {i+1} src: {src}")
                            
                            # 检查是否为跨域iframe
                            current_origin = await self.page.evaluate("window.location.origin")
                            if src.startswith("http") and not src.startswith(current_origin):
                                result["cross_origin_detected"] = True
                                print(f"⚠️  检测到跨域iframe: {src}")
                    except Exception as iframe_error:
                        error_msg = f"检查iframe {i+1}时出错: {iframe_error}"
                        result["security_errors"].append(error_msg)
                        print(f"⚠️  {error_msg}")
            
            # 检查是否在iframe内部
            try:
                is_in_iframe = await self.page.evaluate("window.self !== window.top")
                if is_in_iframe:
                    result["cross_origin_detected"] = True
                    print("⚠️  当前页面运行在iframe内部")
            except Exception as iframe_check_error:
                error_msg = f"检查iframe嵌套状态时出错: {iframe_check_error}"
                result["security_errors"].append(error_msg)
                print(f"⚠️  {error_msg}")
            
            # 检查可能的安全策略限制
            try:
                csp_header = await self.page.evaluate("""
                    () => {
                        const meta = document.querySelector('meta[http-equiv="Content-Security-Policy"]');
                        return meta ? meta.getAttribute('content') : null;
                    }
                """)
                if csp_header:
                    print(f"🔒 检测到CSP策略: {csp_header}")
                    if "frame-ancestors" in csp_header or "frame-src" in csp_header:
                        result["security_errors"].append("CSP策略可能限制iframe操作")
            except Exception as csp_error:
                print(f"⚠️  检查CSP策略时出错: {csp_error}")
            
        except Exception as e:
            error_msg = f"iframe和跨域检查异常: {e}"
            result["security_errors"].append(error_msg)
            print(f"⚠️  {error_msg}")
        
        return result

    async def _enhanced_error_logging(self, operation: str, error: Exception, context: Dict[str, any] = None) -> None:
        """
        增强的错误日志记录
        
        Args:
            operation: 操作名称
            error: 异常对象
            context: 额外的上下文信息
        """
        try:
            print(f"❌ {operation} 失败:")
            print(f"   错误类型: {type(error).__name__}")
            print(f"   错误信息: {str(error)}")
            
            if context:
                print("   上下文信息:")
                for key, value in context.items():
                    print(f"     {key}: {value}")
            
            # 获取当前页面状态
            try:
                current_url = self.page.url
                page_title = await self.page.title()
                ready_state = await self.page.evaluate("document.readyState")
                
                print("   页面状态:")
                print(f"     URL: {current_url}")
                print(f"     标题: {page_title}")
                print(f"     加载状态: {ready_state}")
                
                # 检查控制台错误
                console_errors = await self.page.evaluate("""
                    () => {
                        const errors = [];
                        const originalError = console.error;
                        console.error = function(...args) {
                            errors.push(args.join(' '));
                            originalError.apply(console, args);
                        };
                        return errors.slice(-5); // 返回最近5个错误
                    }
                """)
                
                if console_errors:
                    print("   控制台错误:")
                    for i, error_msg in enumerate(console_errors, 1):
                        print(f"     {i}. {error_msg}")
                        
            except Exception as log_error:
                print(f"   获取页面状态时出错: {log_error}")
                
        except Exception as logging_error:
            print(f"⚠️  错误日志记录失败: {logging_error}")

    async def _extract_full_job_description(self) -> str:
        """
        提取完整的职位描述，包括处理展开按钮和动态内容
        
        Returns:
            str: 完整的职位描述文本
        """
        try:
            print("🔍 正在提取完整职位描述...")
            
            # 等待页面内容加载
            await self.page.wait_for_timeout(1000)
            
            # 尝试多种职位描述选择器
            description_selectors = [
                ".job-sec-text",           # 主要的职位描述容器
                ".job-detail-section",     # 职位详情区域
                ".job-description",        # 职位描述
                ".detail-content",         # 详情内容
                ".job-content",            # 职位内容
                "[class*='job-sec']",      # 包含job-sec的类名
                "[class*='description']"   # 包含description的类名
            ]
            
            description_element = None
            used_selector = None
            
            # 查找职位描述元素
            for selector in description_selectors:
                try:
                    element = await self.page.query_selector(selector)
                    if element:
                        # 检查元素是否包含实际内容
                        text_content = await element.inner_text()
                        if text_content and len(text_content.strip()) > 10:
                            description_element = element
                            used_selector = selector
                            print(f"✅ 找到职位描述元素: {selector}")
                            break
                except:
                    continue
            
            if not description_element:
                print("❌ 未找到职位描述元素")
                return ""
            
            # 查找并点击"展开"按钮
            expand_buttons_selectors = [
                ".fold-text",              # 折叠文本按钮
                ".expand-btn",             # 展开按钮
                ".show-more",              # 显示更多
                ".unfold",                 # 展开
                "[class*='expand']",       # 包含expand的类名
                "[class*='fold']",         # 包含fold的类名
                "[class*='more']",         # 包含more的类名
                "button:has-text('展开')",  # 包含"展开"文本的按钮
                "span:has-text('展开')",    # 包含"展开"文本的span
                "a:has-text('展开')",       # 包含"展开"文本的链接
                "button:has-text('更多')",  # 包含"更多"文本的按钮
                "span:has-text('更多')",    # 包含"更多"文本的span
                ".text-expand",            # 文本展开
                ".btn-expand"              # 按钮展开
            ]
            
            expand_clicked = False
            for selector in expand_buttons_selectors:
                try:
                    # 在职位描述容器内查找展开按钮
                    expand_button = await description_element.query_selector(selector)
                    if not expand_button:
                        # 如果容器内没有，在整个页面查找
                        expand_button = await self.page.query_selector(selector)
                    
                    if expand_button:
                        # 检查按钮是否可见和可点击
                        is_visible = await expand_button.is_visible()
                        if is_visible:
                            print(f"🖱️  找到展开按钮，正在点击: {selector}")
                            await expand_button.click()
                            expand_clicked = True
                            
                            # 等待内容展开
                            await self.page.wait_for_timeout(1500)
                            print("✅ 展开按钮点击成功")
                            break
                except Exception as e:
                    # 忽略单个按钮的错误，继续尝试其他按钮
                    continue
            
            if not expand_clicked:
                print("ℹ️  未找到展开按钮或已经是展开状态")
            
            # 等待可能的动态内容加载
            await self.page.wait_for_timeout(1000)
            
            # 重新获取职位描述元素（因为点击展开后内容可能已更新）
            try:
                updated_element = await self.page.query_selector(used_selector)
                if updated_element:
                    description_element = updated_element
            except:
                pass
            
            # 提取完整文本内容
            full_description = await description_element.inner_text()
            
            # 清理文本内容
            full_description = full_description.strip()
            
            # 移除可能的多余空白字符
            import re
            full_description = re.sub(r'\n\s*\n', '\n\n', full_description)  # 规范化换行
            full_description = re.sub(r' +', ' ', full_description)  # 规范化空格
            
            print(f"✅ 成功提取完整职位描述 (长度: {len(full_description)} 字符)")
            
            # 如果描述仍然很短，尝试其他方法
            if len(full_description) < 50:
                print("⚠️  描述内容较短，尝试其他提取方法...")
                
                # 尝试获取所有文本内容
                try:
                    all_text_elements = await self.page.query_selector_all(".job-sec-text p, .job-sec-text div, .job-detail-section p, .job-detail-section div")
                    all_texts = []
                    for element in all_text_elements:
                        text = await element.inner_text()
                        if text and text.strip():
                            all_texts.append(text.strip())
                    
                    if all_texts:
                        full_description = '\n'.join(all_texts)
                        print(f"✅ 通过备用方法提取到描述 (长度: {len(full_description)} 字符)")
                except:
                    pass
            
            return full_description
            
        except Exception as e:
            print(f"❌ 提取完整职位描述失败: {e}")
            return ""

    async def scrape_job_details(self, job_url: str) -> Dict[str, str]:
        """
        访问岗位JD详情页并抓取详细信息

        Args:
            job_url: 岗位详情页URL

        Returns:
            Dict[str, str]: 包含岗位详细信息的字典
        """
        job_details = {
            "job_title": "",
            "salary": "",
            "location": "",
            "experience": "",
            "education": "",
            "tags": "",
            "description": "",
            "company_info": "",
            "work_address": "",
            "company_scale": "",
            "company_industry": ""
        }

        try:
            print(f"🌐 正在访问岗位详情页: {job_url}")

            # 访问岗位详情页
            await self.page.goto(job_url, wait_until="networkidle")
            await self.page.wait_for_load_state("domcontentloaded")
            await self.page.wait_for_timeout(3000)

            # 提取岗位名称
            try:
                job_title_element = await self.page.query_selector("h1, .name h1, .job-title")
                if job_title_element:
                    job_details["job_title"] = await job_title_element.inner_text()
            except:
                pass

            # 提取薪资
            try:
                salary_element = await self.page.query_selector(".salary, .name .salary")
                if salary_element:
                    job_details["salary"] = await salary_element.inner_text()
            except:
                pass

            # 提取工作地点、经验、学历
            try:
                info_elements = await self.page.query_selector_all(".text-desc")
                for element in info_elements:
                    text = await element.inner_text()
                    if "年" in text and ("经验" in text or "工作" in text):
                        job_details["experience"] = text
                    elif any(edu in text for edu in ["本科", "硕士", "博士", "大专", "高中"]):
                        job_details["education"] = text
                    elif not job_details["location"] and len(text) < 20:
                        job_details["location"] = text
            except:
                pass

            # 提取岗位标签
            try:
                tag_elements = await self.page.query_selector_all(".job-keyword-list li")
                tags = []
                for tag_element in tag_elements:
                    tag_text = await tag_element.inner_text()
                    tags.append(tag_text.strip())
                job_details["tags"] = ", ".join(tags)
            except:
                pass

            # 提取职位描述（完整版本）
            try:
                job_details["description"] = await self._extract_full_job_description()
            except Exception as e:
                print(f"⚠️  提取完整职位描述时出错: {e}")
                # 回退到简单提取方法
                try:
                    desc_element = await self.page.query_selector(".job-sec-text")
                    if desc_element:
                        job_details["description"] = await desc_element.inner_text()
                except:
                    pass

            # 提取公司工商信息
            try:
                company_info_elements = await self.page.query_selector_all(".level-list li")
                company_info = []
                for element in company_info_elements:
                    text = await element.inner_text()
                    company_info.append(text.strip())
                job_details["company_info"] = "; ".join(company_info)
            except:
                pass

            # 提取工作地址
            try:
                address_element = await self.page.query_selector(".location-address")
                if address_element:
                    job_details["work_address"] = await address_element.inner_text()
            except:
                pass

            print("✅ 岗位详情抓取完成")
            return job_details

        except Exception as e:
            print(f"❌ 抓取岗位详情失败: {e}")
            return job_details

    def print_job_details(self, job_details: Dict[str, str], message_info: Dict[str, str]) -> None:
        """
        格式化打印岗位详情信息

        Args:
            job_details: 岗位详情信息
            message_info: 对应的消息信息
        """
        print("\n" + "=" * 100)
        print("📋 岗位详情信息")
        print("=" * 100)
        
        print(f"\n【联系人信息】")
        print(f"👤 姓名: {message_info.get('name', '未知')}")
        print(f"🏢 公司: {message_info.get('company', '未知')}")
        print(f"💬 消息: {message_info.get('message_content', '未知')}")
        print(f"📊 状态: {message_info.get('status', '未知')}")
        
        print(f"\n【岗位基本信息】")
        print(f"💼 岗位名称: {job_details.get('job_title', '未知')}")
        print(f"💰 薪资范围: {job_details.get('salary', '未知')}")
        print(f"📍 工作地点: {job_details.get('location', '未知')}")
        print(f"🎓 工作经验: {job_details.get('experience', '未知')}")
        print(f"📚 学历要求: {job_details.get('education', '未知')}")
        print(f"🏷️  岗位标签: {job_details.get('tags', '未知')}")
        
        print(f"\n【职位描述】")
        description = job_details.get('description', '未知')
        print(f"{description}")
        print(f"📏 描述长度: {len(description)} 字符")
        
        print(f"\n【公司信息】")
        print(f"🏭 公司工商信息: {job_details.get('company_info', '未知')}")
        print(f"🏢 工作地址: {job_details.get('work_address', '未知')}")
        print(f"👥 公司规模: {job_details.get('company_scale', '未知')}")
        print(f"🏭 公司行业: {job_details.get('company_industry', '未知')}")
        
        print("=" * 100)

    async def process_single_message(self, all_messages: List[Dict[str, str]], message_index: int) -> None:
        """
        处理单条消息，提取岗位详情

        Args:
            all_messages: 所有消息列表
            message_index: 要处理的消息索引
        """
        try:
            message = all_messages[message_index]
            print(f"\n🔄 正在处理第 {message_index + 1} 条消息...")
            
            # 点击指定的消息
            if await self.click_message(message_index):
                # 提取职位链接
                job_url = await self.extract_job_link_from_chat()
                if job_url:
                    # 抓取岗位详情
                    job_details = await self.scrape_job_details(job_url)
                    # 打印岗位详情
                    self.print_job_details(job_details, message)
                else:
                    print("⚠️  未找到职位链接，可能该消息不包含岗位信息")
                    # 仍然显示基本消息信息
                    print(f"\n📝 消息基本信息:")
                    print(f"👤 姓名: {message.get('name', '未知')}")
                    print(f"🏢 公司: {message.get('company', '未知')}")
                    print(f"💬 消息: {message.get('message_content', '未知')}")
                    print(f"📊 状态: {message.get('status', '未知')}")
            else:
                print("❌ 点击消息失败")
                
        except Exception as e:
            print(f"❌ 处理消息时出错: {e}")

    async def process_all_messages(self, messages: List[Dict[str, str]]) -> None:
        """
        自动处理所有消息，提取岗位详情
        
        注意：无论消息的阅读状态如何，都会进行相同的处理操作

        Args:
            messages: 消息列表（包括已读和未读消息）
        """
        total_messages = len(messages)
        successful_extractions = 0
        failed_extractions = 0
        
        print(f"\n🎯 开始批量处理 {total_messages} 条消息...")
        print("=" * 80)
        
        for i, message in enumerate(messages):
            try:
                print(f"\n📍 处理进度: {i + 1}/{total_messages}")
                print(f"👤 当前处理: {message.get('name', '未知')} - {message.get('company', '未知')}")
                
                # 点击消息
                if await self.click_message(i):
                    # 提取职位链接
                    job_url = await self.extract_job_link_from_chat()
                    if job_url:
                        # 抓取岗位详情
                        job_details = await self.scrape_job_details(job_url)
                        # 打印岗位详情
                        self.print_job_details(job_details, message)
                        successful_extractions += 1
                    else:
                        print("⚠️  未找到职位链接，可能该消息不包含岗位信息")
                        failed_extractions += 1
                        # 仍然显示基本消息信息
                        print(f"\n📝 消息基本信息:")
                        print(f"👤 姓名: {message.get('name', '未知')}")
                        print(f"🏢 公司: {message.get('company', '未知')}")
                        print(f"💬 消息: {message.get('content', '未知')}")
                else:
                    print("❌ 点击消息失败")
                    failed_extractions += 1
                
                # 返回到消息列表页面，准备处理下一条消息
                if i < total_messages - 1:  # 不是最后一条消息
                    print("🔙 返回消息列表...")
                    await self.page.go_back()
                    await self.page.wait_for_timeout(2000)
                    
            except Exception as e:
                print(f"❌ 处理第 {i + 1} 条消息时出错: {e}")
                failed_extractions += 1
                continue
        
        # 打印处理结果统计
        print("\n" + "=" * 80)
        print("📊 批量处理结果统计")
        print("=" * 80)
        print(f"✅ 成功提取岗位详情: {successful_extractions} 条")
        print(f"❌ 提取失败或无岗位信息: {failed_extractions} 条")
        print(f"📈 成功率: {(successful_extractions / total_messages * 100):.1f}%")
        print("=" * 80)

    async def cleanup(self) -> None:
        """
        清理资源，关闭浏览器
        """
        try:
            if self.browser:
                await self.browser.close()
                print("✅ 浏览器已关闭")
        except Exception as e:
            print(f"⚠️  清理资源时发生错误: {e}")

    async def run(self) -> BeautifulSoup:
        """
        执行完整的爬虫流程

        Returns:
            BeautifulSoup: 解析后的HTML内容
        """
        chat_soup = None

        try:
            print("🎯 开始执行Boss直聘消息页面爬虫...")
            print("-" * 60)

            # 1. 启动浏览器
            await self.start_browser()

            # 2. 导航到首页
            await self.navigate_to_boss_homepage()

            # 3. 等待用户手动登录
            self.wait_for_user_login()

            # 4. 跳转到消息页面
            await self.navigate_to_chat_page()

            # 5. 获取并保存HTML内容
            html_file_path = await self.save_html_content()

            # 6. 解析HTML内容
            chat_soup = self.parse_html_with_beautifulsoup(html_file_path)

            # 7. 提取并打印所有消息信息
            all_messages = self.extract_messages(chat_soup)
            self.print_messages(all_messages)

            # 8. 提供消息处理选择：自动处理所有消息或手动选择特定消息
            if all_messages:
                print(f"\n🤔 发现 {len(all_messages)} 条消息，请选择处理方式：")
                print("   1. 自动处理所有消息（推荐）")
                print("   2. 手动选择特定消息")
                print("   3. 跳过岗位详情查看")
                
                try:
                    user_input = input("请输入选择（1/2/3）: ").strip()
                    
                    if user_input == "1":
                        # 自动处理所有消息
                        print(f"\n🚀 开始自动处理 {len(all_messages)} 条消息...")
                        await self.process_all_messages(all_messages)
                        
                    elif user_input == "2":
                        # 手动选择特定消息
                        print(f"\n📋 请选择要查看的消息编号:")
                        # 显示所有消息的编号映射
                        for i, msg in enumerate(all_messages, 1):
                            status_icon = "🔴" if msg['is_unread'] else "✅"
                            print(f"   {i}. {status_icon} {msg['name']} ({msg['company']}) - {msg['status']}")
                        
                        message_input = input(f"请输入编号（1-{len(all_messages)}）: ").strip()
                        if message_input.isdigit():
                            selected_index = int(message_input) - 1
                            if 0 <= selected_index < len(all_messages):
                                await self.process_single_message(all_messages, selected_index)
                            else:
                                print("❌ 输入的编号超出范围")
                        else:
                            print("❌ 请输入有效的数字")
                            
                    else:
                        print("⏭️  跳过岗位详情查看")
                        
                except Exception as e:
                    print(f"⚠️  处理用户输入时出错: {e}")
            else:
                print("\n✅ 没有找到任何消息需要处理")

            print("-" * 60)
            print("🎉 爬虫执行完成！")

            return chat_soup

        except KeyboardInterrupt:
            print("\n❌ 用户中断执行")
            return None
        except Exception as e:
            print(f"❌ 爬虫执行失败: {e}")
            return None
        finally:
            # 清理资源
            await self.cleanup()


async def main():
    """
    主函数
    """
    spider = BossCaptureSpider()

    try:
        # 执行爬虫
        chat_soup = await spider.run()

        if chat_soup:
            print("\n🎯 爬虫执行成功！")
            print("   ✅ HTML内容已保存到 static/chat.html")
            print("   ✅ 未读消息信息已自动提取并显示")
            print("   💡 可以使用chat_soup对象进行进一步处理")
        else:
            print("\n❌ 爬虫执行失败，未能获取到有效的HTML内容")

    except Exception as e:
        print(f"❌ 程序执行出错: {e}")


if __name__ == "__main__":
    # 运行主程序
    asyncio.run(main())

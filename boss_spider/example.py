"""
Boss直聘登录脚本使用示例
"""

import asyncio
from login import BossLoginManager


async def demo_basic_usage():
    """
    基础使用示例
    """
    print("🚀 启动 Boss直聘登录示例...")

    # 创建登录管理器
    login_manager = BossLoginManager()

    # 启动浏览器会话
    result = await login_manager.start_browser_session(headless=False)

    if result:
        browser, context, page = result

        print("✅ 登录成功！现在可以进行其他操作...")

        # 示例：访问职位搜索页面
        await page.goto("https://www.zhipin.com/web/geek/job")
        await page.wait_for_load_state('networkidle')

        print("📋 已跳转到职位搜索页面")

        # 保持浏览器打开30秒用于演示
        print("⏳ 浏览器将在30秒后自动关闭...")
        await asyncio.sleep(30)

        # 关闭浏览器
        await browser.close()
        print("👋 浏览器已关闭")

    else:
        print("❌ 登录失败")


async def demo_persistent_login():
    """
    持久化登录示例
    """
    print("🔄 演示持久化登录功能...")

    login_manager = BossLoginManager()

    # 第一次运行 - 需要手动登录
    print("\n--- 第一次运行（需要手动登录）---")
    result1 = await login_manager.start_browser_session()

    if result1:
        browser1, context1, page1 = result1
        print("✅ 第一次登录成功，登录状态已保存")
        await browser1.close()

        # 等待几秒
        await asyncio.sleep(3)

        # 第二次运行 - 应该自动登录
        print("\n--- 第二次运行（应该自动登录）---")
        result2 = await login_manager.start_browser_session()

        if result2:
            browser2, context2, page2 = result2
            print("🎉 第二次自动登录成功！")

            # 保持打开一段时间
            await asyncio.sleep(10)
            await browser2.close()
        else:
            print("❌ 第二次登录失败")
    else:
        print("❌ 第一次登录失败")


async def main():
    """
    主函数 - 选择运行哪个示例
    """
    print("Boss直聘登录脚本示例")
    print("=" * 40)
    print("1. 基础使用示例")
    print("2. 持久化登录示例")

    choice = input("\n请选择要运行的示例 (1 或 2): ").strip()

    if choice == "1":
        await demo_basic_usage()
    elif choice == "2":
        await demo_persistent_login()
    else:
        print("❌ 无效选择")

if __name__ == "__main__":
    asyncio.run(main())

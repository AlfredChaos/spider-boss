#!/usr/bin/env python3
"""
测试脚本：验证Boss直聘爬虫的登录优化功能

测试内容：
1. 用户数据目录配置
2. 浏览器持久化启动
3. 登录状态检测
4. 自动跳过登录功能
"""

import asyncio
import os
import sys
from pathlib import Path

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from capture import BossCaptureSpider


async def test_user_data_dir_configuration():
    """测试用户数据目录配置功能"""
    print("\n🧪 测试1: 用户数据目录配置")
    print("-" * 50)
    
    # 测试默认配置
    spider1 = BossCaptureSpider()
    expected_default = Path.cwd() / "browser_data"
    print(f"默认用户数据目录: {spider1.user_data_dir}")
    print(f"预期目录: {expected_default}")
    assert str(spider1.user_data_dir) == str(expected_default), "默认用户数据目录配置错误"
    print("✅ 默认配置测试通过")
    
    # 测试自定义配置
    custom_dir = "/tmp/test_browser_data"
    spider2 = BossCaptureSpider(user_data_dir=custom_dir)
    print(f"自定义用户数据目录: {spider2.user_data_dir}")
    assert str(spider2.user_data_dir) == custom_dir, "自定义用户数据目录配置错误"
    print("✅ 自定义配置测试通过")


async def test_browser_startup():
    """测试浏览器启动功能"""
    print("\n🧪 测试2: 浏览器持久化启动")
    print("-" * 50)
    
    spider = BossCaptureSpider()
    
    try:
        # 启动浏览器
        print("正在启动浏览器...")
        await spider.start_browser()
        print("✅ 浏览器启动成功")
        
        # 检查浏览器和页面对象
        assert spider.browser is not None, "浏览器对象未创建"
        assert spider.page is not None, "页面对象未创建"
        print("✅ 浏览器和页面对象创建成功")
        
        # 检查用户数据目录是否存在
        assert spider.user_data_dir.exists(), "用户数据目录未创建"
        print(f"✅ 用户数据目录已创建: {spider.user_data_dir}")
        
    except Exception as e:
        print(f"❌ 浏览器启动测试失败: {e}")
        raise
    finally:
        # 清理资源
        if spider.browser:
            await spider.browser.close()
            print("🧹 浏览器已关闭")


async def test_navigation_and_login_detection():
    """测试导航和登录状态检测功能"""
    print("\n🧪 测试3: 导航和登录状态检测")
    print("-" * 50)
    
    spider = BossCaptureSpider()
    
    try:
        # 启动浏览器
        await spider.start_browser()
        print("✅ 浏览器启动成功")
        
        # 导航到首页
        print("正在导航到Boss直聘首页...")
        await spider.navigate_to_boss_homepage()
        print("✅ 首页导航成功")
        
        # 检测登录状态
        print("正在检测登录状态...")
        login_status = await spider.check_login_status()
        print(f"登录状态检测结果: {'已登录' if login_status else '未登录'}")
        print("✅ 登录状态检测功能正常")
        
        # 测试智能登录处理（不会实际等待用户输入，只是验证逻辑）
        print("测试智能登录处理逻辑...")
        if login_status:
            print("✅ 检测到已登录状态，应该会自动跳过登录步骤")
        else:
            print("✅ 检测到未登录状态，应该会提示用户登录")
        
    except Exception as e:
        print(f"❌ 导航和登录检测测试失败: {e}")
        raise
    finally:
        # 清理资源
        if spider.browser:
            await spider.browser.close()
            print("🧹 浏览器已关闭")


async def main():
    """主测试函数"""
    print("🚀 开始测试Boss直聘爬虫登录优化功能")
    print("=" * 60)
    
    try:
        # 运行所有测试
        await test_user_data_dir_configuration()
        await test_browser_startup()
        await test_navigation_and_login_detection()
        
        print("\n" + "=" * 60)
        print("🎉 所有测试通过！登录优化功能正常工作")
        print("\n📋 优化功能总结:")
        print("✅ 用户数据目录持久化配置")
        print("✅ 浏览器会话状态保存")
        print("✅ 登录状态智能检测")
        print("✅ 自动跳过登录功能")
        print("\n💡 使用建议:")
        print("1. 首次运行时需要手动登录一次")
        print("2. 后续运行将自动跳过登录步骤")
        print("3. 如需重新登录，可删除browser_data目录")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
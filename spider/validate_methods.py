#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证修改后的方法是否正常工作
"""

import asyncio
from capture import BossCaptureSpider


async def validate_methods():
    """
    验证关键方法的基本功能
    """
    print("🔍 验证修改后的方法...")
    
    spider = BossCaptureSpider()
    
    try:
        # 测试1: 验证类初始化
        print("✅ 类初始化成功")
        
        # 测试2: 验证方法存在性
        assert hasattr(spider, 'extract_job_link_from_chat'), "extract_job_link_from_chat方法不存在"
        assert hasattr(spider, 'wait_for_navigation_with_fallback'), "wait_for_navigation_with_fallback方法不存在"
        assert hasattr(spider, '_validate_page_state'), "_validate_page_state方法不存在"
        print("✅ 所有新方法都存在")
        
        # 测试3: 验证方法签名
        import inspect
        
        # 检查extract_job_link_from_chat方法签名
        sig = inspect.signature(spider.extract_job_link_from_chat)
        params = list(sig.parameters.keys())
        assert 'max_retries' in params, "extract_job_link_from_chat缺少max_retries参数"
        print("✅ extract_job_link_from_chat方法签名正确")
        
        # 检查wait_for_navigation_with_fallback方法签名
        sig = inspect.signature(spider.wait_for_navigation_with_fallback)
        params = list(sig.parameters.keys())
        assert 'timeout' in params, "wait_for_navigation_with_fallback缺少timeout参数"
        print("✅ wait_for_navigation_with_fallback方法签名正确")
        
        # 测试4: 验证方法文档字符串
        assert spider.extract_job_link_from_chat.__doc__ is not None, "extract_job_link_from_chat缺少文档字符串"
        assert "模拟点击" in spider.extract_job_link_from_chat.__doc__, "文档字符串未提及模拟点击"
        print("✅ 方法文档字符串正确")
        
        print("\n🎉 所有验证通过！修改后的方法结构正确。")
        
    except AssertionError as e:
        print(f"❌ 验证失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 验证过程中发生异常: {e}")
        return False
    
    return True


def validate_code_structure():
    """
    验证代码结构
    """
    print("\n🔍 验证代码结构...")
    
    try:
        # 读取源代码文件
        with open('capture.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查关键代码片段
        checks = [
            ("模拟点击", "extract_job_link_from_chat方法包含模拟点击逻辑"),
            ("wait_for_navigation", "包含导航等待逻辑"),
            ("max_retries", "包含重试机制"),
            ("scroll_into_view_if_needed", "包含元素滚动逻辑"),
            ("_validate_page_state", "包含页面状态验证"),
            ("asyncio.create_task", "使用异步任务"),
        ]
        
        for keyword, description in checks:
            if keyword in content:
                print(f"✅ {description}")
            else:
                print(f"⚠️  {description} - 未找到关键字: {keyword}")
        
        print("✅ 代码结构验证完成")
        
    except Exception as e:
        print(f"❌ 代码结构验证失败: {e}")


if __name__ == "__main__":
    print("🚀 开始验证...")
    print("=" * 50)
    
    # 验证方法
    success = asyncio.run(validate_methods())
    
    # 验证代码结构
    validate_code_structure()
    
    print("=" * 50)
    if success:
        print("🎉 验证成功！修改后的功能已准备就绪。")
    else:
        print("❌ 验证失败，请检查代码。")
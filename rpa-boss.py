import rpa as r
import time
import os
import subprocess

# --- 可配置参数 ---
CHAT_URL = "https://www.zhipin.com/web/geek/chat"  # BOSS直聘聊天页面URL
DEFAULT_REPLY = "您好，我已收到您的消息，会尽快给您回复。"  # 默认回复内容
WAIT_TIME_SECONDS = 30  # 每次轮询的间隔时间（秒）

# --- 环境预检 ---

def check_php_available():
    """检查本机是否安装可用的 PHP（TagUI 需要 PHP 来解析脚本）。"""
    try:
        subprocess.run(["php", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except Exception:
        print("检测到 PHP 未安装或不可用。请在 macOS 上使用 Homebrew 安装：\n  brew install php")
        print("安装后将 PHP 加入 PATH（Apple Silicon）：")
        print("  echo 'export PATH=\"/opt/homebrew/opt/php/bin:$PATH\"' >> ~/.zshrc && source ~/.zshrc")
        print("若为 Intel 芯片路径可能为：/usr/local/opt/php/bin，按需替换上面命令中的路径")
        return False


def check_chrome_installed():
    """检查是否安装了 Google Chrome（TagUI 默认使用 Chrome 进行网页自动化）。"""
    chrome_app_path = "/Applications/Google Chrome.app"
    if os.path.isdir(chrome_app_path):
        return True
    print("未检测到 Google Chrome。请先安装 Chrome： https://www.google.com/chrome/")
    return False


def main():
    """
    BOSS直聘自动回复机器人的主函数。
    该函数会初始化RPA环境，引导用户手动登录，
    然后进入一个无限循环来监控和回复新消息。
    """
    try:
        # 环境预检（避免“无法打开浏览器”的根因）
        if not check_php_available():
            return
        if not check_chrome_installed():
            return

        # 1. 初始化RPA环境（强制使用 Chrome，非无头模式）
        r.error(True)  # 出错时抛异常，便于排查
        r.init(visual_automation=False, chrome_browser=True, headless_mode=False, turbo_mode=False)
        print("请在浏览器中手动登录BOSS直聘...")
        print("登录成功并跳转到主聊天页面后，请在本窗口按回车键继续...")
        input()

        # 2. 导航到消息页面
        r.url(CHAT_URL)
        r.wait(5)  # 等待页面加载

        # 3. 开始监控新消息
        while True:
            print("正在检查新消息...")

            # 4. 查找并处理未读消息
            # 注意：'//div[contains(@class, "unread-dot")]' 是一个示例选择器，
            # 您需要根据实际页面结构进行替换。
            if r.present('//div[contains(@class, "unread-dot")]'):
                print("发现新消息，正在处理...")
                r.click('//div[contains(@class, "unread-dot")]')
                r.wait(3)  # 等待进入聊天窗口

                # 5. 输入并发送回复
                # 注意：'//textarea' 是一个示例选择器，
                # 您需要根据实际页面结构进行替换。
                r.type('//textarea', DEFAULT_REPLY + '[enter]')
                print("已自动回复一条新消息。")

                # 6. 返回消息列表
                r.url(CHAT_URL)
                r.wait(5)  # 等待页面加载
            else:
                print("暂无新消息。")

            # 等待下一轮检查
            print(f"将在 {WAIT_TIME_SECONDS} 秒后进行下一次检查...")
            time.sleep(WAIT_TIME_SECONDS)

    except Exception as e:
        print(f"脚本运行期间发生错误: {e}")
        # 若 TagUI 启动异常，可参考本地日志 /Users/alfredchaos/home/code/boss-capture/rpa_python.log
        print("若仍无法打开浏览器，请检查 rpa_python.log 并确认已安装 PHP 和 Chrome。")
    finally:
        # 7. 确保浏览器在脚本结束时关闭
        print("正在关闭浏览器...")
        try:
            r.close()
        except Exception:
            pass

if __name__ == "__main__":
    main()
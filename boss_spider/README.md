# Boss直聘自动登录脚本

这是一个基于 Playwright 的 Boss直聘自动登录脚本，支持持久化登录状态，一次登录后可在后续使用中自动恢复登录状态。

## 功能特性

- ✅ **持久化登录**: 首次手动登录后，自动保存登录状态
- ✅ **自动恢复**: 后续运行时自动加载保存的登录状态
- ✅ **状态检测**: 智能检测当前登录状态
- ✅ **反检测**: 内置反自动化检测机制
- ✅ **错误处理**: 完善的异常处理和重试机制
- ✅ **配置灵活**: 支持多种配置选项

## 安装依赖

```bash
# 安装 Playwright
pip install playwright

# 安装浏览器驱动
playwright install chromium
```

## 使用方法

### 1. 基础使用

```bash
# 运行登录脚本
python login.py
```

### 2. 在代码中使用

```python
from login import BossLoginManager
import asyncio

async def example():
    # 创建登录管理器
    login_manager = BossLoginManager()
    
    # 启动浏览器会话
    result = await login_manager.start_browser_session()
    
    if result:
        browser, context, page = result
        
        # 在这里添加您的业务逻辑
        # 例如：搜索职位、发送消息等
        
        # 完成后关闭浏览器
        await browser.close()

# 运行示例
asyncio.run(example())
```

## 文件说明

- `login.py` - 主要的登录脚本
- `config.py` - 配置文件
- `boss_auth.json` - 自动生成的认证状态文件（首次登录后创建）
- `browser_data/` - 浏览器用户数据目录（自动创建）

## 工作流程

1. **首次运行**:
   - 启动 Chrome 浏览器
   - 跳转到 Boss直聘登录页面
   - 等待用户手动完成登录
   - 保存登录状态到 `boss_auth.json`

2. **后续运行**:
   - 检查 `boss_auth.json` 是否存在且有效
   - 加载保存的登录状态
   - 启动浏览器并自动恢复登录状态
   - 如果状态无效，则重新引导手动登录

## 配置选项

可以通过修改 `config.py` 来调整各种配置：

- `BROWSER_CONFIG`: 浏览器相关配置
- `LOGIN_CONFIG`: 登录相关配置
- `ANTI_DETECTION`: 反检测配置

## 注意事项

1. **首次使用**: 需要手动登录一次，脚本会自动保存登录状态
2. **状态过期**: 登录状态默认7天过期，过期后需要重新登录
3. **网络环境**: 确保网络连接稳定
4. **浏览器版本**: 建议使用最新版本的 Chrome 浏览器

## 故障排除

### 常见问题

1. **登录状态检测失败**
   - 检查网络连接
   - 清除 `boss_auth.json` 文件重新登录

2. **浏览器启动失败**
   - 确认已安装 Playwright 浏览器驱动
   - 检查系统权限

3. **反检测被触发**
   - 适当增加操作间隔
   - 更新 User-Agent 配置

## 开发说明

### 扩展功能

可以基于 `BossLoginManager` 类扩展更多功能：

```python
class ExtendedBossManager(BossLoginManager):
    async def search_jobs(self, keyword):
        """搜索职位"""
        # 实现职位搜索逻辑
        pass
    
    async def send_message(self, recruiter_id, message):
        """发送消息给招聘者"""
        # 实现消息发送逻辑
        pass
```

### API 参考

详细的 API 文档请参考代码中的函数注释。

## 许可证

本项目仅供学习和研究使用，请遵守 Boss直聘的使用条款。
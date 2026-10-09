# 能力与运行条件

使用标准能力，不依赖专用 liyu 服务。宿主需支持 backend-api-v1 和 host-api-v1；macOS 官方 desktop-v0.1.0-rc.2 已验证签名测试安装、启动与宿主登录审阅入口。

| 能力 | 用途 | 不可用时 |
| --- | --- | --- |
| auth | 宿主登录、凭据保管、声明的后端操作 | 显示错误；可主动进入本地演示 |
| runtime | 发现可选日历接口 | 使用 .ics |
| device_calendar | 原生权限、目标日历选择、约定事件创建与更新、回读 | 拒绝不写入，保留 .ics |
| storage | 各账号偏好与日历关联；无登录令牌文件 | 无法保存偏好或关联 |
| net | 后端网页及 HTTPS 允许列表 | 显示联网失败 |
| images | 后端与包内商品图片 | 保留商品文字 |
| model | 目录内推荐、购买注意事项、可见猜礼线索和日期整理 | 手动操作不受影响 |

后端 OAuth 与操作地址只使用同一 HTTPS 443 来源。使用 scripts/configure-backend.py 同步修改服务地址、四个 OAuth 地址与允许列表，再执行 octo check。日历方法在 host_api.optional 声明，支持与授权须分别检查。

card-host 不提供 auth 或设备日历；仅用于本地演示、源码和布局检查。真实后端写入和日历写入须由用户在原生宿主确认，自动化测试不绕过物理确认。各平台的上游限制、迁移说明与数据范围见[凭据说明](docs/authentication.md)和[隐私政策](PRIVACY.md)。

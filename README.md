# 域名监控工具

监控指定域名清单，一旦发现可注册的域名立即发送邮件通知。

## 功能特点

- ✅ 监控自定义域名清单
- ✅ 支持多种顶级域名 (.xyz, .com, .net, .org 等)
- ✅ 发现可注册域名时自动发送邮件
- ✅ 支持本地运行和 GitHub Actions 定时运行

## 文件说明

| 文件 | 说明 |
|------|------|
| `watchlist.txt` | 域名监控清单，每行一个域名 |
| `monitor_domains.py` | 监控脚本 |
| `check_domains.py` | 批量查询脚本（生成符合条件的域名清单） |

## 使用方法

### 1. 编辑域名清单

编辑 `watchlist.txt`，添加你要监控的域名：

```
# 以 # 开头的是注释
333319.xyz
example.com
mydomain.io
```

### 2. 本地运行

```bash
# 设置邮件配置（可选）
export SMTP_SERVER="smtp.gmail.com"
export SMTP_PORT="587"
export SMTP_USER="your-email@gmail.com"
export SMTP_PASSWORD="your-app-password"
export NOTIFY_EMAIL="notify@example.com"

# 运行监控
python3 monitor_domains.py
```

### 3. GitHub Actions 自动运行

1. 将代码推送到 GitHub 仓库
2. 在仓库设置中添加 Secrets：
   - `SMTP_SERVER`: SMTP 服务器地址
   - `SMTP_PORT`: SMTP 端口
   - `SMTP_USER`: 发件邮箱
   - `SMTP_PASSWORD`: 邮箱密码/应用专用密码
   - `NOTIFY_EMAIL`: 收件邮箱
3. 脚本会每 6 小时自动运行一次

## 邮箱配置示例

### Gmail

```
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=xxxx xxxx xxxx xxxx  # 应用专用密码
```

> ⚠️ Gmail 需要先启用两步验证，然后生成[应用专用密码](https://myaccount.google.com/apppasswords)

### QQ 邮箱

```
SMTP_SERVER=smtp.qq.com
SMTP_PORT=587
SMTP_USER=your-email@qq.com
SMTP_PASSWORD=授权码  # 在QQ邮箱设置中生成
```

### 163 邮箱

```
SMTP_SERVER=smtp.163.com
SMTP_PORT=25
SMTP_USER=your-email@163.com
SMTP_PASSWORD=授权码  # 在163邮箱设置中生成
```

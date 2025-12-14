#!/usr/bin/env python3
"""
域名监控脚本
监控指定清单中的域名，一旦发现可注册立即发送邮件通知
支持本地运行或 GitHub Actions 定时运行
"""

import subprocess
import smtplib
import os
import sys
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Optional


# ============== 配置区域 ==============
# 邮件配置 (可通过环境变量覆盖)
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")  # 发件邮箱
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")  # 邮箱密码/应用专用密码
NOTIFY_EMAIL = os.getenv("NOTIFY_EMAIL", "")  # 收件邮箱

# 域名清单文件
WATCHLIST_FILE = os.getenv("WATCHLIST_FILE", "watchlist.txt")
# =====================================


def get_whois_server(domain: str) -> str:
    """根据域名后缀返回对应的 whois 服务器"""
    tld = domain.split(".")[-1].lower()
    servers = {
        "xyz": "whois.nic.xyz",
        "com": "whois.verisign-grs.com",
        "net": "whois.verisign-grs.com",
        "org": "whois.pir.org",
        "io": "whois.nic.io",
        "co": "whois.nic.co",
        "me": "whois.nic.me",
        "info": "whois.afilias.net",
        "top": "whois.nic.top",
        "cn": "whois.cnnic.cn",
    }
    return servers.get(tld, f"whois.nic.{tld}")


def check_domain_whois(domain: str) -> tuple[bool, str]:
    """
    查询域名是否可注册
    
    返回: (是否可注册, 详细信息)
    """
    whois_server = get_whois_server(domain)
    
    try:
        result = subprocess.run(
            ["whois", "-h", whois_server, domain],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        output = result.stdout.lower()
        
        # 未注册的标识
        not_found_keywords = [
            "domain not found",
            "no match",
            "not found",
            "no data found",
            "no entries found",
            "status: free",
            "status: available",
            "object does not exist",
        ]
        
        for keyword in not_found_keywords:
            if keyword in output:
                return (True, "域名可注册")
        
        # 已注册的标识
        if "domain name:" in output or "registrar:" in output:
            return (False, "域名已注册")
        
        return (False, "无法确定状态")
        
    except subprocess.TimeoutExpired:
        return (False, "查询超时")
    except Exception as e:
        return (False, f"查询出错: {str(e)}")


def send_email(available_domains: list[str]) -> bool:
    """发送邮件通知"""
    if not all([SMTP_USER, SMTP_PASSWORD, NOTIFY_EMAIL]):
        print("⚠️ 邮件配置不完整，跳过发送邮件")
        print("请设置环境变量: SMTP_USER, SMTP_PASSWORD, NOTIFY_EMAIL")
        return False
    
    try:
        # 构建邮件内容
        subject = f"🎉 域名可注册提醒 - 发现 {len(available_domains)} 个可注册域名！"
        
        body = f"""
<html>
<body style="font-family: Arial, sans-serif; padding: 20px;">
<h2 style="color: #28a745;">🎉 发现可注册的域名！</h2>
<p>以下域名当前可以注册：</p>
<ul style="font-size: 18px;">
"""
        for domain in available_domains:
            body += f'<li style="margin: 10px 0;"><strong>{domain}</strong></li>\n'
        
        body += f"""
</ul>
<p style="color: #666;">请尽快抢注！</p>
<hr>
<p style="font-size: 12px; color: #999;">
检测时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}<br>
此邮件由域名监控脚本自动发送
</p>
</body>
</html>
"""
        
        # 创建邮件
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = SMTP_USER
        msg["To"] = NOTIFY_EMAIL
        msg.attach(MIMEText(body, "html", "utf-8"))
        
        # 发送邮件
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
        
        print(f"✅ 邮件已发送到 {NOTIFY_EMAIL}")
        return True
        
    except Exception as e:
        print(f"❌ 发送邮件失败: {str(e)}")
        return False


def load_watchlist(filepath: str) -> list[str]:
    """从文件加载域名清单"""
    domains = []
    try:
        with open(filepath, "r") as f:
            for line in f:
                line = line.strip()
                # 跳过空行和注释
                if line and not line.startswith("#"):
                    domains.append(line.lower())
    except FileNotFoundError:
        print(f"❌ 找不到清单文件: {filepath}")
        sys.exit(1)
    
    return domains


def main():
    """主函数"""
    print("=" * 60)
    print("域名监控脚本")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 加载域名清单
    domains = load_watchlist(WATCHLIST_FILE)
    
    if not domains:
        print("⚠️ 清单为空，没有需要监控的域名")
        return
    
    print(f"\n监控 {len(domains)} 个域名:")
    for d in domains:
        print(f"  - {d}")
    print("-" * 60)
    
    available_domains = []
    
    for domain in domains:
        print(f"正在查询: {domain} ... ", end="", flush=True)
        
        is_available, info = check_domain_whois(domain)
        
        if is_available:
            print(f"✅ {info}")
            available_domains.append(domain)
        else:
            print(f"❌ {info}")
    
    print("-" * 60)
    
    # 如果有可注册的域名，发送邮件通知
    if available_domains:
        print(f"\n🎉 发现 {len(available_domains)} 个可注册域名!")
        for d in available_domains:
            print(f"  ✅ {d}")
        
        # 发送邮件
        send_email(available_domains)
        
        # 保存到文件
        with open("available_domains.txt", "w") as f:
            f.write(f"# 检测时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            for d in available_domains:
                f.write(f"{d}\n")
        
        # 设置 GitHub Actions 输出
        if os.getenv("GITHUB_OUTPUT"):
            with open(os.environ["GITHUB_OUTPUT"], "a") as f:
                f.write(f"available=true\n")
                f.write(f"count={len(available_domains)}\n")
    else:
        print("\n没有发现可注册的域名")
        if os.getenv("GITHUB_OUTPUT"):
            with open(os.environ["GITHUB_OUTPUT"], "a") as f:
                f.write("available=false\n")


if __name__ == "__main__":
    main()

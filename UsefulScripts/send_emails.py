import smtplib
import csv
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from datetime import datetime

def load_customer_data(csv_file):
    """从 CSV 文件读取客户信息"""
    customers = []
    try:
        with open(csv_file, newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                customers.append(row)
        return customers
    except FileNotFoundError:
        print(f"错误：找不到文件 {csv_file}")
        return []
    except Exception as e:
        print(f"读取 CSV 文件时出错：{e}")
        return []

def create_email_content(customer, template_file):
    """创建个性化邮件内容"""
    try:
        with open(template_file, 'r', encoding='utf-8') as file:
            template = file.read()
        # 替换模板中的占位符
        template = template.replace('{Name}', customer['Name'])
        template = template.replace('{Company}', customer['Company'])
        template = template.replace('{Date}', datetime.now().strftime('%Y-%m-%d'))
        return template
    except FileNotFoundError:
        print(f"错误：找不到模板文件 {template_file}")
        return None
    except Exception as e:
        print(f"处理模板文件时出错：{e}")
        return None

def send_email(sender_email, app_password, customer, subject, html_content, attachment_path=None):
    """发送邮件"""
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = customer['Email']
    msg['Subject'] = subject

    # 添加 HTML 内容
    msg.attach(MIMEText(html_content, 'html'))

    # 添加附件（如果有）
    if attachment_path and os.path.exists(attachment_path):
        try:
            with open(attachment_path, 'rb') as file:
                part = MIMEApplication(file.read(), Name=os.path.basename(attachment_path))
                part['Content-Disposition'] = f'attachment; filename="{os.path.basename(attachment_path)}"'
                msg.attach(part)
        except Exception as e:
            print(f"添加附件 {attachment_path} 时出错：{e}")

    # 连接到 SMTP 服务器
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, app_password)
            server.send_message(msg)
            print(f"成功发送邮件到 {customer['Email']}")
    except smtplib.SMTPAuthenticationError:
        print("认证失败，请检查邮箱和应用专用密码")
    except Exception as e:
        print(f"发送邮件到 {customer['Email']} 时出错：{e}")

def main():
    # 配置信息
    sender_email = os.getenv('GMAIL_ADDRESS')  # 从环境变量获取邮箱
    app_password = os.getenv('GMAIL_APP_PASSWORD')  # 从环境变量获取应用专用密码
    csv_file = 'customers.csv'  # 客户信息 CSV 文件
    template_file = 'email_template.html'  # HTML 邮件模板文件
    attachment_path = 'energy_storage_brochure.pdf'  # 附件文件（可选）
    subject = 'Energy Storage Solutions for Your Business'

    # 验证环境变量
    if not sender_email or not app_password:
        print("错误：请设置环境变量 GMAIL_ADDRESS 和 GMAIL_APP_PASSWORD")
        print("运行以下命令设置环境变量：")
        print("export GMAIL_ADDRESS='your_email@gmail.com'")
        print("export GMAIL_APP_PASSWORD='your_app_password'")
        return

    # 加载客户数据
    customers = load_customer_data(csv_file)
    if not customers:
        print("没有客户数据可处理")
        return

    # 发送邮件
    for customer in customers:
        html_content = create_email_content(customer, template_file)
        if html_content:
            send_email(sender_email, app_password, customer, subject, html_content, attachment_path)

if __name__ == "__main__":
    main()
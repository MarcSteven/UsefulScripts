#!/usr/bin/env python3
import os
import json
import subprocess
import argparse
import logging
from pathlib import Path

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_config(config_path):
    """加载配置文件"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        logger.error(f"配置文件 {config_path} 不存在")
        exit(1)
    except json.JSONDecodeError:
        logger.error(f"配置文件 {config_path} 格式错误")
        exit(1)

def get_wechat_devtool_cli():
    """获取微信开发者工具 CLI 路径"""
    # 微信开发者工具默认安装路径 (Mac)
    default_cli_path = "/Applications/wechatwebdevtools.app/Contents/MacOS/cli"
    cli_path = os.getenv("WECHAT_DEVTOOL_CLI", default_cli_path)
    
    if not os.path.exists(cli_path):
        logger.error(f"微信开发者工具 CLI 未找到: {cli_path}")
        exit(1)
    return cli_path

def build_mini_program(project_path, output_path, version, desc):
    """执行小程序构建"""
    cli_path = get_wechat_devtool_cli()
    project_path = Path(project_path).resolve()
    output_path = Path(output_path).resolve()

    # 确保项目路径存在
    if not project_path.exists():
        logger.error(f"项目路径 {project_path} 不存在")
        exit(1)

    # 创建输出目录
    output_path.mkdir(parents=True, exist_ok=True)

    # 构建命令
    cmd = [
        cli_path,
        "build",
        "--project", str(project_path),
        "--build-output", str(output_path),
        "--build-version", version,
        "--build-desc", desc
    ]

    logger.info(f"执行构建命令: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        logger.info("构建成功！")
        logger.debug(result.stdout)
    except subprocess.CalledProcessError as e:
        logger.error(f"构建失败: {e.stderr}")
        exit(1)

def main():
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="微信小程序自动化打包脚本")
    parser.add_argument("--config", default="config.json", help="配置文件路径")
    args = parser.parse_args()

    # 加载配置文件
    config = load_config(args.config)

    # 从配置文件获取参数
    project_path = config.get("project_path")
    output_path = config.get("output_path", "dist")
    version = config.get("version", "1.0.0")
    desc = config.get("desc", "Automated build")

    if not project_path:
        logger.error("配置文件中缺少 project_path 参数")
        exit(1)

    # 执行构建
    build_mini_program(project_path, output_path, version, desc)

if __name__ == "__main__":
    main()
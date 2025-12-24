#!/usr/bin/env python3
"""安装依赖"""
import subprocess
import sys


def install_requirements():
    """安装 requirements.txt 中的依赖"""
    requirements = [
        "grpcio>=1.60.0",
        "grpcio-tools>=1.60.0",
        "protobuf>=4.25.3"
    ]

    print("安装 gRPC 依赖...")

    for package in requirements:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✓ 已安装 {package}")
        except subprocess.CalledProcessError:
            print(f"✗ 安装 {package} 失败")
            return False

    return True


if __name__ == "__main__":
    install_requirements()
import socket
from typing import List
import logging

logger = logging.getLogger("IPUtils")


def get_local_ipv4_addresses() -> List[str]:
    """
    简化版：获取本机IPv4地址
    """
    ipv4_addresses = []

    try:
        # 方法1: 通过外部连接获取IP（最可靠）
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            if local_ip != '127.0.0.1':
                ipv4_addresses.append(local_ip)
    except:
        pass

    try:
        # 方法2: 获取主机名对应的IP
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        if local_ip != '127.0.0.1' and local_ip not in ipv4_addresses:
            ipv4_addresses.append(local_ip)
    except:
        pass

    return ipv4_addresses


def log_network_info(port: int):
    """
    输出网络信息到日志
    """
    logger.info("=== 服务器网络信息 ===")

    hostname = socket.gethostname()
    logger.info(f"主机名: {hostname}")

    ipv4_addresses = get_local_ipv4_addresses()

    if not ipv4_addresses:
        logger.warning("无法获取本机IPv4地址")
    else:
        logger.info("本机IPv4地址列表:")
        for ip in ipv4_addresses:
            if ip.startswith('192.168.'):
                ip_type = "局域网IP (192.168.x.x)"
            elif ip.startswith('10.'):
                ip_type = "局域网IP (10.x.x.x)"
            elif ip.startswith('172.16.') or (ip.startswith('172.') and
                                              16 <= int(ip.split('.')[1]) <= 31):
                ip_type = "局域网IP (172.16.x.x-172.31.x.x)"
            else:
                ip_type = "公网IP"
            logger.info(f"  - {ip} ({ip_type})")

        # 显示访问地址
        logger.info("可访问地址:")
        for ip in ipv4_addresses:
            logger.info(f"  - ws://{ip}:{port}")

    logger.info(f"本地回环地址: ws://127.0.0.1:{port}")
    logger.info("===")
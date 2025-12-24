#!/usr/bin/env python3
"""gRPC 聊天服务器 - 显示本机IP和端口"""
import grpc
import logging
import socket
from concurrent import futures
import time
import os
import sys  # 添加这行

# 导入生成的代码
from generated import chat_pb2
from generated import chat_pb2_grpc


class ChatService(chat_pb2_grpc.ChatServiceServicer):
    """ChatService 实现类"""

    def SendMessage(self, request, context):
        """处理客户端发送的消息"""
        user_id = request.user_id
        message = request.message

        # 获取客户端连接信息
        client_info = ""
        try:
            # 获取客户端地址
            peer = context.peer()
            client_info = f"来自 {peer}"
        except:
            client_info = "客户端地址未知"

        logging.info(f"收到{client_info}的消息 - 用户ID: {user_id}, 消息: '{message}'")

        # 构建响应
        if message:
            reply = f"服务器已收到你的消息: '{message}' (用户ID: {user_id})"
            success = True
            code = 200
        else:
            reply = "错误: 消息内容为空"
            success = False
            code = 400

        return chat_pb2.Response(
            reply=reply,
            success=success,
            code=code
        )


def get_local_ip():
    """获取本机IP地址"""
    ip_addresses = []

    try:
        # 方法1: 通过socket获取所有IP
        hostname = socket.gethostname()

        # 获取主机名对应的所有IP
        try:
            all_ips = socket.gethostbyname_ex(hostname)[2]
            ip_addresses.extend(all_ips)
        except:
            pass

        # 方法2: 通过创建临时socket获取
        try:
            # 连接到外部服务器但不发送数据
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.settimeout(0.1)
            # 连接到公共DNS服务器
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            if local_ip not in ip_addresses and local_ip != "127.0.0.1":
                ip_addresses.append(local_ip)
        except:
            pass

        # 方法3: 获取网络接口信息（可选）
        try:
            import netifaces
            for interface in netifaces.interfaces():
                addrs = netifaces.ifaddresses(interface)
                if netifaces.AF_INET in addrs:
                    for addr in addrs[netifaces.AF_INET]:
                        ip = addr['addr']
                        if ip not in ip_addresses and ip != "127.0.0.1":
                            ip_addresses.append(ip)
        except ImportError:
            # netifaces 模块不可用，跳过
            pass

    except Exception as e:
        logging.warning(f"获取IP地址时出错: {e}")

    # 如果没有找到非回环地址，使用localhost
    if not ip_addresses:
        ip_addresses.append("127.0.0.1")

    # 过滤掉本地回环地址和重复项
    unique_ips = []
    for ip in ip_addresses:
        if ip not in unique_ips and not ip.startswith("127."):
            unique_ips.append(ip)

    # 如果没有网络IP，至少保留一个本地地址
    if not unique_ips:
        unique_ips.append("127.0.0.1")

    return unique_ips


def display_server_info(port):
    """显示服务器信息"""
    print("\n" + "=" * 60)
    print("gRPC 聊天服务器信息")
    print("=" * 60)

    # 获取本机IP地址
    ip_addresses = get_local_ip()

    # 显示监听端口
    print(f"监听端口: {port}")
    print("")

    # 显示可访问地址
    print("可以通过以下地址访问:")
    print(f"1. 本机访问:  127.0.0.1:{port}")

    if ip_addresses:
        for i, ip in enumerate(ip_addresses, 2):
            print(f"{i}. 网络访问:  {ip}:{port}")

    # 显示客户端连接命令
    print("\n客户端连接命令示例:")
    print(f"python client.py")
    for ip in ip_addresses:
        if ip != "127.0.0.1":
            print(f"python client.py --host {ip}")

    print("\n快速测试命令:")
    print("python client.py --test")

    # 显示进程信息
    print(f"\n进程ID: {os.getpid()}")
    print(f"Python版本: {sys.version.split()[0]}")
    print("=" * 60 + "\n")


def serve():
    """启动 gRPC 服务器"""
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # 监听端口
    port = 50051

    # 显示服务器信息
    display_server_info(port)

    # 创建服务器
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    # 注册服务
    chat_pb2_grpc.add_ChatServiceServicer_to_server(ChatService(), server)

    # 监听端口
    server.add_insecure_port(f'[::]:{port}')

    # 启动服务器
    server.start()
    logging.info(f"gRPC 服务器已启动，正在监听端口 {port}")
    logging.info("按 Ctrl+C 停止服务器")

    try:
        # 保持服务器运行
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n" + "=" * 60)
        logging.info("正在关闭服务器...")
        server.stop(0)
        logging.info("服务器已安全关闭")
        print("=" * 60)


if __name__ == '__main__':
    serve()
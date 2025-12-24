#!/usr/bin/env python3
"""gRPC 聊天客户端 - 支持指定服务器地址"""
import grpc
import logging
import sys
import argparse

# 导入生成的代码
from generated import chat_pb2
from generated import chat_pb2_grpc


def send_message(stub, message, user_id=1001):
    """发送消息到服务器"""
    try:
        # 创建请求
        request = chat_pb2.Request(
            message=message,
            user_id=user_id
        )

        # 调用 gRPC 方法
        response = stub.SendMessage(request)

        # 处理响应
        if response.success:
            print(f"✓ 成功: {response.reply}")
            print(f"  状态码: {response.code}")
        else:
            print(f"✗ 失败: {response.reply}")
            print(f"  状态码: {response.code}")

        return response.success

    except grpc.RpcError as e:
        print(f"✗ RPC 错误: {e.code()} - {e.details()}")
        return False


def test_connection(host, port):
    """测试连接"""
    server_address = f'{host}:{port}'

    print(f"尝试连接到服务器: {server_address}")

    channel = grpc.insecure_channel(server_address)

    try:
        # 设置超时
        grpc.channel_ready_future(channel).result(timeout=3)
        return channel, True
    except grpc.FutureTimeoutError:
        print(f"✗ 无法连接到服务器 {server_address}")
        print("请确保:")
        print(f"1. 服务器正在运行 (python server.py)")
        print(f"2. 地址正确: {host}")
        print(f"3. 端口正确: {port}")
        print("4. 防火墙已允许该端口")
        return None, False


def run_interactive_mode(host, port):
    """交互式模式"""
    # 测试连接
    channel, connected = test_connection(host, port)
    if not connected:
        return

    stub = chat_pb2_grpc.ChatServiceStub(channel)
    print("✓ 连接成功!")
    print("\n输入 'quit' 或 'exit' 退出程序")
    print("输入 'help' 查看帮助\n")

    # 交互式消息发送
    while True:
        try:
            # 获取用户输入
            message = input("请输入消息: ").strip()

            if message.lower() in ['quit', 'exit', 'q']:
                print("正在退出...")
                break

            if message.lower() in ['help', 'h', '?']:
                print("\n可用命令:")
                print("  help      - 显示此帮助")
                print("  quit/exit - 退出程序")
                print("  test      - 发送测试消息")
                print("  info      - 显示连接信息")
                print("")
                continue

            if message.lower() == 'info':
                print(f"\n当前连接信息:")
                print(f"  服务器: {host}:{port}")
                print("")
                continue

            if message.lower() == 'test':
                message = "这是测试消息"
                user_id = 9999
                print(f"发送测试消息: '{message}'")
            else:
                user_id = 1001

            if not message:
                print("消息不能为空，请重新输入")
                continue

            # 发送消息
            send_message(stub, message, user_id)

        except KeyboardInterrupt:
            print("\n正在退出...")
            break
        except Exception as e:
            print(f"发生错误: {e}")


def run_test_mode(host, port):
    """测试模式"""
    channel, connected = test_connection(host, port)
    if not connected:
        return

    stub = chat_pb2_grpc.ChatServiceStub(channel)

    print("\n" + "=" * 60)
    print("开始测试 gRPC 通信")
    print("=" * 60)

    # 测试多个消息
    test_cases = [
        ("你好，服务器!", 1001, True),
        ("今天天气不错", 1002, True),
        ("", 1003, False),  # 空消息，应该会失败
        ("这是一个长消息测试，看看服务器如何响应", 1004, True),
        ("!@#$%^&*()特殊字符测试", 1005, True),
        ("Hello from Python gRPC client!", 1006, True),
    ]

    for i, (message, user_id, should_succeed) in enumerate(test_cases, 1):
        print(f"\n测试 {i}/{len(test_cases)}")
        print(f"消息: '{message}'")
        print(f"用户ID: {user_id}")

        success = send_message(stub, message, user_id)

        if success == should_succeed:
            print("✓ 测试通过")
        else:
            print("✗ 测试失败")

    print("\n" + "=" * 60)
    print("测试完成!")
    print("=" * 60)


def main():
    """主函数"""
    # 配置日志
    logging.basicConfig(level=logging.WARNING)

    # 解析命令行参数
    parser = argparse.ArgumentParser(description='gRPC 聊天客户端')
    parser.add_argument('--host', default='localhost',
                        help='服务器主机地址 (默认: localhost)')
    parser.add_argument('--port', type=int, default=50051,
                        help='服务器端口 (默认: 50051)')
    parser.add_argument('--test', action='store_true',
                        help='运行测试模式')

    args = parser.parse_args()

    print("\n" + "=" * 60)
    print("gRPC 聊天客户端")
    print("=" * 60)

    if args.test:
        run_test_mode(args.host, args.port)
    else:
        run_interactive_mode(args.host, args.port)


if __name__ == '__main__':
    main()
import asyncio
import websockets
import json
import time
from datetime import datetime


class WebSocketClient:
    def __init__(self, uri="ws://192.168.101.102:3100"):
        self.uri = uri
        self.websocket = None
        self.is_connected = False

    async def connect(self):
        """连接到WebSocket服务器"""
        try:
            self.websocket = await websockets.connect(self.uri)
            self.is_connected = True
            print(f"成功连接到服务器 {self.uri}")
            return True
        except Exception as e:
            print(f"连接失败: {e}")
            return False

    async def send_message(self, message_type, **kwargs):
        """发送消息到服务器"""
        if not self.is_connected or not self.websocket:
            print("未连接到服务器")
            return None

        message = {
            "type": message_type,
            "timestamp": datetime.now().isoformat(),
            **kwargs
        }

        try:
            await self.websocket.send(json.dumps(message, ensure_ascii=False))
            print(f"发送消息: {message}")
            return True
        except Exception as e:
            print(f"发送消息失败: {e}")
            return False

    async def receive_messages(self):
        """接收服务器消息"""
        try:
            async for message in self.websocket:
                data = json.loads(message)
                print(f"收到服务器消息: {json.dumps(data, indent=2, ensure_ascii=False)}")
        except websockets.exceptions.ConnectionClosed:
            print("连接已关闭")
            self.is_connected = False
        except Exception as e:
            print(f"接收消息错误: {e}")

    async def test_echo(self, message="Hello, WebSocket!"):
        """测试回声功能"""
        await self.send_message("echo", message=message)

    async def test_broadcast(self, message="这是广播消息"):
        """测试广播功能"""
        await self.send_message("broadcast", message=message)

    async def test_ping(self):
        """测试心跳检测"""
        await self.send_message("ping")

    async def close(self):
        """关闭连接"""
        if self.websocket:
            await self.websocket.close()
            self.is_connected = False
            print("连接已关闭")


async def run_test_client():
    """运行测试客户端"""
    client = WebSocketClient()

    # 连接服务器
    if not await client.connect():
        return

    # 启动消息接收任务
    receive_task = asyncio.create_task(client.receive_messages())

    try:
        # 执行各种测试
        print("\n=== 测试回声功能 ===")
        await client.test_echo("第一次回声测试")
        await asyncio.sleep(1)

        print("\n=== 测试广播功能 ===")
        await client.test_broadcast("大家好，这是广播测试!")
        await asyncio.sleep(1)

        print("\n=== 测试心跳检测 ===")
        await client.test_ping()
        await asyncio.sleep(1)

        print("\n=== 测试未知消息类型 ===")
        await client.send_message("unknown_type", data="测试数据")
        await asyncio.sleep(1)

        # 保持连接运行一段时间
        print("\n=== 测试完成，等待额外消息... ===")
        await asyncio.sleep(3)

    except KeyboardInterrupt:
        print("用户中断测试")
    finally:
        # 清理
        receive_task.cancel()
        await client.close()


async def run_simple_client():
    """运行简单客户端（长时间运行）"""
    client = WebSocketClient()

    if await client.connect():
        # 启动消息接收
        receive_task = asyncio.create_task(client.receive_messages())

        try:
            # 定期发送消息
            counter = 0
            while client.is_connected:
                await client.test_echo(f"自动消息 #{counter}")
                counter += 1
                await asyncio.sleep(5)  # 每5秒发送一次
        except KeyboardInterrupt:
            print("客户端停止")
        finally:
            receive_task.cancel()
            await client.close()


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "simple":
        asyncio.run(run_simple_client())
    else:
        asyncio.run(run_test_client())
import asyncio
import websockets
import json
from datetime import datetime
import logging
import socket
from typing import List, Dict
import random

# 设置日志格式，包含具体时间（精确到毫秒）
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s.%(msecs)03d - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("WebSocketServer")


def get_local_ipv4_addresses() -> List[str]:
    """
    获取本机IPv4地址
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


def choose_best_ip() -> str:
    """
    自动选择最佳IP地址
    """
    ips = get_local_ipv4_addresses()

    if not ips:
        return '0.0.0.0'  # 监听所有接口

    # 优先选择局域网IP
    for ip in ips:
        if ip.startswith('192.168.') or ip.startswith('10.') or \
                (ip.startswith('172.') and 16 <= int(ip.split('.')[1]) <= 31):
            return ip

    # 如果没有局域网IP，返回第一个IP
    return ips[0]


class WebSocketServer:
    def __init__(self, host=None, port=3100):
        # 如果未指定host，自动选择最佳IP
        self.host = host if host else choose_best_ip()
        self.port = port
        self.connected_clients = set()
        # 存储每个客户端的播放状态
        self.playback_status: Dict[int, Dict] = {}  # client_id -> {actionGroupID: status_data}

    async def send_ack(self, websocket, original_message, status="processed"):
        """发送ack确认消息"""
        ack_msg = {
            "type": "ack",
            "data": {
                "status": status,
                "message": f"接收到的消息 '{original_message}' 处理成功"
            },
            "timestamp": int(datetime.now().timestamp() * 1000)
        }
        await websocket.send(json.dumps(ack_msg, ensure_ascii=False))

    async def simulate_playback(self, websocket, client_id, action_group_id):
        """模拟播放进度"""
        # 设置播放状态
        if client_id not in self.playback_status:
            self.playback_status[client_id] = {}

        self.playback_status[client_id][action_group_id] = {
            'playing': True,
            'current_progress': 0.0,
            'websocket': websocket
        }

        logger.info(f"开始为客户端 {client_id} 模拟播放，actionGroupID: {action_group_id}")

        # 发送播放进度消息（5-10次随机进度更新）
        progress_steps = random.randint(5, 10)
        for i in range(progress_steps):
            # 检查是否还在播放状态
            if (client_id not in self.playback_status or
                    action_group_id not in self.playback_status[client_id] or
                    not self.playback_status[client_id][action_group_id]['playing']):
                logger.info(f"播放被停止，actionGroupID: {action_group_id}")
                return

            progress_value = min(100.0, float((i + 1) * 100.0 / progress_steps))

            # 更新进度
            self.playback_status[client_id][action_group_id]['current_progress'] = progress_value

            # 发送播放进度消息
            progress_msg = {
                "type": "progress",
                "data": {
                    "value": progress_value,  # 改为浮点数
                    "message": "播放中",
                    "actionGroupID": action_group_id
                },
                "timestamp": int(datetime.now().timestamp() * 1000)
            }

            try:
                await websocket.send(json.dumps(progress_msg, ensure_ascii=False))
                logger.info(f"向客户端 {client_id} 发送播放进度: {progress_value:.2f}%, actionGroupID: {action_group_id}")
            except:
                logger.error(f"向客户端 {client_id} 发送消息失败")
                break

            # 随机延迟0.5-2秒
            await asyncio.sleep(random.uniform(0.5, 2.0))

        # 检查是否还在播放状态（可能被actionStop中断）
        if (client_id in self.playback_status and
                action_group_id in self.playback_status[client_id] and
                self.playback_status[client_id][action_group_id]['playing']):

            # 发送播放结束消息
            end_msg = {
                "type": "actionEnd",
                "data": {
                    "value": 100.0,  # 改为浮点数
                    "message": "播放完成",
                    "actionGroupID": action_group_id
                },
                "timestamp": int(datetime.now().timestamp() * 1000)
            }

            try:
                await websocket.send(json.dumps(end_msg, ensure_ascii=False))
                logger.info(f"向客户端 {client_id} 发送播放结束通知，actionGroupID: {action_group_id}")
            except:
                logger.error(f"向客户端 {client_id} 发送结束消息失败")

            # 清理播放状态
            if client_id in self.playback_status and action_group_id in self.playback_status[client_id]:
                del self.playback_status[client_id][action_group_id]

    async def handle_client(self, websocket):
        """处理客户端连接"""
        client_id = id(websocket)
        self.connected_clients.add(websocket)
        # 初始化客户端的播放状态
        self.playback_status[client_id] = {}
        logger.info(f"客户端 {client_id} 已连接，当前连接数: {len(self.connected_clients)}")

        try:
            # 发送欢迎消息
            welcome_msg = {
                "type": "welcome",
                "data": {
                    "status": "connected",
                    "message": f"Hello {client_id}, welcome to WebSocket Server!"
                },
                "timestamp": int(datetime.now().timestamp() * 1000)
            }
            await websocket.send(json.dumps(welcome_msg, ensure_ascii=False))

            # 处理客户端消息
            async for message in websocket:
                await self.process_message(websocket, message, client_id)

        except websockets.exceptions.ConnectionClosed:
            logger.info(f"客户端 {client_id} 断开连接")
        except Exception as e:
            logger.error(f"处理客户端 {client_id} 时发生错误: {e}")
        finally:
            # 清理客户端状态
            if client_id in self.playback_status:
                del self.playback_status[client_id]
            if websocket in self.connected_clients:
                self.connected_clients.remove(websocket)
            logger.info(f"客户端 {client_id} 已移除，当前连接数: {len(self.connected_clients)}")

    async def process_message(self, websocket, message, client_id):
        """处理接收到的消息"""
        try:
            data = json.loads(message)
            logger.info(f"收到来自客户端 {client_id} 的消息: {data}")

            # 首先发送ack确认消息
            original_message = data.get('message', str(data))
            await self.send_ack(websocket, original_message)

            # 根据消息类型处理
            msg_type = data.get('type', 'unknown')
            action_group_id = data.get('actionGroupID')

            if msg_type == 'actionStart':
                # 开始播放
                if not action_group_id:
                    error_msg = {
                        "type": "error",
                        "data": {
                            "message": "缺少actionGroupID参数",
                            "actionGroupID": None
                        },
                        "timestamp": int(datetime.now().timestamp() * 1000)
                    }
                    await websocket.send(json.dumps(error_msg, ensure_ascii=False))
                    return

                # 如果该actionGroupID已经在播放，先停止之前的
                if (client_id in self.playback_status and
                        action_group_id in self.playback_status[client_id]):
                    self.playback_status[client_id][action_group_id]['playing'] = False

                # 在后台任务中开始播放模拟
                asyncio.create_task(self.simulate_playback(websocket, client_id, action_group_id))

                # 发送开始确认
                start_ack = {
                    "type": "actionStartAck",
                    "data": {
                        "status": "started",
                        "message": "播放已开始",
                        "actionGroupID": action_group_id
                    },
                    "timestamp": int(datetime.now().timestamp() * 1000)
                }
                await websocket.send(json.dumps(start_ack, ensure_ascii=False))

            elif msg_type == 'actionStop':
                # 停止播放
                if not action_group_id:
                    error_msg = {
                        "type": "error",
                        "data": {
                            "message": "缺少actionGroupID参数",
                            "actionGroupID": None
                        },
                        "timestamp": int(datetime.now().timestamp() * 1000)
                    }
                    await websocket.send(json.dumps(error_msg, ensure_ascii=False))
                    return

                # 停止播放
                if (client_id in self.playback_status and
                        action_group_id in self.playback_status[client_id]):
                    self.playback_status[client_id][action_group_id]['playing'] = False

                    # 发送停止确认
                    stop_ack = {
                        "type": "actionStopAck",
                        "data": {
                            "status": "stopped",
                            "message": "播放已停止",
                            "actionGroupID": action_group_id
                        },
                        "timestamp": int(datetime.now().timestamp() * 1000)
                    }
                    await websocket.send(json.dumps(stop_ack, ensure_ascii=False))
                    logger.info(f"客户端 {client_id} 停止播放，actionGroupID: {action_group_id}")
                else:
                    # 没有找到对应的播放任务
                    error_msg = {
                        "type": "error",
                        "data": {
                            "message": f"未找到actionGroupID为 {action_group_id} 的播放任务",
                            "actionGroupID": action_group_id
                        },
                        "timestamp": int(datetime.now().timestamp() * 1000)
                    }
                    await websocket.send(json.dumps(error_msg, ensure_ascii=False))

            elif msg_type == 'echo':
                # 回声测试
                response = {
                    "type": "echo_response",
                    "data": {
                        "original_message": data.get('message', ''),
                        "server_note": "这是回声测试的响应"
                    },
                    "timestamp": int(datetime.now().timestamp() * 1000)
                }
                await websocket.send(json.dumps(response, ensure_ascii=False))

            elif msg_type == 'broadcast':
                # 广播消息
                broadcast_msg = {
                    "type": "broadcast",
                    "data": {
                        "message": data.get('message', ''),
                        "from_client": client_id
                    },
                    "timestamp": int(datetime.now().timestamp() * 1000)
                }
                await self.broadcast_message(json.dumps(broadcast_msg, ensure_ascii=False), sender=websocket)

            elif msg_type == 'get_server_info':
                # 获取服务器信息
                server_info = {
                    "type": "server_info",
                    "data": {
                        "host": self.host,
                        "port": self.port,
                        "protocol": "ws",
                        "connected_clients": len(self.connected_clients),
                        "server_ips": get_local_ipv4_addresses()
                    },
                    "timestamp": int(datetime.now().timestamp() * 1000)
                }
                await websocket.send(json.dumps(server_info, ensure_ascii=False))

            else:
                # 未知消息类型的默认响应
                response = {
                    "type": "unknown_command",
                    "data": {
                        "received_message": data,
                        "note": "未知的消息类型"
                    },
                    "timestamp": int(datetime.now().timestamp() * 1000)
                }
                await websocket.send(json.dumps(response, ensure_ascii=False))

        except json.JSONDecodeError:
            # JSON解析错误时也发送ack，但状态为error
            error_ack = {
                "type": "ack",
                "data": {
                    "status": "error",
                    "message": "无效的JSON格式，消息解析失败"
                },
                "timestamp": int(datetime.now().timestamp() * 1000)
            }
            await websocket.send(json.dumps(error_ack, ensure_ascii=False))

            # 同时发送错误消息
            error_msg = {
                "type": "error",
                "data": {
                    "message": "无效的JSON格式",
                    "original_message": message
                },
                "timestamp": int(datetime.now().timestamp() * 1000)
            }
            await websocket.send(json.dumps(error_msg, ensure_ascii=False))

    async def broadcast_message(self, message, sender=None):
        """向所有连接的客户端广播消息"""
        if self.connected_clients:
            tasks = []
            for client in self.connected_clients:
                if client != sender:  # 不发送给消息发送者
                    try:
                        tasks.append(client.send(message))
                    except:
                        # 如果发送失败，从连接列表中移除
                        self.connected_clients.remove(client)
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)

    def log_network_info(self):
        """输出网络信息到日志"""
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
            protocol = "ws"
            logger.info("可访问地址:")
            for ip in ipv4_addresses:
                logger.info(f"  - {protocol}://{ip}:{self.port}")

        logger.info(f"本地回环地址: {protocol}://127.0.0.1:{self.port}")
        logger.info(f"选择的监听地址: {self.host}:{self.port}")
        logger.info("===")

    async def start_server(self):
        """启动WebSocket服务器"""
        # 显示网络信息
        self.log_network_info()

        protocol = "ws"
        logger.info(f"启动WebSocket服务器在 {protocol}://{self.host}:{self.port}")

        # 启动服务器
        async with websockets.serve(
                self.handle_client,
                self.host,
                self.port
        ):
            logger.info("服务器已启动，等待客户端连接...")
            await asyncio.Future()  # 永久运行


if __name__ == "__main__":
    # 自动选择IP地址
    server = WebSocketServer()

    try:
        asyncio.run(server.start_server())
    except KeyboardInterrupt:
        logger.info("服务器被用户中断")
    except Exception as e:
        logger.error(f"服务器运行错误: {e}")
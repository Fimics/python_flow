import requests
import json
import os
from pathlib import Path


class GLMTTS:
    def __init__(self, api_key):
        """
        初始化TTS客户端
        :param api_key: 智谱AI的API密钥
        """
        self.api_url = "https://open.bigmodel.cn/api/paas/v4/audio/speech"  # 完整的API链接
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }

    def text_to_speech(self, text, voice="tongtong", response_format="pcm",
                       stream=False, speed=1.0, volume=1.0, watermark_enabled=True):
        """
        将文本转换为语音
        """
        # 检查文本长度
        if len(text) > 1024:
            raise ValueError("文本长度不能超过1024个字符")

        # 构建请求数据
        data = {
            "model": "glm-tts",
            "input": text,
            "voice": voice,
            "response_format": response_format,
            "stream": stream
        }

        # 可选参数
        if speed != 1.0:
            data["speed"] = speed
        if volume != 1.0:
            data["volume"] = volume
        if not watermark_enabled:
            data["watermark_enabled"] = watermark_enabled

        print(f"请求数据: {json.dumps(data, ensure_ascii=False)}")

        try:
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=data,
                timeout=30
            )

            print(f"响应状态码: {response.status_code}")

            if response.status_code == 200:
                content_type = response.headers.get('Content-Type', '')
                print(f"响应Content-Type: {content_type}")

                if 'audio' in content_type or response.content:
                    print("成功获取音频数据")
                    return response.content
                else:
                    # 可能是错误信息
                    try:
                        error_data = response.json()
                        print(f"错误响应: {error_data}")
                        raise Exception(f"API返回错误: {error_data}")
                    except:
                        print(f"响应内容: {response.text[:200]}...")
                        raise Exception("响应格式不是音频")
            else:
                # 详细错误信息
                try:
                    error_data = response.json()
                    error_msg = error_data.get('message', '未知错误')
                    error_code = error_data.get('code', '无错误码')
                    print(f"错误详情: 代码={error_code}, 消息={error_msg}")
                    raise Exception(f"API请求失败 (状态码{response.status_code}): {error_msg}")
                except:
                    print(f"原始错误响应: {response.text}")
                    raise Exception(f"HTTP错误 {response.status_code}: {response.text}")

        except requests.exceptions.RequestException as e:
            print(f"网络请求异常: {str(e)}")
            raise Exception(f"网络请求错误: {str(e)}")


def save_pcm_to_file(pcm_data, filename, output_dir="audio_output"):
    """保存PCM数据到文件"""
    Path(output_dir).mkdir(exist_ok=True)
    file_path = os.path.join(output_dir, f"{filename}.pcm")

    with open(file_path, 'wb') as f:
        f.write(pcm_data)

    print(f"PCM音频已保存到: {file_path}")
    print(f"文件大小: {len(pcm_data)} 字节")
    return file_path


def main():
    # 使用您提供的API密钥
    API_KEY = "eca191a6911a45d988cc2855a3310bf9.UvQgwYeV2z7CRugp"  # 直接使用您的密钥

    # 初始化TTS客户端
    tts_client = GLMTTS(API_KEY)

    # 使用简单的测试文本
    text = """
      女朋友生气时，我深情地对她说：“你知道吗？科学家说，人类遇到真爱时，大脑会分泌苯基乙胺…”
她冷冷打断：“所以呢？”
我：“…所以我刚刚脑子一抽，把你口红当马克笔画白板了。但你看！这个哑光雾面效果其实挺适合办公室会议的！"""

    try:
        print("\n=== 开始文本转语音 ===")
        print(f"转换文本: {text}")

        # 调用API（使用最简参数）
        pcm_data = tts_client.text_to_speech(
            text=text,
            voice="tongtong",
            response_format="pcm",
            stream=False
        )

        print("✅ 语音生成成功！")

        # 保存文件
        pcm_file_path = save_pcm_to_file(pcm_data, "test_audio")
        print("✅ 文件保存完成！")

        # 显示文件信息
        print(f"\n📁 文件信息:")
        print(f"位置: {os.path.abspath(pcm_file_path)}")
        print(f"大小: {len(pcm_data)} 字节")

    except Exception as e:
        print(f"❌ 错误: {str(e)}")

        # 提供调试建议
        print("\n🔧 调试建议:")
        print("1. 检查API密钥是否正确")
        print("2. 检查网络连接")
        print("3. 确认账号有足够的余额或权限")
        print("4. 尝试使用不同的文本或参数")


# 简单的测试函数
def quick_test():
    """快速测试函数"""
    API_KEY = "eca191a6911a45d988cc2855a3310bf9.UvQgwYeV2z7CRugp"

    print("=== 快速测试 ===")

    # 直接测试API连接
    url = "https://open.bigmodel.cn/api/paas/v4/audio/speech"
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }
    data = {
        "model": "glm-tts",
        "input": "你好",
        "voice": "tongtong",
        "response_format": "pcm"
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        print(f"状态码: {response.status_code}")

        if response.status_code == 200:
            print("✅ API请求成功！")
            # 保存音频
            with open("test_simple.pcm", "wb") as f:
                f.write(response.content)
            print("✅ 音频文件已保存: test_simple.pcm")
        else:
            print(f"❌ 错误响应: {response.text}")

    except Exception as e:
        print(f"❌ 请求异常: {e}")


if __name__ == "__main__":
    # 运行主程序
    main()

    # 或者运行快速测试
    # quick_test()
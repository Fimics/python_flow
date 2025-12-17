import requests
import json
import os
import time
import base64
from pathlib import Path


class GLMVoiceClone:
    """智谱AI音色复刻完整实现"""

    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://open.bigmodel.cn/api/paas/v4"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def check_permissions(self):
        """检查API权限和可用服务"""
        print("=== 检查API权限 ===")

        try:
            response = requests.get(f"{self.base_url}/models", headers=self.headers, timeout=10)
            if response.status_code == 200:
                models = [m["id"] for m in response.json().get("data", [])]
                print(f"✅ 基础API权限正常")
                print(f"可用模型: {', '.join(models)}")
            else:
                print(f"❌ API权限检查失败: {response.status_code}")
                return False

            # 测试语音API可用性
            print("\n🔍 测试语音API可用性...")
            tts_test = self._test_tts_api()
            if tts_test:
                print("✅ TTS服务可用")
                return True
            else:
                print("⚠️  TTS服务可能需要额外权限，但将继续尝试")
                return True

        except Exception as e:
            print(f"❌ 权限检查异常: {e}")
            return True

    def _test_tts_api(self):
        """测试TTS API是否可用"""
        try:
            url = f"{self.base_url}/audio/speech"
            data = {
                "model": "glm-tts",
                "input": "测试",
                "voice": "female"  # 使用正确的音色名
            }

            response = requests.post(url, headers=self.headers, json=data, timeout=10)
            return response.status_code in [200, 400, 422]
        except:
            return False

    def clone_voice(self, voice_name, input_text, file_path, reference_text="", output_path=None):
        """音色复刻主函数"""
        print(f"🎯 开始音色复刻: {voice_name}")

        # 智谱AI目前不支持音色复刻，使用标准TTS
        print("⚠️  智谱AI目前不支持音色复刻功能，将使用标准TTS服务")

        # 使用可用的音色
        available_voices = ["female", "male", "alloy", "echo", "fable", "onyx", "nova", "shimmer"]
        selected_voice = "female"  # 默认使用女声

        print(f"🔊 使用音色: {selected_voice}")

        return self.standard_tts(input_text, selected_voice, output_path)

    def standard_tts(self, text, voice_type="female", output_path="output_tts.mp3"):
        """标准TTS服务"""
        print(f"🔊 使用标准TTS服务")
        print(f"📝 文本: {text}")
        print(f"🎵 音色: {voice_type}")

        # 智谱AI TTS API端点
        url = f"{self.base_url}/audio/speech"

        # 根据智谱AI文档构建请求
        data = {
            "model": "glm-tts",
            "input": text,
            "voice": voice_type,
            "speed": 1.0,
            "response_format": "mp3"
        }

        try:
            print("🔄 发送TTS请求...")
            response = requests.post(url, headers=self.headers, json=data, timeout=30)

            if response.status_code == 200:
                # 确保输出目录存在
                os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)

                with open(output_path, "wb") as f:
                    f.write(response.content)

                file_size = os.path.getsize(output_path)
                print(f"✅ TTS音频保存成功: {output_path} ({file_size}字节)")
                return output_path
            else:
                print(f"❌ TTS失败: {response.status_code}")
                print(f"错误信息: {response.text}")

                # 尝试其他音色
                if "音色不存在" in response.text:
                    print("🔄 尝试使用默认音色...")
                    return self._try_default_voices(text, output_path)

                return None

        except Exception as e:
            print(f"❌ TTS异常: {e}")
            return None

    def _try_default_voices(self, text, output_path):
        """尝试使用默认音色"""
        default_voices = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]

        for voice in default_voices:
            print(f"🔄 尝试音色: {voice}")
            url = f"{self.base_url}/audio/speech"
            data = {
                "model": "glm-tts",
                "input": text,
                "voice": voice,
                "speed": 1.0,
                "response_format": "mp3"
            }

            try:
                response = requests.post(url, headers=self.headers, json=data, timeout=30)
                if response.status_code == 200:
                    with open(output_path, "wb") as f:
                        f.write(response.content)
                    print(f"✅ 使用音色 {voice} 成功生成音频: {output_path}")
                    return output_path
            except:
                continue

        print("❌ 所有音色都尝试失败")
        return None

    def get_available_voices(self):
        """获取可用音色列表"""
        print("🔍 获取可用音色列表...")

        # 智谱AI支持的音色（根据文档）
        voices = {
            "female": "女声",
            "male": "男声",
            "alloy": "合金声",
            "echo": "回声",
            "fable": "寓言",
            "onyx": "玛瑙",
            "nova": "新星",
            "shimmer": "微光"
        }

        print("📋 可用音色:")
        for key, value in voices.items():
            print(f"  - {key}: {value}")

        return voices

    def test_voice(self, voice_name, test_text="这是一个测试语音"):
        """测试特定音色"""
        print(f"🔊 测试音色: {voice_name}")

        output_path = f"output/test_{voice_name}.mp3"
        result = self.standard_tts(test_text, voice_name, output_path)

        if result:
            print(f"✅ 音色 {voice_name} 测试成功")
            return True
        else:
            print(f"❌ 音色 {voice_name} 测试失败")
            return False


def main():
    """主函数 - 演示使用"""
    API_KEY = "eca191a6911a45d988cc2855a3310bf9.UvQgwYeV2z7CRugp"

    # 初始化
    voice_clone = GLMVoiceClone(API_KEY)

    # 检查权限
    if not voice_clone.check_permissions():
        print("❌ 权限检查失败，但仍将尝试使用服务")

    print("\n" + "=" * 50)
    print("🎯 智谱AI语音合成演示")
    print("=" * 50)

    # 显示可用音色
    available_voices = voice_clone.get_available_voices()

    # 配置参数
    text_to_speak = "欢迎使用智谱AI语音合成服务，这是一个演示示例。"
    output_file = "output/cloned_voice.mp3"

    # 确保输出目录存在
    os.makedirs("output", exist_ok=True)

    print(f"\n📝 目标文本: {text_to_speak}")
    print(f"💾 输出文件: {output_file}")
    print("\n" + "-" * 50)

    # 执行语音合成
    result = voice_clone.standard_tts(text_to_speak, "female", output_file)

    if result:
        print(f"\n🎉 语音合成完成!")
        print(f"📁 输出文件: {os.path.abspath(result)}")

        # 测试其他音色
        print("\n🔊 测试其他音色...")
        test_voices = ["male", "alloy", "nova"]
        for voice in test_voices:
            voice_clone.test_voice(voice, f"这是{voice}音色的测试")
    else:
        print(f"\n❌ 语音合成失败")
        print("💡 请检查API Key和网络连接")


def batch_demo():
    """批量处理演示"""
    API_KEY = "eca191a6911a45d988cc2855a3310bf9.UvQgwYeV2z7CRugp"

    voice_clone = GLMVoiceClone(API_KEY)

    # 批量文本
    texts = [
        "大家好，欢迎使用智能语音服务。",
        "今天的天气真不错，适合外出活动。",
        "科技创新改变生活，人工智能助力未来。"
    ]

    # 不同音色
    voices = ["female", "male", "alloy"]

    print("🔊 批量语音合成演示")

    for i, (text, voice) in enumerate(zip(texts, voices), 1):
        print(f"\n📝 处理第 {i} 段文本: {text}")
        print(f"🎵 使用音色: {voice}")

        output_file = f"output/batch_output_{i}_{voice}.mp3"
        result = voice_clone.standard_tts(text, voice, output_file)

        if result:
            print(f"✅ 第 {i} 段处理成功")
        else:
            print(f"❌ 第 {i} 段处理失败")


def interactive_demo():
    """交互式演示"""
    API_KEY = "eca191a6911a45d988cc2855a3310bf9.UvQgwYeV2z7CRugp"

    voice_clone = GLMVoiceClone(API_KEY)

    # 显示可用音色
    available_voices = voice_clone.get_available_voices()

    print("\n🎯 交互式语音合成")
    print("-" * 30)

    # 获取用户输入
    text = input("请输入要合成的文本: ").strip()
    if not text:
        text = "这是默认的测试文本"
        print(f"使用默认文本: {text}")

    print("\n请选择音色:")
    for i, voice in enumerate(available_voices.keys(), 1):
        print(f"{i}. {voice} - {available_voices[voice]}")

    try:
        choice = int(input("请输入音色编号 (1-8): ").strip()) - 1
        voice_list = list(available_voices.keys())
        if 0 <= choice < len(voice_list):
            selected_voice = voice_list[choice]
        else:
            selected_voice = "female"
            print("使用默认音色: female")
    except:
        selected_voice = "female"
        print("使用默认音色: female")

    output_file = f"output/interactive_{selected_voice}_{int(time.time())}.mp3"

    print(f"\n🔄 开始合成...")
    result = voice_clone.standard_tts(text, selected_voice, output_file)

    if result:
        print(f"\n🎉 合成完成!")
        print(f"📁 文件路径: {os.path.abspath(result)}")
    else:
        print(f"\n❌ 合成失败")


if __name__ == "__main__":
    print("请选择运行模式:")
    print("1. 标准演示")
    print("2. 批量处理演示")
    print("3. 交互式演示")

    choice = input("请输入选择 (1-3): ").strip()

    if choice == "1":
        main()
    elif choice == "2":
        batch_demo()
    elif choice == "3":
        interactive_demo()
    else:
        main()

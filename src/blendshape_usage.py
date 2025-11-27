from blendshape_reader import BlendshapeReader

if __name__ == "__main__":
    # 方法2: 假设脚本在项目根目录下运行
    csv_path = "data/csv/default.csv"

    reader = BlendshapeReader()
    all_data = reader.read_csv(csv_path)

    if all_data:
        print(f"✅ 数据加载成功! 帧数: {len(all_data)}")
    else:
        print("❌ 数据加载失败!")

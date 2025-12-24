protoc --python_out=. message.proto
protoc --python_out=. message.proto

1. 然后重新创建虚拟环境,激活虚拟环境
cd ~/code/python/python_flow
python3 -m venv .venv
source .venv/bin/activate

# 完全卸载所有相关包
pip uninstall -y grpcio grpcio-tools protobuf

# 清除 pip 缓存
pip cache purge
# 验证安装
pip show protobuf
# 应显示版本 6.33.2

-------------------------------------------------------------------------
pip install -r requirements.txt
python gen_proto.py

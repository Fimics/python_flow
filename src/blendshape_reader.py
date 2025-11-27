import csv
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import logging


class BlendshapeReader:
    """
    Blendshape数据读取工具类
    用于读取CSV格式的blendshape动画数据
    """

    def __init__(self, log_level=logging.INFO):
        """
        初始化Blendshape读取器

        Args:
            log_level: 日志级别
        """
        self.logger = self._setup_logger(log_level)
        self.data = []
        self.column_names = []
        self.timestamps = []

    def _setup_logger(self, level):
        """设置日志器"""
        logger = logging.getLogger(__name__)
        logger.setLevel(level)

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    def read_csv(self, file_path: str) -> Optional[List[Dict[str, float]]]:
        """
        从CSV文件读取blendshape数据并直接返回

        Args:
            file_path: CSV文件路径

        Returns:
            Optional[List[Dict[str, float]]]: 读取成功返回数据列表，失败返回None
        """
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                self.logger.error(f"文件不存在: {file_path}")
                return None

            self.logger.info(f"开始读取文件: {file_path}")

            with open(file_path, 'r', encoding='utf-8') as file:
                # 使用csv.reader读取逗号分隔的文件
                csv_reader = csv.reader(file)

                # 第一行就是列名
                self.column_names = next(csv_reader)
                self.logger.info(f"检测到列名: {self.column_names[:5]}...")
                self.logger.info(f"总列数: {len(self.column_names)}")

                # 验证列数
                if len(self.column_names) < 3:
                    self.logger.error(f"列数不足，期望至少3列，实际{len(self.column_names)}列")
                    return None

                # 读取数据行
                self.data = []
                self.timestamps = []
                line_count = 0

                for row in csv_reader:
                    if row:  # 跳过空行
                        if len(row) >= 3:
                            timestamp = row[0]

                            # 创建字典映射（从第3列开始是blendshape值）
                            blendshape_dict = {}
                            for i in range(2, min(len(row), len(self.column_names))):
                                try:
                                    value = float(row[i])
                                    blendshape_dict[self.column_names[i]] = value
                                except (ValueError, IndexError):
                                    continue

                            self.data.append(blendshape_dict)
                            self.timestamps.append(timestamp)
                            line_count += 1

                self.logger.info(f"成功读取 {line_count} 行blendshape数据")
                return self.data

        except Exception as e:
            self.logger.error(f"读取文件时发生错误: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())
            return None

    def read_csv_with_info(self, file_path: str) -> Optional[Tuple[List[Dict[str, float]], List[str], List[str]]]:
        """
        读取CSV文件并返回数据、时间戳和列名

        Args:
            file_path: CSV文件路径

        Returns:
            Optional[Tuple]: (数据列表, 时间戳列表, 列名列表) 或 None
        """
        data = self.read_csv(file_path)
        if data is not None:
            return data, self.timestamps, self.column_names
        return None

    def get_blendshape_data(self) -> List[Dict[str, float]]:
        """获取blendshape数据"""
        return self.data

    def get_timestamps(self) -> List[str]:
        """获取时间戳列表"""
        return self.timestamps

    def get_blendshape_names(self) -> List[str]:
        """获取blendshape名称列表"""
        if self.data:
            return list(self.data[0].keys())
        return []

    def get_frame_count(self) -> int:
        """获取帧数"""
        return len(self.data)

    def get_blendshape_value(self, frame_index: int, blendshape_name: str) -> Optional[float]:
        """获取指定帧和blendshape的值"""
        if 0 <= frame_index < len(self.data):
            return self.data[frame_index].get(blendshape_name)
        return None

    def get_frame_data(self, frame_index: int) -> Optional[Dict[str, float]]:
        """获取指定帧的所有blendshape数据"""
        if 0 <= frame_index < len(self.data):
            return self.data[frame_index]
        return None

    def get_blendshape_range(self, blendshape_name: str) -> Dict[str, float]:
        """获取指定blendshape在整个动画中的数值范围"""
        values = []
        for frame_data in self.data:
            if blendshape_name in frame_data:
                values.append(frame_data[blendshape_name])

        if values:
            return {
                'min': min(values),
                'max': max(values),
                'average': sum(values) / len(values),
                'count': len(values)
            }
        else:
            return {'min': 0, 'max': 0, 'average': 0, 'count': 0}

    def clear_data(self):
        """清除所有数据"""
        self.data = []
        self.timestamps = []
        self.column_names = []
        self.logger.info("数据已清除")


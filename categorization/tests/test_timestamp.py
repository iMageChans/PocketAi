from django.test import TestCase
from datetime import datetime
from utils.serializers_fields import TimestampField


class TimestampTestCase(TestCase):
    def test_timestamp_serialization(self):
        """测试时间戳序列化"""
        field = TimestampField()
        # 创建一个固定的datetime对象
        dt = datetime(2023, 1, 1, 12, 0, 0)
        # 序列化为时间戳
        timestamp = field.to_representation(dt)
        # 验证结果
        self.assertIsInstance(timestamp, int)
        
        # 反序列化回datetime
        dt_back = field.to_internal_value(timestamp)
        # 验证结果（注意可能有小数秒的差异）
        self.assertEqual(dt.year, dt_back.year)
        self.assertEqual(dt.month, dt_back.month)
        self.assertEqual(dt.day, dt_back.day)
        self.assertEqual(dt.hour, dt_back.hour)
        self.assertEqual(dt.minute, dt_back.minute) 
"""
数据库连接验证测试

验证 PortalDB 可正常连接数据库并执行查询操作
TC-DB-001: 查询 t_appointment 表中指定患者预约记录
TC-DB-002: 将最新预约时间修改为整点-15min
"""
from db.portal_db import PortalDB
from utils.logger import get_logger

log = get_logger(__name__)


class TestDatabase:
    """数据库连接与查询测试"""

    def test_query_appointment_by_patient(self, db: PortalDB):
        """TC-DB-001: 查询 patient_id=3702 的预约记录"""
        sql = "SELECT * FROM `t_appointment` WHERE `patient_id` = %s ORDER BY id DESC"
        rows = db.query(sql, (3702,))

        log.info(f"查询结果共 {len(rows)} 条记录")
        for i, row in enumerate(rows, 1):
            log.info(f"  第 {i} 条: {row}")

        assert isinstance(rows, list), "查询结果应为列表"

    def test_set_appointment_to_last_full_hour(self, db: PortalDB):
        """TC-DB-002: 将 patient_id=3702 最新预约时间修改为整点-15min"""
        result = db.set_appointment_to_last_full_hour(patient_id=3702)

        log.info(f"数据库当前时间: {result['db_now']}")
        log.info(f"appointment_id: {result['appointment_id']}")
        log.info(f"end_datetime:   {result['end_datetime']}")
        log.info(f"start_datetime: {result['start_datetime']}")

        # 验证 end 是整点（分/秒为0）
        assert result["end_datetime"].minute == 0, "end_datetime 分钟应为 0"
        assert result["end_datetime"].second == 0, "end_datetime 秒应为 0"

        # 验证 start 比 end 早 15 分钟
        diff = (result["end_datetime"] - result["start_datetime"]).total_seconds()
        assert diff == 900, f"start 与 end 应相差 900 秒(15分钟)，实际相差 {diff} 秒"

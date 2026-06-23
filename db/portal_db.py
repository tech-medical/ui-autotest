"""
Portal 业务数据库操作

与 PortalHomePage 对齐，封装 Portal 相关的数据库操作。
UI 测试脚本只需调用业务方法，不直接写 SQL。
"""
from __future__ import annotations

from datetime import datetime, timedelta

from db.base_db import BaseDB


class PortalDB(BaseDB):
    """Portal 业务数据库操作类"""

    # ── 用户相关 ────────────────────────────────

    def get_user_by_email(self, email: str) -> dict | None:
        """根据邮箱查询用户"""
        return self.query_one(
            "SELECT * FROM users WHERE email = %s", (email,)
        )

    def get_user_by_id(self, user_id: int) -> dict | None:
        """根据 ID 查询用户"""
        return self.query_one(
            "SELECT * FROM users WHERE id = %s", (user_id,)
        )

    def update_user_field(self, email: str, field: str, value: str) -> int:
        """更新用户指定字段（field 为列名，自动做参数化）"""
        # field 只允许字母+下划线，防注入
        if not field.isidentifier():
            raise ValueError(f"非法字段名: {field}")
        sql = f"UPDATE users SET `{field}` = %s WHERE email = %s"
        with self._get_conn() as conn:
            with conn.cursor() as cur:
                rows = cur.execute(sql, (value, email))
                conn.commit()
        return rows

    # ── 预约相关 ────────────────────────────────

    def get_appointments_by_user(self, user_id: int) -> list[dict]:
        """查询用户的预约列表（按创建时间倒序）"""
        return self.query(
            "SELECT * FROM appointments WHERE user_id = %s ORDER BY created_at DESC",
            (user_id,),
        )

    def get_appointment_by_id(self, appointment_id: int) -> dict | None:
        """根据 ID 查询预约"""
        return self.query_one(
            "SELECT * FROM appointments WHERE id = %s", (appointment_id,)
        )

    def delete_appointment(self, appointment_id: int) -> int:
        """删除指定预约"""
        return self.delete("appointments", "id = %s", (appointment_id,))

    def delete_test_appointments(self, user_id: int) -> int:
        """删除指定用户的所有测试预约"""
        return self.delete("appointments", "user_id = %s", (user_id,))

    def count_appointments(self, user_id: int) -> int:
        """统计用户预约数量"""
        return self.count("appointments", "user_id = %s", (user_id,))

    def set_appointment_to_last_full_hour(self, patient_id: int) -> dict:
        """
        将指定患者最新预约的时间改为：
          - appointment_end_datetime   = 数据库当前时间的整点（分/秒归零）
          - appointment_start_datetime = end_datetime - 15 分钟

        逻辑：
          1. 查询 patient_id 最新一条预约（id DESC LIMIT 1）
          2. SELECT NOW() 获取数据库服务端当前时间
          3. 截断到整点：13:06 → 13:00，13:00 → 13:00
          4. start = end - 15 分钟
          5. UPDATE t_appointment

        返回 dict:
          {
            "appointment_id": int,
            "db_now":         datetime,   # 数据库当前时间
            "end_datetime":   datetime,   # 写入的 end 值
            "start_datetime": datetime,   # 写入的 start 值
          }

        异常：
          ValueError  — patient_id 下没有预约记录
        """
        # ① 查最新一条预约
        appointment = self.query_one(
            "SELECT * FROM `t_appointment` WHERE `patient_id` = %s ORDER BY id DESC LIMIT 1",
            (patient_id,),
        )
        if appointment is None:
            raise ValueError(f"patient_id={patient_id} 没有找到任何预约记录")

        appointment_id = appointment["id"]
        self._log.info(f"[set_appointment_to_last_full_hour] 找到最新预约 id={appointment_id}")

        # ② 获取数据库当前时间
        row = self.query_one("SELECT NOW() AS db_now")
        db_now: datetime = row["db_now"]
        self._log.info(f"[set_appointment_to_last_full_hour] 数据库当前时间: {db_now}")

        # ③ 截断到整点（分/秒/微秒归零）
        end_datetime = db_now.replace(minute=0, second=0, microsecond=0)

        # ④ start = end - 15 分钟
        start_datetime = end_datetime - timedelta(minutes=15)

        self._log.info(
            f"[set_appointment_to_last_full_hour] "
            f"end={end_datetime}  start={start_datetime}"
        )

        # ⑤ UPDATE
        sql = (
            "UPDATE `t_appointment` "
            "SET `appointment_end_datetime` = %s, `appointment_start_datetime` = %s "
            "WHERE `id` = %s"
        )
        affected = self.execute(sql, (end_datetime, start_datetime, appointment_id))
        self._log.info(
            f"[set_appointment_to_last_full_hour] UPDATE 影响行数: {affected}"
        )

        return {
            "appointment_id": appointment_id,
            "db_now":         db_now,
            "end_datetime":   end_datetime,
            "start_datetime": start_datetime,
        }

    # ── 通用查询 ────────────────────────────────

    def get_table_count(self, table: str, where: str = "1=1", where_params=None) -> int:
        """通用表计数（where 需参数化）"""
        return self.count(table, where, where_params)

    def query_custom(self, sql: str, params=None) -> list[dict]:
        """
        自定义查询（兜底方法）

        仅当上述业务方法无法满足时使用，SQL 需参数化。
        优先扩展业务方法，而非长期使用此方法。
        """
        return self.query(sql, params)

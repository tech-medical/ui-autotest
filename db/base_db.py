"""
数据库操作基类

职责：
  1. 连接池管理（dbutils.PooledDB + pymysql）
  2. 通用 CRUD（query / query_one / execute / insert / update / delete / count）
  3. 事务上下文管理器

设计对齐 BasePage：
  - _log 属性记录日志
  - 子类只需关注业务方法，不关心连接细节
"""
from __future__ import annotations

from contextlib import contextmanager
from typing import Any

import pymysql
from dbutils.pooled_db import PooledDB

from config.config import config
from utils.logger import get_logger

logger = get_logger(__name__)


class BaseDB:
    """数据库操作基类，提供连接池管理和通用 CRUD"""

    _pool: PooledDB | None = None  # 类级别共享连接池

    def __init__(self):
        self._log = get_logger(self.__class__.__name__)
        self._init_pool()

    # ── 连接池 ──────────────────────────────────

    @classmethod
    def _init_pool(cls) -> None:
        """懒初始化连接池（所有子类共享）"""
        if cls._pool is not None:
            return
        cls._pool = PooledDB(
            creator=pymysql,
            maxconnections=config.DB_POOL_SIZE,
            mincached=0,
            maxcached=config.DB_POOL_SIZE,
            blocking=True,
            host=config.DB_HOST,
            port=config.DB_PORT,
            user=config.DB_USER,
            password=config.DB_PASSWORD,
            database=config.DB_NAME,
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,
        )
        logger.info(
            f"数据库连接池初始化完成 → {config.DB_HOST}:{config.DB_PORT}/{config.DB_NAME}"
        )

    @contextmanager
    def _get_conn(self):
        """获取连接的上下文管理器，用完自动归还"""
        conn = self._pool.connection()
        try:
            yield conn
        finally:
            conn.close()

    # ── 通用查询 ────────────────────────────────

    def query(self, sql: str, params: Any = None) -> list[dict]:
        """执行查询，返回所有结果行（list[dict]）"""
        with self._get_conn() as conn:
            with conn.cursor() as cur:
                affected = cur.execute(sql, params)
                rows = cur.fetchall()
        self._log.debug(f"[QUERY] {sql} | params={params} | rows={affected}")
        return rows

    def query_one(self, sql: str, params: Any = None) -> dict | None:
        """执行查询，返回单行结果（dict | None）"""
        with self._get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, params)
                row = cur.fetchone()
        self._log.debug(f"[QUERY ONE] {sql} | params={params} | result={'hit' if row else 'miss'}")
        return row

    # ── 通用增删改 ──────────────────────────────

    def execute(self, sql: str, params: Any = None) -> int:
        """执行增/删/改 SQL，返回影响行数"""
        with self._get_conn() as conn:
            with conn.cursor() as cur:
                rows = cur.execute(sql, params)
                conn.commit()
        self._log.debug(f"[EXECUTE] {sql} | params={params} | affected={rows}")
        return rows

    def execute_many(self, sql: str, params_list: list) -> int:
        """批量执行增/删/改 SQL，返回累计影响行数"""
        with self._get_conn() as conn:
            with conn.cursor() as cur:
                rows = cur.executemany(sql, params_list)
                conn.commit()
        self._log.debug(f"[EXECUTE MANY] {sql} | batch={len(params_list)} | affected={rows}")
        return rows

    # ── 便捷 CRUD ───────────────────────────────

    def insert(self, table: str, data: dict) -> int:
        """
        便捷插入，返回自增主键 ID

        用法: db.insert("users", {"email": "a@b.com", "name": "Alice"})
        """
        cols = ", ".join(data.keys())
        placeholders = ", ".join(["%s"] * len(data))
        sql = f"INSERT INTO {table} ({cols}) VALUES ({placeholders})"
        with self._get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, tuple(data.values()))
                conn.commit()
                last_id = cur.lastrowid
        self._log.debug(f"[INSERT] table={table} | data={data} | last_id={last_id}")
        return last_id

    def update(self, table: str, data: dict, where: str, where_params: Any = None) -> int:
        """
        便捷更新，返回影响行数

        用法: db.update("users", {"name": "Bob"}, "email = %s", "a@b.com")
        """
        set_clause = ", ".join([f"`{k}` = %s" for k in data.keys()])
        sql = f"UPDATE {table} SET {set_clause} WHERE {where}"
        params = tuple(data.values()) + (() if where_params is None else (where_params,))
        with self._get_conn() as conn:
            with conn.cursor() as cur:
                rows = cur.execute(sql, params)
                conn.commit()
        self._log.debug(f"[UPDATE] table={table} | where={where} | affected={rows}")
        return rows

    def delete(self, table: str, where: str, where_params: Any = None) -> int:
        """
        便捷删除，返回影响行数

        用法: db.delete("appointments", "id = %s", 123)
        """
        sql = f"DELETE FROM {table} WHERE {where}"
        rows = self.execute(sql, where_params)
        self._log.debug(f"[DELETE] table={table} | where={where} | affected={rows}")
        return rows

    def count(self, table: str, where: str = "1=1", where_params: Any = None) -> int:
        """便捷计数"""
        sql = f"SELECT COUNT(*) AS cnt FROM {table} WHERE {where}"
        row = self.query_one(sql, where_params)
        return row["cnt"] if row else 0

    # ── 事务 ────────────────────────────────────

    @contextmanager
    def transaction(self):
        """
        事务上下文管理器

        用法:
            with db.transaction() as conn:
                conn.cursor().execute("INSERT ...")
                conn.cursor().execute("UPDATE ...")
            # 正常退出自动 commit，异常自动 rollback
        """
        conn = self._pool.connection()
        try:
            yield conn
            conn.commit()
            self._log.debug("[TRANSACTION] committed")
        except Exception:
            conn.rollback()
            self._log.warning("[TRANSACTION] rolled back")
            raise
        finally:
            conn.close()

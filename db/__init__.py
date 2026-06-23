"""
数据库操作模块

提供与 BasePage -> 业务 PO 同构的 BaseDB -> 业务 DB 分层：
  - BaseDB：连接池管理 + 通用 CRUD
  - PortalDB：Portal 业务数据库操作
"""

from db.base_db import BaseDB
from db.portal_db import PortalDB

__all__ = ["BaseDB", "PortalDB"]

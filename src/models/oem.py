"""OEM 데이터 모델"""
from src.models.database import get_connection


class OemModel:
    @staticmethod
    def create(name, description="", config_yaml="", conn=None):
        should_close = conn is None
        if conn is None:
            conn = get_connection()
        cursor = conn.execute(
            "INSERT INTO oems (name, description, config_yaml) VALUES (?, ?, ?)",
            (name, description, config_yaml)
        )
        conn.commit()
        oem_id = cursor.lastrowid
        if should_close:
            conn.close()
        return oem_id

    @staticmethod
    def get_all(conn=None):
        should_close = conn is None
        if conn is None:
            conn = get_connection()
        rows = conn.execute("SELECT * FROM oems ORDER BY name").fetchall()
        if should_close:
            conn.close()
        return rows

    @staticmethod
    def get_by_id(oem_id, conn=None):
        should_close = conn is None
        if conn is None:
            conn = get_connection()
        row = conn.execute("SELECT * FROM oems WHERE id = ?", (oem_id,)).fetchone()
        if should_close:
            conn.close()
        return row

    @staticmethod
    def update(oem_id, name=None, description=None, config_yaml=None, conn=None):
        should_close = conn is None
        if conn is None:
            conn = get_connection()
        fields, values = [], []
        if name is not None:
            fields.append("name = ?")
            values.append(name)
        if description is not None:
            fields.append("description = ?")
            values.append(description)
        if config_yaml is not None:
            fields.append("config_yaml = ?")
            values.append(config_yaml)
        if fields:
            fields.append("updated_at = CURRENT_TIMESTAMP")
            values.append(oem_id)
            conn.execute(f"UPDATE oems SET {', '.join(fields)} WHERE id = ?", values)
            conn.commit()
        if should_close:
            conn.close()

    @staticmethod
    def delete(oem_id, conn=None):
        should_close = conn is None
        if conn is None:
            conn = get_connection()
        conn.execute("DELETE FROM oems WHERE id = ?", (oem_id,))
        conn.commit()
        if should_close:
            conn.close()

from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.session_windows import SessionLocal
import logging

logger = logging.getLogger(__name__)

class BaseAdapter:
    def __init__(self):
        self.db: Session = SessionLocal()

    def execute_query(self, query: str, params: tuple = ()):
        try:
            logger.info(f"→ Ejecutando: {query}")
            logger.info(f"→ Con parámetros: {params}")
            self.db.execute(text(query), params)
            self.db.commit()
        except Exception as e:
            logger.error(f"❌ Error en execute_query: {e}")
            self.db.rollback()
            raise

    def fetch_one(self, query: str, params: tuple = ()):
        try:
            logger.info(f"→ Ejecutando: {query}")
            result = self.db.execute(text(query), params)
            return result.fetchone()
        except Exception as e:
            logger.error(f"❌ Error en fetch_one: {e}")
            raise

    def fetch_all(self, query: str, params: tuple = ()):
        try:
            logger.info(f"→ Ejecutando: {query}")
            result = self.db.execute(text(query), params)
            return result.fetchall()
        except Exception as e:
            logger.error(f"❌ Error en fetch_all: {e}")
            raise

    def insert_log(self, user_name: str, action: str, detail: str):
        query = """
        INSERT INTO app_log (user_name, action, detail, created_at)
        VALUES (:user_name, :action, :detail, :created_at)
        """
        self.execute_query(query, {
            "user_name": user_name,
            "action": action,
            "detail": detail,
            "created_at": datetime.now()
        })
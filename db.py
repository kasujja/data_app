from sqlalchemy import create_engine

class Database:
    def __init__(self, uri):
        self.engine = create_engine(uri, pool_pre_ping=True)

    def execute(self, query):
        with self.engine.connect() as conn:
            result = conn.execute(query)
            return result.fetchall()

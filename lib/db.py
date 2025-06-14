from contextlib import asynccontextmanager
import aiomysql

from lib.env import DB_USER, DB_USER_PWD, DB_NAME



@asynccontextmanager
async def db_connect():
    # Configuration de la connexion à MariaDB à partir du fichier .env
    db_config = {
        "host": "127.0.0.1",
        "user": DB_USER,
        "password": DB_USER_PWD,
        "db": DB_NAME
    }

    # Ouverture de la connexion
    conn = await aiomysql.connect(**db_config)
    try:
        # Fourniture de la connexion pour usage temporaire
        yield conn
    finally:
        # Fermeture automatique après usage
        conn.close()


async def get_db():
    # Fournit une connexion au format attendu par Depends(FastAPI)
    async with db_connect() as conn:
        yield conn
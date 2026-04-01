"""
Charge `.env` avant `settings` et enregistre un pilote MySQL compatible.

Ordre : `mysqlclient` (`MySQLdb`) si présent, sinon `PyMySQL` (pratique sous Windows / XAMPP / WAMP).
"""

from pathlib import Path

try:
    from dotenv import load_dotenv

    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
except ImportError:
    pass

try:
    import MySQLdb  # noqa: F401 — fourni par mysqlclient
except ImportError:
    try:
        import pymysql

        pymysql.install_as_MySQLdb()
    except ImportError:
        pass

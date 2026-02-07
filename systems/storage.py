import sqlite3
from typing import Dict


DB_PATH = "arcade_stats.db"


def _connect() -> sqlite3.Connection:
    return sqlite3.connect(DB_PATH)


def init_db() -> None:
    with _connect() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS stats (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                total_runs INTEGER NOT NULL,
                total_coins INTEGER NOT NULL,
                best_score REAL NOT NULL,
                best_coins INTEGER NOT NULL,
                coins_balance INTEGER NOT NULL
            )
            """
        )
        cur.execute(
            """
            INSERT OR IGNORE INTO stats
            (id, total_runs, total_coins, best_score, best_coins, coins_balance)
            VALUES (1, 0, 0, 0, 0, 0)
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS purchases (
                item_id TEXT PRIMARY KEY
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
            """
        )
        conn.commit()


def get_stats() -> Dict[str, float]:
    with _connect() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT total_runs, total_coins, best_score, best_coins, coins_balance "
            "FROM stats WHERE id = 1"
        )
        row = cur.fetchone()
        if not row:
            return {
                "total_runs": 0,
                "total_coins": 0,
                "best_score": 0,
                "best_coins": 0,
                "coins_balance": 0,
            }
        return {
            "total_runs": int(row[0]),
            "total_coins": int(row[1]),
            "best_score": float(row[2]),
            "best_coins": int(row[3]),
            "coins_balance": int(row[4]),
        }


def record_run(score: float, coins: int) -> None:
    with _connect() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT total_runs, total_coins, best_score, best_coins, coins_balance "
            "FROM stats WHERE id = 1"
        )
        total_runs, total_coins, best_score, best_coins, coins_balance = cur.fetchone()
        total_runs += 1
        total_coins += coins
        coins_balance += coins
        best_score = max(best_score, score)
        best_coins = max(best_coins, coins)
        cur.execute(
            """
            UPDATE stats
            SET total_runs = ?, total_coins = ?, best_score = ?, best_coins = ?, coins_balance = ?
            WHERE id = 1
            """,
            (total_runs, total_coins, best_score, best_coins, coins_balance),
        )
        conn.commit()


def get_coins_balance() -> int:
    return int(get_stats()["coins_balance"])


def purchase(item_id: str, cost: int) -> bool:
    with _connect() as conn:
        cur = conn.cursor()
        cur.execute("SELECT item_id FROM purchases WHERE item_id = ?", (item_id,))
        if cur.fetchone():
            return False

        cur.execute("SELECT coins_balance FROM stats WHERE id = 1")
        balance = cur.fetchone()[0]
        if balance < cost:
            return False

        balance -= cost
        cur.execute("UPDATE stats SET coins_balance = ? WHERE id = 1", (balance,))
        cur.execute("INSERT INTO purchases (item_id) VALUES (?)", (item_id,))
        conn.commit()
        return True


def is_owned(item_id: str) -> bool:
    with _connect() as conn:
        cur = conn.cursor()
        cur.execute("SELECT item_id FROM purchases WHERE item_id = ?", (item_id,))
        return cur.fetchone() is not None


def get_setting(key: str, default: str) -> str:
    with _connect() as conn:
        cur = conn.cursor()
        cur.execute("SELECT value FROM settings WHERE key = ?", (key,))
        row = cur.fetchone()
        return row[0] if row else default


def set_setting(key: str, value: str) -> None:
    with _connect() as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO settings (key, value) VALUES (?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            (key, value),
        )
        conn.commit()


def add_coins(amount: int) -> None:
    if amount <= 0:
        return
    with _connect() as conn:
        cur = conn.cursor()
        cur.execute(
            "UPDATE stats SET coins_balance = coins_balance + ? WHERE id = 1",
            (amount,),
        )
        conn.commit()


def unlock_items(item_ids) -> None:
    if not item_ids:
        return
    with _connect() as conn:
        cur = conn.cursor()
        for item_id in item_ids:
            cur.execute(
                "INSERT OR IGNORE INTO purchases (item_id) VALUES (?)", (item_id,)
            )
        conn.commit()


def reset_all() -> None:
    with _connect() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            UPDATE stats
            SET total_runs = 0, total_coins = 0, best_score = 0, best_coins = 0, coins_balance = 0
            WHERE id = 1
            """
        )
        cur.execute("DELETE FROM purchases")
        cur.execute("DELETE FROM settings")
        conn.commit()

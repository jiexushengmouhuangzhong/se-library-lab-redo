"""实验一初始版本：建立图书数据并查询库存。运行：py library.py。"""

from pathlib import Path
import sqlite3

DB_PATH = Path(__file__).with_name("library.db")


def init_database(conn):
    conn.execute("""CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY, title TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT '可借')""")
    conn.execute("""CREATE TABLE IF NOT EXISTS loans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        book_id INTEGER NOT NULL REFERENCES books(id),
        borrower TEXT NOT NULL, borrowed_at TEXT NOT NULL,
        returned_at TEXT)""")
    conn.executemany(
        "INSERT OR IGNORE INTO books(id, title) VALUES (?, ?)",
        [(1, "软件工程导论"), (2, "Python程序设计"), (3, "数据库系统原理")],
    )
    conn.commit()


def query_books(conn):
    for row in conn.execute("SELECT id, title, status FROM books ORDER BY id"):
        print(f"{row[0]} | {row[1]} | {row[2]}")


def main():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        init_database(conn)
        while True:
            print("\n图书借阅系统：1 查询图书；0 退出")
            choice = input("请选择：").strip()
            if choice == "1":
                query_books(conn)
            elif choice == "0":
                break
            else:
                print("请输入有效的菜单编号。")


if __name__ == "__main__":
    main()

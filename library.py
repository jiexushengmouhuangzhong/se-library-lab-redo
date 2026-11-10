"""教学用图书借阅系统：Python标准库和SQLite，无需安装第三方包。"""

from pathlib import Path
import sqlite3

DB_PATH = Path(__file__).with_name("library.db")


def init_database(conn):
    conn.execute("""CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY, title TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT '可借'
            CHECK(status IN ('可借', '已借出')))""")
    conn.execute("""CREATE TABLE IF NOT EXISTS loans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        book_id INTEGER NOT NULL REFERENCES books(id),
        borrower TEXT NOT NULL, borrowed_at TEXT NOT NULL,
        returned_at TEXT)""")
    conn.execute("""CREATE UNIQUE INDEX IF NOT EXISTS one_active_loan
        ON loans(book_id) WHERE returned_at IS NULL""")
    conn.executemany(
        "INSERT OR IGNORE INTO books(id, title) VALUES (?, ?)",
        [(1, "软件工程导论"), (2, "Python程序设计"), (3, "数据库系统原理")],
    )
    conn.commit()


def query_books(conn):
    rows = conn.execute("SELECT id, title, status FROM books ORDER BY id").fetchall()
    for book_id, title, status in rows:
        print(f"{book_id} | {title} | {status}")
    return rows


def borrow_book(conn, book_id, borrower):
    borrower = borrower.strip()
    if not borrower:
        return "借阅人不能为空。"
    with conn:
        book = conn.execute("SELECT status FROM books WHERE id = ?", (book_id,)).fetchone()
        if book is None:
            return "图书不存在。"
        if book[0] != "可借":
            return "图书已借出。"
        conn.execute("UPDATE books SET status = '已借出' WHERE id = ?", (book_id,))
        conn.execute("""INSERT INTO loans(book_id, borrower, borrowed_at)
            VALUES (?, ?, datetime('now', 'localtime'))""", (book_id, borrower))
    return "借书成功。"


def return_book(conn, book_id, borrower):
    borrower = borrower.strip()
    if not borrower:
        return "借阅人不能为空。"
    with conn:
        book = conn.execute("SELECT status FROM books WHERE id = ?", (book_id,)).fetchone()
        if book is None:
            return "图书不存在。"
        loan = conn.execute("""SELECT id, borrower FROM loans
            WHERE book_id = ? AND returned_at IS NULL""", (book_id,)).fetchone()
        if loan is None:
            return "该图书没有未归还记录。"
        if loan[1] != borrower:
            return "借阅人与记录不符。"
        conn.execute("""UPDATE loans SET returned_at = datetime('now', 'localtime')
            WHERE id = ?""", (loan[0],))
        conn.execute("UPDATE books SET status = '可借' WHERE id = ?", (book_id,))
    return "还书成功。"


def query_loans(conn):
    rows = conn.execute("""SELECT loans.id, books.title, loans.borrower,
        loans.borrowed_at, COALESCE(loans.returned_at, '未归还')
        FROM loans JOIN books ON loans.book_id = books.id
        ORDER BY loans.id""").fetchall()
    if not rows:
        print("暂无借阅记录。")
    for row in rows:
        print(" | ".join(str(value) for value in row))
    return rows


def main():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        init_database(conn)
        while True:
            print("\n图书借阅系统：1 查询图书；2 借书；3 还书；4 借阅记录；0 退出")
            choice = input("请选择：").strip()
            if choice == "0":
                break
            if choice == "1":
                query_books(conn)
            elif choice == "4":
                query_loans(conn)
            elif choice in ("2", "3"):
                try:
                    book_id = int(input("图书编号：").strip())
                except ValueError:
                    print("图书编号必须是整数。")
                    continue
                borrower = input("借阅人姓名：")
                action = borrow_book if choice == "2" else return_book
                print(action(conn, book_id, borrower))
            else:
                print("请输入有效的菜单编号。")


if __name__ == "__main__":
    main()

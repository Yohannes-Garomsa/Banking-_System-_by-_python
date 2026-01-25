from account_repository import get_connection


def list_accounts():
    conn = get_connection()
    if not conn:
        print("No database connection. Check credentials and dependencies.")
        return
    cursor = conn.cursor()
    cursor.execute("SELECT id, owner, balance FROM accounts")
    rows = cursor.fetchall()
    if not rows:
        print("No accounts found in the database.")
    else:
        for r in rows:
            print(f"id: {r[0]} | owner: {r[1]} | balance: {r[2]}")
    cursor.close()
    conn.close()


if __name__ == "__main__":
    list_accounts()

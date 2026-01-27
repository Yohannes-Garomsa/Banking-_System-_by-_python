import mysql.connector


def connect_to_db():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="root",
            database="bank_system",
        )
        return connection
    except mysql.connector.Error as err:
        print(f"error: {err}")
        return None


def setup_database():
    conn = connect_to_db()
    if conn:
        cursor = conn.cursor()
        # Create table if not exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS accounts (
                id INT AUTO_INCREMENT PRIMARY KEY,
                owner VARCHAR(100) NOT NULL,
                balance DECIMAL(15, 2) DEFAULT 0.00
            )
        """)
        conn.commit()
        print("✅ Database & Table ready!")
        cursor.close()
        conn.close()


if __name__ == "__main__":
    setup_database()
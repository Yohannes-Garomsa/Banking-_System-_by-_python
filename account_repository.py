def get_connection():
    try:
        import mysql.connector
    except ImportError:
        raise ImportError("mysql-connector-python is not installed. Run 'pip install mysql-connector-python'.")

    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="bank_system",
    )
def save_account(owner,balance):
    conn =get_connection()
    cursor=conn.cursor()

    query ="""INSERT INTO accounts (owner, balance) VALUES (%s, %s)"""
    cursor.execute(query, (owner, balance))
    conn.commit()
    cursor.close()
    conn.close()

def get_account(owner):
    conn=get_connection()
    cursor=conn.cursor()
    
    cursor.execute("SELECT owner FROM accounts WHERE owner=%s", (owner,))
    
    account =cursor.fetchone()
    
    cursor.close()
    conn.close()
    return account


def update_balance(owner,balance):
    conn=get_connection()
    cursor =conn.cursor()
    
    cursor.execute("UPDATE accounts SET balance=%s WHERE owner=%s",(balance,owner))
    
    conn.commit()
    cursor.close()
    conn.close()
    
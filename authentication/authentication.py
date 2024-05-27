def authenticate_admin(conn, username, password):
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM Librarian WHERE Username=? AND Password=?
    ''', (username, password))
    return cursor.fetchone()

def authenticate_user(conn, library_card_number):
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM User WHERE LibraryCardNumber=?
    ''', (library_card_number,))
    return cursor.fetchone()

def register_user(conn, full_name):
    import uuid
    from datetime import datetime
    from utils.utils import add_one_year  # Correct import for add_one_year

    card_number = str(uuid.uuid4())
    valid_until = add_one_year(datetime.today()).strftime('%Y-%m-%d')

    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO User (LibraryCardNumber, FullName, ValidUntil)
        VALUES (?, ?, ?)
    ''', (card_number, full_name, valid_until))
    conn.commit()
    return card_number

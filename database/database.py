import sqlite3

def create_tables(conn):
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS User (
            UserID INTEGER PRIMARY KEY AUTOINCREMENT,
            LibraryCardNumber TEXT UNIQUE NOT NULL,
            FullName TEXT NOT NULL,
            ValidUntil DATE NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Librarian (
            LibrarianID INTEGER PRIMARY KEY AUTOINCREMENT,
            Username TEXT UNIQUE NOT NULL,
            Password TEXT NOT NULL,
            FullName TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Book (
            BookID INTEGER PRIMARY KEY AUTOINCREMENT,
            Title TEXT,
            Author TEXT,
            Year INTEGER,
            Genre TEXT,
            ISBN TEXT NOT NULL,
            Count INTEGER DEFAULT 1
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Rental (
            RentalID INTEGER PRIMARY KEY AUTOINCREMENT,
            UserID INTEGER NOT NULL,
            BookID INTEGER NOT NULL,
            RentalDate DATE NOT NULL DEFAULT (date('now')),
            ReturnDate DATE NOT NULL,
            Returned BOOLEAN DEFAULT 0,
            Quantity INTEGER NOT NULL DEFAULT 1,
            FOREIGN KEY (UserID) REFERENCES User (UserID),
            FOREIGN KEY (BookID) REFERENCES Book (BookID)
        )
    ''')
    conn.commit()

def insert_sample_data(conn):
    cursor = conn.cursor()
    # Check if sample data for Librarian table already exists
    cursor.execute("SELECT COUNT(*) FROM Librarian")
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
            INSERT INTO Librarian (Username, Password, FullName) VALUES
            ('admin1', 'password1', 'Librarian One'),
            ('admin2', 'password2', 'Librarian Two')
        ''')

    # Check if sample data for User table already exists
    cursor.execute("SELECT COUNT(*) FROM User")
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
            INSERT INTO User (LibraryCardNumber, FullName, ValidUntil) VALUES
            ('CARD12345', 'User One', '2025-12-31'),
            ('CARD67890', 'User Two', '2024-12-31')
        ''')

    # Check if sample data for Book table already exists
    cursor.execute("SELECT COUNT(*) FROM Book")
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
            INSERT INTO Book (Title, Author, Year, Genre, ISBN, Count) VALUES
            ('Book One', 'Author One', 2001, 'Fiction', 'ISBN001', 5),
            ('Book Two', 'Author Two', 2015, 'Non-Fiction', 'ISBN002', 2)
        ''')

    # Check if sample data for Rental table already exists
    cursor.execute("SELECT COUNT(*) FROM Rental")
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
            INSERT INTO Rental (UserID, BookID, RentalDate, ReturnDate, Returned, Quantity) VALUES
            (1, 1, '2024-01-01', '2024-02-01', 0, 1),
            (2, 2, '2024-03-01', '2024-04-01', 0, 1)
        ''')

    conn.commit()
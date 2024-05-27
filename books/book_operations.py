from tabulate import tabulate

def add_book(conn, title, author, year, genre, isbn, count):
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO Book (Title, Author, Year, Genre, ISBN, Count)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (title, author, year, genre, isbn, count))
    conn.commit()

def delete_book_by_isbn(conn, book_isbn, book_count_to_delete=None):
    cursor = conn.cursor()
    
    # Count the number of books available with the given ISBN
    cursor.execute('''
        SELECT SUM(Count) FROM Book WHERE ISBN=?
    ''', (book_isbn,))
    total_books = cursor.fetchone()[0]

    if book_count_to_delete is None or book_count_to_delete == '' or book_count_to_delete >= total_books:
        # Delete all books with the given ISBN if the input is empty or greater than available books
        cursor.execute('''
            DELETE FROM Book WHERE ISBN=?
        ''', (book_isbn,))
    else:
        # Delete a specific number of books with the given ISBN
        books_to_delete = book_count_to_delete
        while books_to_delete > 0:
            cursor.execute('''
                SELECT BookID, Count FROM Book WHERE ISBN=? LIMIT 1
            ''', (book_isbn,))
            book = cursor.fetchone()
            if book is None:
                break
            book_id, book_count = book
            if book_count > books_to_delete:
                cursor.execute('''
                    UPDATE Book SET Count = Count - ? WHERE BookID = ?
                ''', (books_to_delete, book_id))
                books_to_delete = 0
            else:
                cursor.execute('''
                    DELETE FROM Book WHERE BookID = ?
                ''', (book_id,))
                books_to_delete -= book_count
    
    conn.commit()

def delete_book_by_year(conn, year):
    cursor = conn.cursor()
    cursor.execute('''
        DELETE FROM Book WHERE Year <= ?
    ''', (year,))
    conn.commit()

def list_available_books(conn):
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM Book WHERE Count > 0
    ''')
    rows = cursor.fetchall()
    print(tabulate(rows, headers=[description[0] for description in cursor.description], tablefmt='grid'))

def search_books(conn, search_term):
    cursor = conn.cursor()
    query = '''
        SELECT * FROM Book
        WHERE Title LIKE '%' || ? || '%'
           OR Author LIKE '%' || ? || '%';
    '''
    cursor.execute(query, (search_term, search_term))
    rows = cursor.fetchall()
    print(tabulate(rows, headers=[description[0] for description in cursor.description], tablefmt='grid'))

def top_books_by_genre_library(conn):
    cursor = conn.cursor()
    query = '''
        SELECT Genre, SUM(Count) as TotalBooks
        FROM Book
        GROUP BY Genre
        ORDER BY TotalBooks DESC
        LIMIT 5;
    '''
    cursor.execute(query)
    rows = cursor.fetchall()
    print(tabulate(rows, headers=[description[0] for description in cursor.description], tablefmt='grid'))

def top_books_by_genre_rented(conn):
    cursor = conn.cursor()
    query = '''
        SELECT b.Genre, SUM(r.Quantity) as TotalRented
        FROM Rental r
        JOIN Book b ON r.BookID = b.BookID
        GROUP BY b.Genre
        ORDER BY TotalRented DESC
        LIMIT 5;
    '''
    cursor.execute(query)
    rows = cursor.fetchall()
    print(tabulate(rows, headers=[description[0] for description in cursor.description], tablefmt='grid'))
from datetime import datetime
from utils.utils import add_one_month  # Correct import for add_one_month
from tabulate import tabulate
from datetime import date, datetime, timedelta

def check_rental_status(conn, library_card_number):
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT Rental.RentalID, Rental.BookID, Rental.Quantity, Rental.ReturnDate
        FROM Rental
        JOIN User ON Rental.UserID = User.UserID
        WHERE User.LibraryCardNumber = ? AND Rental.Returned = 0
        ORDER BY Rental.ReturnDate ASC;
    ''', (library_card_number,))
    
    rentals = cursor.fetchall()
    
    today = date.today()
    
    for rental in rentals:
        rental_id, book_id, quantity, return_date = rental
        return_date = date.fromisoformat(return_date)
        if return_date < today:
            return True  # There is an overdue book
    
    return False  # No overdue books

def rent_book(conn, user_id, book_isbn_to_rent, return_date, quantity):
    overdue = check_rental_status(conn, user_id)
    
    if overdue:
        print("You can't rent a new book before you return all overdue books.")
    else:
        cursor = conn.cursor()
        # If return_date is empty, set it to one month from today
        if not return_date:
            return_date = add_one_month(datetime.today()).strftime('%Y-%m-%d')

        if quantity == '':
            quantity = 1
        else:
            quantity = int(quantity)
        
        # Check if enough books are available
        cursor.execute('''
            SELECT BookID, Count FROM Book WHERE ISBN = ?
        ''', (book_isbn_to_rent,))
        book = cursor.fetchone()
        
        if book and book[1] >= quantity:
            try:
                # Insert rental record
                cursor.execute('''
                    INSERT INTO Rental (UserID, BookID, ReturnDate, Quantity)
                    VALUES (?, ?, ?, ?)
                ''', (user_id, book[0], return_date, quantity))

                # Update book count
                cursor.execute('''
                    UPDATE Book SET Count = Count - ? WHERE BookID = ?
                ''', (quantity, book[0]))
                conn.commit()
                print("Book(s) rented successfully.")
            except Exception as e:
                conn.rollback()
                print("Error during renting book:", e)
        else:
            print("Not enough books available for the requested ISBN.")

def return_book(conn, library_card_number, book_isbn, return_quantity=None):
    cursor = conn.cursor()
    
    # First, get the user's rental IDs using the provided ISBN and library card number, sorted by return date
    cursor.execute('''
        SELECT Rental.RentalID, Rental.BookID, Rental.Quantity, Rental.ReturnDate
        FROM Rental
        JOIN User ON Rental.UserID = User.UserID
        JOIN Book ON Rental.BookID = Book.BookID
        WHERE User.LibraryCardNumber = ? AND Book.ISBN = ? AND Rental.Returned = 0
        ORDER BY Rental.ReturnDate ASC
    ''', (library_card_number, book_isbn))
    rentals = cursor.fetchall()
    
    if not rentals:
        print("Error: No active rental found for this ISBN and user.")
        return

    if return_quantity is None:
        # Calculate the total quantity to return
        return_quantity = sum(rental[2] for rental in rentals)
    
    remaining_quantity_to_return = return_quantity
    
    for rental in rentals:
        rental_id, book_id, quantity, return_date = rental
        
        if remaining_quantity_to_return <= 0:
            break

        if remaining_quantity_to_return >= quantity:
            # Mark the rental as returned if returning all books in this rental
            cursor.execute('''
                UPDATE Rental SET Returned = 1, Quantity = 0 WHERE RentalID = ?
            ''', (rental_id,))
            # print(f"Marked rental ID {rental_id} as returned.")
            remaining_quantity_to_return -= quantity
        else:
            # Update the quantity in the rental record
            cursor.execute('''
                UPDATE Rental SET Quantity = Quantity - ? WHERE RentalID = ?
            ''', (remaining_quantity_to_return, rental_id))
            print(f"Decreased rental ID {rental_id} quantity by {remaining_quantity_to_return}. Remaining quantity: {quantity - remaining_quantity_to_return}")
            remaining_quantity_to_return = 0
        
        # Update the book count
        cursor.execute('''
            UPDATE Book SET Count = Count + ? WHERE BookID = ?
        ''', (quantity, book_id))

    if remaining_quantity_to_return > 0:
        print(f"Warning: Not all requested quantities were returned. {remaining_quantity_to_return} books could not be returned because the rentals were not found.")
    
    conn.commit()
    print("Book(s) returned successfully.")

def list_overdue_books(conn):
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM Rental
        WHERE ReturnDate < ? AND Returned = 0
    ''', (date.today(),))
    rows = cursor.fetchall()
    print(tabulate(rows, headers=[description[0] for description in cursor.description], tablefmt='grid'))

def list_total_overdue_books(conn):
    cursor = conn.cursor()
    cursor.execute('''
        SELECT SUM(Quantity) as TotalOverdue
        FROM Rental
        WHERE ReturnDate < ? AND Returned = 0
    ''', (date.today(),))
    row = cursor.fetchone()
    print(tabulate([row], headers=['TotalOverdue'], tablefmt='grid'))

def check_rental_status(conn, library_card_number):
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT Rental.RentalID, Rental.BookID, Rental.Quantity, Rental.ReturnDate
        FROM Rental
        JOIN User ON Rental.UserID = User.UserID
        WHERE User.LibraryCardNumber = ? AND Rental.Returned = 0
        ORDER BY Rental.ReturnDate ASC;
    ''', (library_card_number,))
    
    rentals = cursor.fetchall()
    
    today = date.today()
    
    for rental in rentals:
        rental_id, book_id, quantity, return_date = rental
        return_date = date.fromisoformat(return_date)
        if return_date < today:
            return True  # There is an overdue book
    
    return False  # No overdue books

def return_available_books(conn, isbn):
    cursor = conn.cursor()
    cursor.execute('''
        SELECT Count FROM Book WHERE ISBN = ?
    ''', (isbn,))
    book_count = cursor.fetchone()
    if book_count:
        return book_count[0]
    return 0

def list_rented_books(conn, library_card):
    cursor = conn.cursor()
    cursor.execute('''
        SELECT 
            Book.BookID,
            Book.Title,
            Book.Author,
            Book.Year,
            Book.Genre,
            Book.ISBN,
            Rental.RentalDate,
            Rental.ReturnDate,
            Rental.Quantity,
            Rental.Returned
        FROM 
            User
        JOIN 
            Rental ON User.UserID = Rental.UserID
        JOIN 
            Book ON Rental.BookID = Book.BookID
        WHERE 
            User.LibraryCardNumber = ? AND Rental.Returned = 0
    ''', (library_card,))
    rows = cursor.fetchall()
    print(tabulate(rows, headers=[description[0] for description in cursor.description], tablefmt='grid'))
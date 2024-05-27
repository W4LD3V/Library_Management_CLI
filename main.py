import sqlite3
from getpass import getpass
from authentication.authentication import authenticate_admin, authenticate_user, register_user
from books.book_operations import add_book, delete_book_by_isbn, delete_book_by_year, list_available_books, search_books, top_books_by_genre_library, top_books_by_genre_rented
from rentals.rental_operations import rent_book, return_book, list_rented_books, list_overdue_books, list_total_overdue_books, check_rental_status, return_available_books
from utils.utils import add_one_month
from database.database import create_tables, insert_sample_data
from datetime import date, datetime

def main():
    conn = sqlite3.connect('library.db')
    create_tables(conn)
    insert_sample_data(conn)
    
    while True:
        print("\nWelcome to the Library Management System\n")
        print("1. Login as Admin")
        print("2. Login as User")
        print("3. Register as User")
        print("4. See top charts")
        print("5. Exit")
        choice = input("Enter your choice: ")

        if choice == '1':
            print()
            username = input("Enter username: ")
            password = getpass("Enter password: ")
            admin = authenticate_admin(conn, username, password)
            if admin:
                print("\nLogin successful!\n")
                while True:
                    print("\nAdmin Menu\n")
                    print("1. Add Book")
                    print("2. Delete Book")
                    print("3. List Available Books")
                    print("4. List Overdue Books")
                    print("5. Logout")
                    admin_choice = input("Enter your choice: ")

                    if admin_choice == '1':
                        while True:
                            print("\nEnter book details (type 'exit' to quit):")
                            title = input("Enter book title [optional]: ")
                            if title.lower() == 'exit':
                                break
                            author = input("Enter author [optional]: ")
                            if author.lower() == 'exit':
                                break
                            
                            year_input = input("Enter year [optional]: ")
                            if year_input.lower() == 'exit':
                                break
                            year = int(year_input) if year_input else None

                            genre = input("Enter genre [optional]: ")
                            if genre.lower() == 'exit':
                                break

                            while True:
                                isbn = input("Enter ISBN: ")
                                if isbn.lower() == 'exit':
                                    break
                                if isbn.strip() == "":
                                    print("ISBN cannot be empty. Please enter a valid ISBN.")
                                else:
                                    break
                            if isbn.lower() == 'exit':
                                break

                            count_input = input("Enter count (default is 1 [optional]: ")
                            if count_input.lower() == 'exit':
                                break
                            count = int(count_input) if count_input else 1

                            add_book(conn, title, author, year, genre, isbn, count)
                            print("Book added successfully.")
                            break

                    elif admin_choice == '2':
                        print("\nDelete Menu\n")
                        while True:
                            print("1. Remove book by ISBN")
                            print("2. Remove all books by year")
                            print("3. Go back")
                            delete_choice = input("Enter your choice: ")
                            if delete_choice == '1':
                                while True:
                                    book_isbn = input("Enter book ISBN to remove (type 'exit' to quit): ")
                                    if book_isbn.lower() == 'exit':
                                        break
                                    if book_isbn.strip() == "":
                                        print("ISBN cannot be empty. Please enter a valid ISBN.")
                                    else:
                                        break
                                if book_isbn.lower() == 'exit':
                                    break
                                book_count_input = input("Enter how many books you want to delete, leave input empty if you want to delete all: ")
                                book_count_to_delete = int(book_count_input) if book_count_input else None
                                delete_book_by_isbn(conn, book_isbn, book_count_to_delete)
                                print("Book/s deleted successfully.")
                                break
                            elif delete_choice == '2':
                                while True:
                                    year_input = input("Enter year of books to delete (type 'exit' to quit): ")
                                    if year_input.lower() == 'exit':
                                        break
                                    if year_input.strip() == "":
                                        print("Year cannot be empty. Please enter a valid year.")
                                    else:
                                        try:
                                            year = int(year_input)
                                            delete_book_by_year(conn, year)
                                            print("Book/s deleted successfully.")
                                            break
                                        except ValueError:
                                            print("Invalid year. Please enter a valid year.")
                                if year_input.lower() == 'exit':
                                    break
                            elif delete_choice == '3':
                                break
                            else:
                                print("Invalid choice. Please try again.")

                    elif admin_choice == '3':
                        print()
                        list_available_books(conn)
                    elif admin_choice == '4':
                        print()
                        list_total_overdue_books(conn)
                        list_overdue_books(conn)
                    elif admin_choice == '5':
                        break
                    else:
                        print("Invalid choice. Please try again.")
            else:
                print("\nInvalid username or password.\n")
        
        elif choice == '2':
            while True:
                print()
                library_card_number = input("Enter your library card number: ")
                user = authenticate_user(conn, library_card_number)
                if user:
                    print("\nLogin successful!\n")
                    while True:
                        print("\nUser Menu\n")
                        print("1. Rent Book")
                        print("2. Return Book")
                        print("3. List Available Books")
                        print("4. List Rented Books")
                        print("5. Search books")
                        print("6. Logout")
                        user_choice = input("Enter your choice: ")

                        if user_choice == '1':
                            print()
                            while True:
                                overdue = check_rental_status(conn, library_card_number)
                                if overdue:
                                    print("You can't rent a new book before you return all overdue books.")
                                    break

                                book_isbn_to_rent = input("Enter book ISBN to rent (type 'exit' to quit): ")  
                                if book_isbn_to_rent.lower() == 'exit':
                                    break
                                
                                available_books = return_available_books(conn, book_isbn_to_rent)
                                if available_books == 0:
                                    print("The book doesn't exist in the library, please try a different ISBN number (type 'exit' to quit)")
                                    continue

                                while True:
                                    return_date = input("Enter return date (YYYY-MM-DD), (default is 1 month): ")
                                    if not return_date:
                                        return_date = add_one_month(datetime.today()).strftime('%Y-%m-%d')
                                    
                                    try:
                                        return_formatted_date = date.fromisoformat(return_date)
                                        today = date.today()
                                        if return_formatted_date < today:
                                            print(f"Return date cannot be less than today: {today}")
                                        else:
                                            break
                                    except ValueError:
                                        print("Invalid date format. Please enter a valid date in YYYY-MM-DD format.")
                                
                                while True:
                                    quantity_input = input(f"Enter quantity of books to rent, currently there are {available_books} book(s) in the library, (default is 1, limit is <= 3, type 'exit' to quit): ")
                                    if quantity_input.lower() == 'exit':
                                        break
                                    try:
                                        quantity = int(quantity_input) if quantity_input else 1
                                        if quantity > 3:
                                            print("Cannot rent more than 3 of the same book")
                                        elif quantity > available_books:
                                            print(f"Cannot rent more books than are available in the library ({available_books})")
                                        else:
                                            rent_book(conn, user[0], book_isbn_to_rent, return_date, quantity)
                                            break
                                    except ValueError:
                                        print("Invalid quantity. Please enter a valid number.")
                                break  # Break out of the rent book loop
                                        
                        elif user_choice == '2':
                            print()
                            book_isbn_to_return = input("Enter book ISBN to return: ")
                            return_quantity_input = input("Enter quantity of books to return (leave empty to return all): ")
                            try:
                                return_quantity = int(return_quantity_input) if return_quantity_input else None
                                return_book(conn, library_card_number, book_isbn_to_return, return_quantity)
                            except ValueError:
                                print("Invalid quantity. Please enter a valid number.")
                        elif user_choice == '3':
                            print()
                            list_available_books(conn)
                        elif user_choice == '4':
                            print()
                            list_rented_books(conn, library_card_number)
                        elif user_choice == '5':
                            search_term = input("Enter either the name of the book or author you want to look up: ")
                            search_books(conn, search_term)  # This will print the results directly
                        elif user_choice == '6':
                            break
                        else:
                            print("Invalid choice. Please try again.")
                    break  # Break out of the library card number prompt loop after logging out
                else:
                    print("Invalid library card number. Please try again.")
        
        elif choice == '3':
            user_registration_name = input("Please enter your full name in order to register: ")
            while True:
                registration_result = register_user(conn, user_registration_name)
                if not registration_result:
                    print(f"Registration error, please try again (type 'exit' to quit)")
                else:
                    print(f"Successful registration! Please save your card number, and don't let anyone else use it: {registration_result}")
                    break
        elif choice == '4':
            print("\nTop Charts Menu\n")
            while True:
                print("1. Top Library Books ranked by Genre:")
                print("2. Top Rented Books ranked by Genre:")
                print("3. Go back")
                user_choice = input("Enter your choice: ")
                if user_choice == '1':
                    top_books_by_genre_library(conn)
                elif user_choice == '2':
                    top_books_by_genre_rented(conn)
                elif user_choice == '3':
                    break
                else:
                    print("Invalid choice. Please try again.")
        elif choice == '5':
            break
        else:
            print("Invalid choice. Please try again.")

    conn.close()

if __name__ == '__main__':
    main()

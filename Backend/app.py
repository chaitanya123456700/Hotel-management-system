from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
import os
import datetime 
from datetime import datetime
import secrets # For generating a secure secret key

# Initialize the Flask application
app = Flask(__name__)
# Generate a strong, random secret key for session management and flash messages.
# IMPORTANT: In a production environment, this key should be loaded from an
# environment variable or a configuration file, NOT hardcoded.
app.secret_key = secrets.token_hex(16) # Generates a 32-character hexadecimal string

# Define the path for the SQLite database file
DATABASE = 'hotel_management.db'

# Function to get a database connection
def get_db_connection():
    """
    Establishes a connection to the SQLite database.
    If the database file does not exist, it will be created.
    Configures row_factory to allow accessing columns by name.
    """
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # This allows accessing columns by name (e.g., row['column_name'])
    return conn

# Function to initialize the database tables
def init_db():
    """
    Initializes the database by creating the 'bookings', 'food_orders',
    and 'users' tables if they do not already exist.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create bookings table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            check_in_date TEXT NOT NULL,
            check_out_date TEXT NOT NULL,
            adults INTEGER NOT NULL,
            children INTEGER NOT NULL,
            rooms INTEGER NOT NULL,
            room_type TEXT NOT NULL,
            booking_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Create food_orders table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS food_orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT NOT NULL,
            customer_number TEXT NOT NULL,
            food_item TEXT NOT NULL,
            additional_food TEXT,
            quantity INTEGER NOT NULL,
            delivery_time TEXT,
            delivery_address TEXT NOT NULL,
            message TEXT,
            order_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Create users table for registration and login
    # username and email are set to UNIQUE to prevent duplicate registrations
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL, -- In a real application, store hashed passwords (e.g., using bcrypt)
            registration_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()  # Save changes to the database
    conn.close()   # Close the connection
    print("Database tables created or already exist.")

# Route for the home page (your main hotel website)
@app.route('/')
def index():
    """Renders the main index page."""
    # Pass the logged-in username to the template if available
    return render_template('index.html', username=session.get('username'))

# Route for the booking page
@app.route('/booking')
def booking():
    """Renders the booking form page."""
    return render_template('booking.html')

# Route for the sign-in and sign-up page

# Route for the restaurant main page
@app.route('/restaurant')
def restaurant():
    """Renders the main restaurant page (uiproject.html)."""
    return render_template('uiproject.html')

# Routes for specific cuisine menus
@app.route('/indian.html')
def indian_menu():
    """Renders the Indian cuisine menu page."""
    return render_template('indian.html')

@app.route('/japanese.html')
def japanese_menu():
    """Renders the Japanese cuisine menu page."""
    return render_template('japanese.html')

@app.route('/thai.html')
def thai_menu():
    """Renders the Thai cuisine menu page."""
    return render_template('thai.html')

@app.route('/french.html')
def french_menu():
    """Renders the French cuisine menu page."""
    return render_template('french.html')

@app.route('/uiproject')
def uiproject_page():
    """Renders the main restaurant page (alias for /restaurant)."""
    return render_template('uiproject.html')

@app.route('/order.html')
def order_page():
    """Renders the food order form page."""
    return render_template('order.html')

# Route for menu.html
@app.route('/menu.html')
def menu_page():
    """Renders the general menu page."""
    return render_template('menu.html')

@app.route('/italian.html')
def italian_menu():
    """Renders the Italian cuisine menu page."""
    return render_template('italian.html')

# Route for handling the "Check Availability" form submission and storing booking data
@app.route('/check_availability', methods=['POST'])
def check_availability():
    """
    Handles the submission of the booking form.
    Retrieves form data, validates it, and inserts it into the 'bookings' table.
    Flashes success or error messages and redirects.
    """
    try:
        # Retrieve form data using the correct 'name' attributes from booking.html
        name = request.form.get('name')
        email = request.form.get('email')
        check_in_date = request.form.get('check_in_date')
        check_out_date = request.form.get('check_out_date')
        adults = request.form.get('adults')
        children = request.form.get('children')
        rooms = request.form.get('rooms')
        room_type = request.form.get('room_type')

        # Basic validation for all required fields
        if not all([name, email, check_in_date, check_out_date, adults, children, rooms, room_type]):
            flash('All booking fields are required! Please fill out the entire form.', 'error')
            return redirect(url_for('booking'))

        # Convert numerical fields to integers
        adults = int(adults)
        children = int(children)
        rooms = int(rooms)

        conn = get_db_connection()
        cursor = conn.cursor()

        # Insert booking data into the database
        cursor.execute(
            "INSERT INTO bookings (name, email, check_in_date, check_out_date, adults, children, rooms, room_type) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (name, email, check_in_date, check_out_date, adults, children, rooms, room_type)
        )
        conn.commit()
        conn.close()

        flash('Booking details saved successfully!', 'success')
        print(f"Booking saved: Name: {name}, Email: {email}, Check-in: {check_in_date}, Check-out: {check_out_date}, Adults: {adults}, Children: {children}, Rooms: {rooms}, Room Type: {room_type}")
        return redirect(url_for('index')) # Redirect to the home page after successful booking
    except ValueError:
        # Catches errors if conversion to int fails (e.g., non-numeric input for adults, children, rooms)
        flash('Invalid input for adults, children, or rooms. Please enter numbers.', 'error')
        return redirect(url_for('booking'))
    except Exception as e:
        # Catches any other unexpected errors during the booking process
        flash(f'An unexpected error occurred while saving your booking: {e}', 'error')
        print(f"Error saving booking: {e}") # Print the actual error for server-side debugging
        return redirect(url_for('booking'))

# Route to handle food order submission and store data
@app.route('/place_food_order', methods=['POST'])
def place_food_order():
    """
    Handles the submission of the food order form.
    Retrieves form data, validates it, and inserts it into the 'food_orders' table.
    Flashes success or error messages and redirects.
    """
    try:
        # Retrieve form data using the 'name' attributes from order.html
        customer_name = request.form.get('customer_name')
        customer_number = request.form.get('customer_number')
        food_item = request.form.get('food_item')
        additional_food = request.form.get('additional_food') # Optional field
        quantity = request.form.get('quantity')
        delivery_time = request.form.get('delivery_time')     # Optional field
        delivery_address = request.form.get('delivery_address')
        message = request.form.get('message')                 # Optional field

        # Basic validation for required fields
        if not all([customer_name, customer_number, food_item, quantity, delivery_address]):
            flash('Required order fields are missing! Please fill in Name, Number, Order, Quantity, and Address.', 'error')
            return redirect(url_for('order_page'))

        # Convert quantity to integer. This needs to be inside a try-except block
        # because request.form.get() returns a string or None, and int(None) fails.
        try:
            quantity = int(quantity)
        except (ValueError, TypeError): # Catch both ValueError for bad string and TypeError for None
            flash('Quantity must be a valid number.', 'error')
            return redirect(url_for('order_page'))

        conn = get_db_connection()
        cursor = conn.cursor()

        # Insert food order data into the database
        cursor.execute(
            "INSERT INTO food_orders (customer_name, customer_number, food_item, additional_food, quantity, delivery_time, delivery_address, message) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (customer_name, customer_number, food_item, additional_food, quantity, delivery_time, delivery_address, message)
        )
        conn.commit() # Commit the transaction to save changes
        conn.close()  # Close the database connection

        flash('Food order placed successfully!', 'success')
        print(f"Food order saved: Name: {customer_name}, Number: {customer_number}, Item: {food_item}, Quantity: {quantity}, Address: {delivery_address}")
        return redirect(url_for('index')) # Redirect to home or an order confirmation page
    except Exception as e:
        # Catch any other unexpected errors during the order placement process
        flash(f'An unexpected error occurred while placing your order: {e}', 'error')
        print(f"Error placing food order: {e}") # This will print the actual error to your console
        return redirect(url_for('order_page'))
@app.route('/sign_in_and_up')
def sign_in_and_up():
    # Pass datetime to the template
    return render_template('signinandup.html', datetime=datetime)

# Route to handle user registration
@app.route('/register_details', methods=['POST'])
def register_details():
    """
    Handles new user registration.
    Retrieves username, email, and password from the form,
    validates them, and stores them in the 'users' table.
    Flashes messages and redirects.
    """
    username = request.form.get('newUsername')
    email = request.form.get('newEmail')
    password = request.form.get('newPassword')

    if not all([username, email, password]):
        flash('All registration fields are required!', 'error')
        return redirect(url_for('sign_in_and_up'))

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Check if username or email already exists
        cursor.execute("SELECT id FROM users WHERE username = ? OR email = ?", (username, email))
        existing_user = cursor.fetchone()
        if existing_user:
            flash('Username or Email already exists. Please choose a different one.', 'error')
            return redirect(url_for('sign_in_and_up'))

        # Insert new user into the database
        # In a real application, you would hash the password before storing it.
        cursor.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                       (username, email, password))
        conn.commit()
        flash('Registration successful! Please log in.', 'success')
        print(f"User registered: Username: {username}, Email: {email}")
        return redirect(url_for('sign_in_and_up')) # Redirect to login page
    except sqlite3.IntegrityError as e:
        # This catches unique constraint violations if, for some reason, the check above missed it
        flash('A user with that username or email already exists.', 'error')
        print(f"Integrity error during registration: {e}")
        return redirect(url_for('sign_in_and_up'))
    except Exception as e:
        flash(f'An error occurred during registration: {e}', 'error')
        print(f"Error during registration: {e}")
        return redirect(url_for('sign_in_and_up'))
    finally:
        conn.close()

# Route to handle user login
@app.route('/login_details', methods=['POST'])
def login_details():
    """
    Handles user login.
    Retrieves username/email and password from the form,
    authenticates against the 'users' table, and manages session.
    Flashes messages and redirects.
    """
    username_or_email = request.form.get('username') # This input can be either username or email
    password = request.form.get('password')

    if not all([username_or_email, password]):
        flash('Both username/email and password are required!', 'error')
        return redirect(url_for('sign_in_and_up'))

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Try to find a user matching either username or email and the provided password
        cursor.execute("SELECT * FROM users WHERE (username = ? OR email = ?) AND password = ?",
                       (username_or_email, username_or_email, password))
        user = cursor.fetchone()

        if user:
            # If user found, set session variables
            session['logged_in'] = True
            session['username'] = user['username'] # Store the actual username in session
            flash(f'Welcome, {user["username"]}! You have been successfully logged in.', 'success')
            print(f"User logged in: {user['username']}")
            return redirect(url_for('index')) # Redirect to the home page
        else:
            flash('Invalid username/email or password.', 'error')
            print(f"Failed login attempt for: {username_or_email}")
            return redirect(url_for('sign_in_and_up'))
    except Exception as e:
        flash(f'An error occurred during login: {e}', 'error')
        print(f"Error during login: {e}")
        return redirect(url_for('sign_in_and_up'))
    finally:
        conn.close()

# Route to view all bookings
@app.route('/view_bookings')
def view_bookings():
    """Retrieves and displays all stored hotel bookings."""
    conn = get_db_connection()
    # Fetch all bookings, ordered by the most recent first
    bookings = conn.execute('SELECT * FROM bookings ORDER BY booking_time DESC').fetchall()
    conn.close()
    return render_template('view_bookings.html', bookings=bookings)

# Route to view all food orders
@app.route('/view_orders')
def view_orders():
    """Retrieves and displays all stored food orders."""
    conn = get_db_connection()
    # Fetch all food orders, ordered by the most recent first
    orders = conn.execute('SELECT * FROM food_orders ORDER BY order_time DESC').fetchall()
    conn.close()
    return render_template('view_orders.html', orders=orders)

# Route for user logout
@app.route('/logout')
def logout():
    """Logs out the current user by clearing the session."""
    session.pop('logged_in', None)
    session.pop('username', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))


# Main entry point for the application
if __name__ == '__main__':
    # Initialize the database tables when the application starts
    init_db()
    # Run the Flask application in debug mode.
    # IMPORTANT: debug=True should NEVER be used in a production environment.
    app.run(debug=True)

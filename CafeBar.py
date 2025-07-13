import mysql.connector
from datetime import datetime

# MySQL database setup
def create_connection():
    return mysql.connector.connect(
        host="localhost",  
        user="root",       
        password="#rani@20$",  
        database="cafebar"  
    )

# Function to create database and tables
def create_database_and_tables():
    connection = mysql.connector.connect(
        host="localhost",  
        user="root",       
        password="#rani@20$"  
    )
    cursor = connection.cursor()

    # Create the database if it doesn't exist
    cursor.execute("CREATE DATABASE IF NOT EXISTS cafebar")
    cursor.execute("USE cafebar")

    # Create the tables if they don't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Customers (
            customer_id INT AUTO_INCREMENT PRIMARY KEY,
            customer_name VARCHAR(100) NOT NULL,
            contact VARCHAR(15) NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Menu (
            item_id INT AUTO_INCREMENT PRIMARY KEY,
            item_name VARCHAR(100) NOT NULL,
            price DECIMAL(10, 2) NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Orders (
            order_id INT AUTO_INCREMENT PRIMARY KEY,
            customer_id INT,
            item_id INT,
            quantity INT,
            order_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (customer_id) REFERENCES Customers(customer_id),
            FOREIGN KEY (item_id) REFERENCES Menu(item_id)
        )
    """)

    connection.commit()
    cursor.close()
    connection.close()

# Management class for handling operations
class Management:
    def __init__(self):
        self.conn = create_connection()
        self.cursor = self.conn.cursor()
        
    def save_rating(self, rating, feedback):
        # Example: Save the rating and feedback to a file or database
        with open("ratings.txt", "a") as file:
            file.write(f"Rating: {rating}, Feedback: {feedback}\n")

    def add_customer(self, customer):
        # Check if the customer already exists
        self.cursor.execute("SELECT customer_id FROM Customers WHERE customer_name=%s AND contact=%s", (customer.name, customer.contact))
        result = self.cursor.fetchone()
        if result:
            return result[0]
        # Add new customer if not exists
        self.cursor.execute("INSERT INTO Customers (customer_name, contact) VALUES (%s, %s)", (customer.name, customer.contact))
        self.conn.commit()
        return self.cursor.lastrowid

    def place_order(self, customer, items):
        # Get or add the customer
        customer_id = self.add_customer(customer)

        # Insert the new order with the current time (NOW() to timestamp the order)
        for item in items:
            self.cursor.execute("""
                INSERT INTO Orders (customer_id, item_id, quantity, order_time) 
                VALUES (%s, %s, %s, NOW())
            """, (customer_id, item["item_id"], item["quantity"]))
        
        self.conn.commit()

    def view_order(self, customer_name=None, contact=None):
        if customer_name and contact:
            # Get only the latest order for the specific customer based on the order time (DESC)
            self.cursor.execute("""
                SELECT c.customer_name, m.item_name, o.quantity, o.order_time
                FROM Orders o
                JOIN Customers c ON o.customer_id = c.customer_id
                JOIN Menu m ON o.item_id = m.item_id
                WHERE c.customer_name=%s AND c.contact=%s
                ORDER BY o.order_time DESC LIMIT 1
            """, (customer_name.strip().lower(), contact.strip()))
        else:
            # Get all orders sorted by order time (latest first)
            self.cursor.execute("""
                SELECT c.customer_name, m.item_name, o.quantity, o.order_time
                FROM Orders o
                JOIN Customers c ON o.customer_id = c.customer_id
                JOIN Menu m ON o.item_id = m.item_id
                ORDER BY o.order_time DESC
            """)
        
        orders = self.cursor.fetchall()
        order_dict = {}
        for customer_name, item_name, quantity, order_time in orders:
            if customer_name not in order_dict:
                order_dict[customer_name] = []
            order_dict[customer_name].append((item_name, quantity, order_time))
        return order_dict

    def view_menu(self):
        self.cursor.execute("SELECT * FROM Menu")
        return self.cursor.fetchall()

    def delete_customer(self, customer_name, contact):
        self.cursor.execute("SELECT customer_id FROM Customers WHERE customer_name=%s AND contact=%s", (customer_name, contact))
        result = self.cursor.fetchone()
        if result:
            customer_id = result[0]
            self.cursor.execute("DELETE FROM Orders WHERE customer_id=%s", (customer_id,))
            self.cursor.execute("DELETE FROM Customers WHERE customer_id=%s", (customer_id,))
            self.conn.commit()
            return True
        return False

    def delete_all_customers(self):
        self.cursor.execute("DELETE FROM Orders")
        self.cursor.execute("DELETE FROM Customers")
        self.conn.commit()

# Classes for handling data
class MenuItem:
    def __init__(self, item_id, item_name, price):
        self.item_id = item_id
        self.item_name = item_name
        self.price = price

class Customer:
    def __init__(self, name, contact):
        self.name = name.strip().lower()
        self.contact = contact.strip()

# Create database and tables if they don't exist
create_database_and_tables()


# //////////////////////////////////////////
def test_connection():
    try:
        conn = create_connection()
        print("Connected to MySQL Workbench database successfully!")
        conn.close()
    except mysql.connector.Error as err:
        print("Connection failed:", err)

test_connection()

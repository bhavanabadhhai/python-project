import streamlit as st
from CafeBar import Management, Customer  # Importing backend classes and functions
import base64
import mysql.connector

# Function to convert image to base64
def image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()

# Function to set background
def set_background(image_path):
    encoded_image = image_to_base64(image_path)
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{encoded_image}");
            background-size: cover;
            background-position: center;
        }}
        </style>
        """, unsafe_allow_html=True
    )

# Function to set sidebar background
def set_sidebar_background(image_path):
    encoded_image = image_to_base64(image_path)
    st.markdown(
        f"""
        <style>
        [data-testid="stSidebar"] > div:first-child {{
            background-image: url("data:image/png;base64,{encoded_image}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
        }}
        </style>
        """, unsafe_allow_html=True
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

# Main function
def main():
    # Create database and tables if they don't exist
    create_database_and_tables()

    st.sidebar.title("The Maclaren's")

    # Dropdown for sidebar options
    options = ["Place Order", "View Orders", "Print Bill", "Delete Customer", "Ratings"]
    choice = st.sidebar.selectbox("Select an option", options)

    # Set backgrounds based on selected panel
    background_images = {
        "Place Order": "C:/Users/HP/OneDrive/Desktop/CafeManagement\photo_3_2024-12-12_00-46-01.jpg",
        "View Orders": "C:/Users/HP/OneDrive/Desktop/CafeManagement\photo_4_2024-12-12_00-46-01.jpg",
        "Print Bill": "C:/Users/HP/OneDrive/Desktop/CafeManagement\photo_1_2024-12-12_00-46-01.jpg",
        "Delete Customer": "C:/Users/HP/OneDrive/Desktop/CafeManagement\photo_6_2024-12-12_00-46-01.jpg",
    }
    set_sidebar_background("C:/Users/HP/OneDrive/Desktop/CafeManagement/photo_5_2024-12-12_00-46-01.jpg")

    if "welcome_shown" not in st.session_state:
        st.session_state.welcome_shown = True
        set_background("C:/Users/HP/OneDrive/Desktop/CafeManagement/photo_2_2024-12-12_00-46-01.jpg")
        st.markdown(
            """
            <div style="background-color: rgba(0, 0, 0, 0.5); padding: 20px; border-radius: 10px; text-align: center;">
                <h1 style="color: white !important;">Welcome to</h1>
                <p style="color: white;font-size: 38px">The Maclaren's Cafe</p>
                <p style="color: white; font-size: 18px;">Step into a world where every sip and bite is crafted with care and passion. At The Maclarens, we aim to deliver an unparalleled café experience, blending exquisite flavors with a warm and inviting atmosphere.

Whether you're here for a quick coffee, a hearty meal, or just a cozy place to relax, we've got you covered. Let’s make your time here unforgettable! ☕✨</p>
                 <p style="color: white;font-size: 20px;font-weight: bold">Please Select Your Options From Sidebar</p>
            </div>
           
            """, unsafe_allow_html=True
        )
        st.stop()  # Stop execution to show welcome panel first

    set_background(background_images.get(choice, "C:/Users/HP/OneDrive/Desktop/CafeManagement/paring.jpg"))

    # Create instance of Management class
    system = Management()

    if choice == "Ratings":
        # Ratings Panel
        st.title("Give Your Rating", anchor="center")
        st.subheader("We value your feedback!", anchor="center")

        # Star Rating Section using radio buttons
        rating = st.radio("Rate Your Experience", options=["⭐", "⭐⭐", "⭐⭐⭐", "⭐⭐⭐⭐", "⭐⭐⭐⭐⭐"])

        # Optionally, add a text area for feedback
        feedback = st.text_area("Share your feedback", placeholder="Enter your comments here...")

        if st.button("Submit Rating"):
            if feedback:
                # Store the rating and feedback into the system (e.g., database or variable)
                st.success(f"Thank you for your feedback! You rated: {rating}")
            else:
                st.warning("Please provide feedback along with your rating.")

    elif choice == "Place Order":
        st.title("Place Your Order", anchor="center")
        st.subheader("Customer Details", anchor="center")
        customer_name = st.text_input("Enter Your Name", key="name_input")
        customer_contact = st.text_input("Enter Your Contact No.", key="contact_input")
        if not customer_name or not customer_contact:
            st.warning("Please enter your name and contact before placing an order.")
        customer = Customer(customer_name, customer_contact)

        st.subheader("Menu")
        menu_items = system.view_menu()
        selected_items = []
        with st.container():
            for item in menu_items:
                st.markdown(f'<div class="menu-item-container"><div class="menu-item">{item[1]} - ${item[2]}</div></div>', unsafe_allow_html=True)
                quantity = st.number_input(f"Enter quantity for {item[1]}", min_value=0, key=f"quantity_{item[0]}", help=f"Select quantity for {item[1]}")
                if quantity > 0:
                    selected_items.append({"item_id": item[0], "item_name": item[1], "price": item[2], "quantity": quantity})
            st.session_state.selected_items = selected_items

        if st.button("Place Order") and customer_name and customer_contact:
            if st.session_state.selected_items:
                order_status = system.place_order(customer, st.session_state.selected_items)
                if order_status == "Order placed successfully!":
                    st.success("Order placed successfully!")
            else:
                st.success(order_status)

    elif choice == "View Orders":
        st.title("View Orders", anchor="center")
        try:
            # Fetch aggregated orders
            system.cursor.execute("""
                SELECT c.customer_name, c.contact, m.item_name, SUM(o.quantity) AS total_quantity, MAX(o.order_time) AS latest_order_date
                FROM Orders o
                JOIN Customers c ON o.customer_id = c.customer_id
                JOIN Menu m ON o.item_id = m.item_id
                GROUP BY c.customer_name, c.contact, m.item_name
                ORDER BY latest_order_date DESC
            """)
            orders = system.cursor.fetchall()

            if orders:
                # Group data by customer
                customer_orders = {}
                for customer_name, contact, item_name, total_quantity, latest_order_date in orders:
                    if (customer_name, contact) not in customer_orders:
                        customer_orders[(customer_name, contact)] = {"items": [], "date": latest_order_date}
                    customer_orders[(customer_name, contact)]["items"].append((item_name, total_quantity))

                # Display grouped orders
                for (customer_name, contact), data in customer_orders.items():
                    items_list = "".join([f"<li>{item_name} x {total_quantity}<li>" for item_name, total_quantity in data["items"]])
                    st.markdown(f"""
                    <div style="background-color: rgba(0, 0, 0, 0.5); padding: 20px; color: white; border-radius: 10px; margin-bottom: 20px;">
                        <h3 style="margin-bottom: 10px; color: #ffd700;">Customer: <span style="color: #fff;">{customer_name}</span></h3>
                        <p style="margin: 5px 0; font-size: 18px;"><strong>Contact:<span style="color: #fff;"></strong>{contact}</span></p>
                        <p style="margin: 5px 0; font-size: 18px;"><strong>Last Ordered On:</strong> {data['date'].strftime('%Y-%m-%d %H:%M:%S')}</p>
                        <p style="margin: 5px 0; font-size: 18px;"><strong>Orders:</strong></p>
                        <ul style="list-style-type: none; padding-right: 20px;">
                            {items_list}
                        </ul>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.warning("No orders found.")
        except Exception as e:
            st.error(f"Error while fetching orders: {str(e)}")

    elif choice == "Print Bill":
        st.title("Print Bill", anchor="center")
        customer_name = st.text_input("Enter Customer Name for Bill")
        customer_contact = st.text_input("Enter Customer Contact for Bill")

        if st.button("Generate Bill"):
            if customer_name and customer_contact:
                system.cursor.execute("""
                    SELECT c.customer_name, m.item_name, o.quantity, o.order_time
                    FROM Orders o
                    JOIN Customers c ON o.customer_id = c.customer_id
                    JOIN Menu m ON o.item_id = m.item_id
                    WHERE c.customer_name = %s AND c.contact = %s
                    ORDER BY o.order_time DESC
                """, (customer_name, customer_contact))
                customer_orders = system.cursor.fetchall()

                if customer_orders:
                    total_bill = 0
                    st.markdown(f"""
                    <div style="background-color: #f4f4f9; padding: 20px; border-radius: 10px; box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);">
                    <h2 style="text-align: center; color: black;">Customer Bill</h2>
                    <hr style="border: 1px solid #ccc;">
                    <div style="font-size: 18px; color: black; padding: 10px 0;">
                        <strong>Customer Name:</strong> {customer_name}<br>
                        <strong>Contact:</strong> {customer_contact}<br>
                        <strong>Order Date:</strong> {customer_orders[0][3].strftime('%Y-%m-%d %H:%M:%S')}<br>
                    </div>
                    <hr style="border: 1px solid #ccc;">
                    """, unsafe_allow_html=True)

                    for _, item_name, quantity, _ in customer_orders:
                        item_total = quantity * 20  # Assuming each item costs $20
                        total_bill += item_total
                        st.markdown(f"""
                        <div style="background-color: #ecf0f1; padding: 10px; color: black;margin: 10px 0; border-radius: 8px; border: 1px solid #ddd;">
                            <div style="display: flex; justify-content: space-between;">
                                <div><strong>Item:</strong> <span style="color: black ;">{item_name}</span></div>
                                <div><strong>Quantity:</strong> <span style="color: black;">{quantity}</span></div>
                            </div>
                            <div style="display: flex; justify-content: space-between; padding-top: 8px;">
                                <div><strong>Item Total:</strong> <span style="color: black;">${item_total}</span></div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                    st.markdown(f"""
                    <hr style="border: 1px solid #ccc;">
                    <div style="font-size: 20px; font-weight: bold; text-align: right; padding: 10px 0; color: black;">
                    <strong>Total Bill:</strong> ${total_bill}
                    </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.warning("No such user found.")
            else:
                st.warning("Please enter both name and contact to generate the bill.")

    elif choice == "Delete Customer":
        st.title("Delete Customer", anchor="center")
        delete_all_checkbox = st.checkbox("Delete All Customers", value=False)
        
        if delete_all_checkbox:
            confirm_delete_all = st.button("Confirm Delete All Customers")
            if confirm_delete_all:
                system.delete_all_customers()
                st.success("All customers have been deleted successfully.")
        else:
            customer_name = st.text_input("Enter Customer Name to Delete")
            customer_contact = st.text_input("Enter Customer Contact to Delete")
            if customer_name and customer_contact:
                if st.button("Delete"):
                    success = system.delete_customer(customer_name, customer_contact)
                    if success:
                        st.success(f"Customer {customer_name} with contact {customer_contact} has been deleted successfully.")
                    else:
                        st.error(f"Customer with name {customer_name} and contact {customer_contact} not found.")

if __name__ == "__main__":
    main()
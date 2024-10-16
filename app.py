from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os

app = Flask(__name__)

# Ensure the database is initialized on app startup
def init_db():
    db_exists = os.path.exists('pizza_orders.db')
    conn = sqlite3.connect('pizza_orders.db')
    c = conn.cursor()
    
    # Create the table if it doesn't exist
    c.execute('''CREATE TABLE IF NOT EXISTS orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    table_number INTEGER NOT NULL,
                    pizza TEXT NOT NULL,
                    quantity INTEGER NOT NULL,
                    price REAL NOT NULL,
                    total REAL NOT NULL
                )''')
    conn.commit()
    conn.close()

# Define pizza prices
pizza_prices = {
    'Margherita': 8.50,
    'Pepperoni': 10.00,
    'Vegetarian': 9.00,
    'Hawaiian': 10.50
}

# Route for processing the order from customers (tables)
@app.route('/table/<int:id>/process_order', methods=['POST'])
def process_order(id):
    pizza = request.form['pizza']
    quantity = int(request.form['quantity'])
    
    # Get the price of the selected pizza
    price = pizza_prices[pizza]
    total = price * quantity

    # Insert the order into the database
    conn = sqlite3.connect('pizza_orders.db')
    c = conn.cursor()
    c.execute('INSERT INTO orders (table_number, pizza, quantity, price, total) VALUES (?, ?, ?, ?, ?)', 
              (id, pizza, quantity, price, total))
    conn.commit()
    conn.close()
    
    # Redirect to the table's orders page
    return redirect(url_for('view_table', id=id))

# Route for displaying the order form for customers (tables)
@app.route('/table/<int:id>/order')
def order_form_table(id):
    return render_template('order.html', id=id)

# Route for employees to input orders, includes table_number input
@app.route('/', methods=['GET', 'POST'])
def order_form():
    if request.method == 'POST':
        pizza = request.form['pizza']
        quantity = int(request.form['quantity'])
        table_number = int(request.form['table_number'])
        
        # Get the price of the selected pizza
        price = pizza_prices[pizza]
        total = price * quantity

        # Insert the order into the database
        conn = sqlite3.connect('pizza_orders.db')
        c = conn.cursor()
        c.execute('INSERT INTO orders (table_number, pizza, quantity, price, total) VALUES (?, ?, ?, ?, ?)', 
                  (table_number, pizza, quantity, price, total))
        conn.commit()
        conn.close()
        
        # Redirect to the table's orders page
        return redirect(url_for('view_table', id=table_number))
    else:
        return render_template('order_employee.html')  # A separate template with table_number input field

# Route to view orders for a table
@app.route('/table/<int:id>')
def view_table(id):
    conn = sqlite3.connect('pizza_orders.db')
    c = conn.cursor()
    c.execute('SELECT pizza, quantity, price, total FROM orders WHERE table_number = ?', (id,))
    orders = c.fetchall()
    c.execute('SELECT SUM(total) FROM orders WHERE table_number = ?', (id,))
    table_total = c.fetchone()[0]
    conn.close()
    return render_template('table_orders.html', id=id, orders=orders, total=table_total)

# Route to handle payment for a table
@app.route('/pay/<int:id>', methods=['GET', 'POST'])
def pay(id):
    if request.method == 'POST':
        # Delete the orders for the table from the database
        conn = sqlite3.connect('pizza_orders.db')
        c = conn.cursor()
        c.execute('DELETE FROM orders WHERE table_number = ?', (id,))
        conn.commit()
        conn.close()
        return render_template('payment_success.html', id=id)
    else:
        # Display the total amount and ask for confirmation
        conn = sqlite3.connect('pizza_orders.db')
        c = conn.cursor()
        c.execute('SELECT SUM(total) FROM orders WHERE table_number = ?', (id,))
        table_total = c.fetchone()[0]
        conn.close()
        return render_template('payment.html', id=id, total=table_total)

if __name__ == '__main__':
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True) # running flask on local network in order to be possible to acces the flask server from the phone

from flask import Flask, jsonify, render_template, request, redirect, url_for
import sqlite3
import time
import requests  # Add this import

app = Flask(__name__)

DATABASE = 'pizza_order.db'
connection = sqlite3.connect(DATABASE, check_same_thread=False)
cursor = connection.cursor()

# Table creation (unchanged)
cursor.execute("""
CREATE TABLE IF NOT EXISTS pizzaOrders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    orderId INTEGER,
    tablenr INTEGER,
    pizza_type TEXT,
    quantity INTEGER,
    time TIME,
    order_status TEXT DEFAULT 'pending'
)
""")

order = {}
pizzaPrice = {
    'Margherita': 3,
    'Pepperoni': 5,
    'Vegetarian': 4,
    'BBQ-Chicken': 6,
    'Hawaiian': 9
}

tableNr = None
total_amount = 0

@app.route('/')
def index():
    return redirect(url_for('table_number'))

@app.route('/table_number', methods=['GET', 'POST'])
def table_number():
    if request.method == 'POST':
        table_nr = request.form.get('table_nr')
        return redirect(url_for('menu', id=table_nr))
    return render_template('table_number.html')

@app.route("/order")
def menu():
    table_nr = request.args.get('id')
    global tableNr
    tableNr = table_nr
    return render_template('menu.html', table=tableNr)

@app.route("/submit_order", methods=['POST'])
def submit():
    pizza_type = request.form.get('pizza')
    if pizza_type in order:
        order[pizza_type] += 1
    else:
        order[pizza_type] = 1
    return jsonify({'message': f'{pizza_type} has been added to your cart!'})

@app.route("/confirm")
def confirm():
    global total_amount
    total_amount = 0  # Reset total_amount before calculation
    for pizza, amount in order.items():
        total_amount += pizzaPrice[pizza] * amount
    return render_template("confirm.html", order=order, table=tableNr, total=total_amount)

@app.route('/thankyou')
def thankyou():
    time_cur = time.strftime('%H:%M:%S')
    # Generate new orderId
    cursor.execute("SELECT MAX(orderId) FROM pizzaOrders")
    result = cursor.fetchone()
    if result[0] is None:
        new_order_id = 1
    else:
        new_order_id = result[0] + 1
    for pizzaType, amount in order.items():
        cursor.execute(
            "INSERT INTO pizzaOrders (orderId, tablenr, pizza_type, quantity, time) VALUES (?, ?, ?, ?, ?)",
            (new_order_id, tableNr, pizzaType, amount, time_cur)
        )
    order.clear()
    connection.commit()
    return render_template('thankyou.html')

@app.route('/dashboard')
def dashboard():
    cursor.execute("""
        SELECT po.orderId, po.tablenr, po.time, po.pizza_type, po.quantity
        FROM pizzaOrders po
    """)
    orders_raw = cursor.fetchall()
    orders = {}
    for order_id, table_nr, order_time, pizza_type, quantity in orders_raw:
        if order_id not in orders:
            orders[order_id] = {
                'orderId': order_id,
                'tablenr': table_nr,
                'time': order_time,
                'order_items': []
            }
        orders[order_id]['order_items'].append((pizza_type, quantity))
    return render_template('dashboard.html', orders=orders.values())

@app.route('/validate_order', methods=['POST'])
def validate_order():
    order_id = request.form.get('orderId')
    # Delete the order from the database
    cursor.execute("DELETE FROM pizzaOrders WHERE orderId = ?", (order_id,))
    connection.commit()
    # Send notification to Arduino
    arduino_url = 'http://arduino_ip_address/beep'  # Replace with actual IP and endpoint
    try:
        response = requests.get(arduino_url)
        print(f"Arduino response: {response.status_code}")
    except Exception as e:
        print(f"Error sending notification to Arduino: {e}")
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

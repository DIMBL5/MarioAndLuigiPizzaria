from flask import Flask,jsonify,render_template,request,redirect,url_for
import sqlite3
import time

app = Flask(__name__)

DATABASE = 'pizza_orders.db'
connection = sqlite3.connect("pizza_order.db",check_same_thread=False)
cursor = connection.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS pizzaOrders (orderNr INTEGER NOT NULL PRIMARY KEY,tablenr INTEGER, pizza_type TEXT, quantity INTEGER, time TIME)")

order = {}

pizzaPrice= {
    'Margherita' : 3,
    'Pepperoni' : 5,
    'Vegetarian' : 4,
    'BBQ-Chicken' : 6,
    'Hawaiian' : 9
}

tableNr = None
total_amount = 0

@app.route("/order") # this is the index page, where customers order 
def menu():
    table_nr = request.args.get('id')
    global tableNr
    tableNr = table_nr
    return render_template('menu.html',table = tableNr)

@app.route("/submit_order",methods = ['POST']) 
def submit():
    pizza_type = request.form.get('pizza') 

    if pizza_type in order :
        order[pizza_type] += 1
    else:
        order[pizza_type] = 1
    return jsonify({'message': f'{pizza_type} has been added to your cart!'})

@app.route("/confirm")
def confirm():
    global total_amount
    for pizza,amount in order.items():
        total_amount = total_amount + pizzaPrice[pizza] * amount
    return render_template("confirm.html",order = order,table = tableNr,total = total_amount)

@app.route('/thankyou')
def thankyou():
    time_cur = time.strftime('%H:%M:%S')
    for pizzaType,amount in order.items():
        cursor.execute("INSERT INTO pizzaOrders (tablenr,pizza_type,quantity,time) VALUES (?,?,?,?)",(tableNr,pizzaType,amount,time_cur))
    
    order.clear()
    connection.commit()
    return render_template('thankyou.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000,debug=True)
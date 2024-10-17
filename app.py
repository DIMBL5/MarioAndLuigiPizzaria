from flask import Flask,jsonify,render_template,request,redirect,url_for,session
import sqlite3
import time

app = Flask(__name__)

file = open("sessionkey.txt","r")
SESSIONKEY  = file.read() # reading from a gitignore file in order not to leak the key

app.secret_key=SESSIONKEY


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


@app.route("/order") # this is the index page, where customers order 
def menu():
    table_nr = request.args.get('id')
    session['tableNr'] = table_nr
    session['order'] ={}
    return render_template('menu.html',table = session['tableNr'])

@app.route("/submit_order",methods = ['POST']) 
def submit():
    pizza_type = request.form.get('pizza') 
    if 'order' not in session : #if there is no order in session, create new order
        session['order'] = {}

    order = session['order'] #populate dictionary from session

    if pizza_type in order:
        order[pizza_type] += 1
    else:
        order[pizza_type] = 1 

    session['order'] = order #updating session with data /send back to session
    return jsonify({'message': f'{pizza_type} has been added to your cart!'})

@app.route("/confirm")
def confirm():
    order = session.get('order',{})
    total_amount = sum(quantity * pizzaPrice[pizza] for pizza, quantity in order.items())
    return render_template("confirm.html",order = order,table = session['tableNr'], total = total_amount)

@app.route('/thankyou')
def thankyou():
    order = session.get('order' , {}) #if not found returns an empty dict {}
    tableNr = session['tableNr']
    time_cur = time.strftime('%H:%M:%S')

    for pizzaType,amount in order.items():
        cursor.execute("INSERT INTO pizzaOrders (tablenr,pizza_type,quantity,time) VALUES (?,?,?,?)",(tableNr,pizzaType,amount,time_cur))
    
    session.pop('order',None) # clear the dictionary from the session
    connection.commit()
    return render_template('thankyou.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000,debug=True)
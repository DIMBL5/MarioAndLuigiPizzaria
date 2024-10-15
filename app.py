from flask import Flask , render_template , redirect,request,url_for

app = Flask(__name__)

@app.route("/order") #order page from where we place an order 
def order () : 
    return render_template("order.html")
 
@app.route("/process",methods =["POST"]) 

def process_order(): #processing the order 
    pizza_type = request.form.get("pizza")
    quantity = request.form.get("quantity")
    #table_nr = request.form.get("table")
    id_nr = request.args.get('id')

    return render_template('placeholder.html',pizza = pizza_type , quan = quantity,id = id_nr)
    

if __name__ == '__main__' : 
    app.run(host="0.0.0.0",port=5000,debug =True)#running flask on local network in order to be possible to acces the flask server from the phone
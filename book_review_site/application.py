import os

from flask import Flask, session, render_template, request,jsonify,json
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))
@app.route("/", methods=["POST","GET"])
def index():
	print("index() running...................................")
	if request.method == "POST":
		username1 = request.form.get("username")
		password = request.form.get("password")
		usernameCheck = db.execute("SELECT * FROM users WHERE username = :username AND password = :password",{"username":username1,"password":password})
		if usernameCheck != None:
			session['username']=username1
			return render_template("login.html",username=session['username'])
		else: 
			return render_template("index.html")
	else:
		return render_template("index.html")


@app.route("/login", methods=["POST","GET"])
def login():
	print("login() running...................................")
	if request.method == "POST":
		username1 = request.form.get("username")
		password = request.form.get("password")
		db.execute("INSERT INTO users (username, password) VALUES (:username,:password)",{ "username" : username1, "password" : password}).first()
		db.commit()
		session['username']=username1
		return render_template("login.html",username=session['username'])


	elif session['username'] != None:
			return render_template("login.html",username=session['username'])
	else: return render_template("index.html")

@app.route("/registration")
def registration():
	print("registration() running...................................")
	return render_template("registration.html")

@app.route("/search", methods=["POST","GET"])
def search():
	print("search() running...................................")
	searchword = request.form.get("searchword")
	print(searchword)
	searchworda = "%"
	searchworda +=str(searchword)
	searchworda += "%"
	searchworda=str(searchworda)
	print(searchworda)
	results1 = db.execute("SELECT * FROM books WHERE isbn LIKE :searchword OR title LIKE :searchword1 OR author LIKE :searchword2 OR year LIKE :searchword3 ", {"searchword":searchworda,"searchword1":searchworda,"searchword2":searchworda,"searchword3":searchworda}).fetchall()
	message=""
	if not results1:
		message="could not find books"
	return render_template("results.html",results=results1,username=session['username'],message=message)

@app.route("/book/<string:isbn>", methods=["GET","POST"])
def bookpage(isbn):
	print("bookpage(isbn) running...................................")
	reviewerror=""
	if request.method == "POST":
		review =request.form.get("review")
		rating = request.form.get("rating")
		checkuser = db.execute("SELECT * FROM reviews WHERE username=:username AND isbn =:isbn",{"username":session["username"],"isbn":isbn}).first()
		if checkuser == None:
			db.execute("INSERT INTO reviews (isbn,review,username,rating) VALUES (:isbn,:review,:username,:rating)",{"isbn":isbn,"review":review,"username":session["username"],"rating":rating})
			db.commit()
		else:
			reviewerror="you have already reviewed this book"
	bookinfo = db.execute("SELECT * FROM books WHERE isbn= :isbn",{"isbn":isbn}).first()
	reviews = db.execute("SELECT * FROM reviews WHERE isbn= :isbn",{"isbn":isbn}).fetchall()
	return render_template("bookinfo.html",bookinfo=bookinfo,reviews=reviews,reviewerror=reviewerror)	


@app.route("/api/<isbn>")
def book_api(isbn):
	print("book_api(isbn) running...................................")
	bookinfo= db.execute("SELECT * FROM books WHERE isbn =:isbn", {"isbn":isbn}).first()
	reviewcount = db.execute("SELECT COUNT(review) FROM  reviews WHERE isbn =:isbn", {"isbn":isbn}).first()
	print(reviewcount[0])
	ratingavg = db.execute("SELECT AVG(rating) FROM reviews WHERE isbn =:isbn", {"isbn":isbn}).first()
	if bookinfo == None:
		return jsonify({"error":"isbn not found"}), 404
	return jsonify({
		"title": bookinfo.title,
		"author": bookinfo.author,
		"year": bookinfo.year,
		"isbn": bookinfo.isbn,
		"review_count": reviewcount[0],
		"average_score": str(ratingavg[0])
		})

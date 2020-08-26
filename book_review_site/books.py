import os,csv

from flask import Flask, session, render_template, request
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
def main():
	with open('books.csv') as file:
		data = csv.reader(file, delimiter=',')
		for row in data:
			try: 
				db.execute("INSERT INTO books (isbn,title,author,year)VALUES (:isbn,:title,:author,:year)",
				{"isbn":row[0],"title":row[1],"author":row[2],"year":row[3]})
				db.commit()
			except:
				continue
			else:
				continue
main()
from flask import Flask, render_template, request, redirect, url_for
import os
import sqlite3

app = Flask(__name__)
DATABASE = "bookstore.db"

def get_db_connection():
    conn = sqlite3.connect("bookstore.db")
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/", methods=["GET"])
def home():
    conn = get_db_connection()

    categories = conn.execute("""
        SELECT *
        FROM category
        ORDER BY categoryName
    """).fetchall()

    conn.close()

    return render_template("index.html", categories=categories)

@app.route("/category", methods=["GET"])
def category():
    category_id = request.args.get("categoryId", type=int)

    conn = get_db_connection()

    categories = conn.execute("""
        SELECT *
        FROM category
        ORDER BY categoryName
    """).fetchall()

    selected_category = conn.execute("""
        SELECT *
        FROM category
        WHERE categoryId = ?
    """, (category_id,)).fetchone()

    books = conn.execute("""
        SELECT book.*, category.categoryName
        FROM book
        JOIN category ON book.categoryId = category.categoryId
        WHERE book.categoryId = ?
        ORDER BY book.title
    """, (category_id,)).fetchall()

    conn.close()

    return render_template(
        "category.html",
        categories=categories,
        selectedCategory=selected_category,
        books=books,
        searchTerm=None,
        nothingFound=False
    )

@app.route("/search", methods=["POST"])
def search():
    term = request.form.get("search", "").strip()

    conn = get_db_connection()

    categories = conn.execute("""
        SELECT *
        FROM category
        ORDER BY categoryName
    """).fetchall()

    books = conn.execute("""
        SELECT book.*, category.categoryName
        FROM book
        JOIN category ON book.categoryId = category.categoryId
        WHERE lower(book.title) LIKE lower(?)
        ORDER BY book.title
    """, (f"%{term}%",)).fetchall()

    conn.close()

    return render_template(
        "category.html",
        categories=categories,
        selectedCategory=None,
        books=books,
        searchTerm=term,
        nothingFound=(len(books) == 0)
    )

@app.route("/book", methods=["GET"])
def book_detail():
    book_id = request.args.get("bookId", type=int)

    conn = get_db_connection()

    categories = conn.execute("""
        SELECT *
        FROM category
        ORDER BY categoryName
    """).fetchall()

    book = conn.execute("""
        SELECT book.*, category.categoryName
        FROM book
        JOIN category ON book.categoryId = category.categoryId
        WHERE book.bookId = ?
    """, (book_id,)).fetchone()

    conn.close()

    return render_template(
        "book_detail.html",
        book=book,
        categories=categories
    )

@app.route("/add-book", methods=["GET", "POST"])
def add_book():
    conn = get_db_connection()

    categories = conn.execute("""
        SELECT *
        FROM category
        ORDER BY categoryName
    """).fetchall()

    if request.method == "POST":
        title = request.form.get("title")
        author = request.form.get("author")
        isbn = request.form.get("isbn")
        price = request.form.get("price", type=float)
        image = request.form.get("image")
        category_id = request.form.get("categoryId", type=int)

        conn.execute("""
            INSERT INTO book (categoryId, title, author, isbn, price, image, readNow)
            VALUES (?, ?, ?, ?, ?, ?, 0)
        """, (category_id, title, author, isbn, price, image))

        conn.commit()
        conn.close()

        return redirect(url_for("home"))

    conn.close()
    return render_template("add_book.html", categories=categories)

@app.route("/search-author", methods=["POST"])
def search_author():
    term = request.form.get("author", "").strip()

    conn = get_db_connection()

    categories = conn.execute("""
        SELECT *
        FROM category
        ORDER BY categoryName
    """).fetchall()

    books = conn.execute("""
        SELECT book.*, category.categoryName
        FROM book
        JOIN category ON book.categoryId = category.categoryId
        WHERE lower(book.author) LIKE lower(?)
        ORDER BY book.author, book.title
    """, (f"%{term}%",)).fetchall()

    conn.close()

    return render_template(
        "category.html",
        categories=categories,
        selectedCategory=None,
        books=books,
        searchTerm=term,
        nothingFound=(len(books) == 0)
    )

@app.errorhandler(Exception)
def handle_error(e):
    return render_template("error.html", error=e), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=True)
    

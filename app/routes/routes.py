from datetime import date
import json
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash
from models.models import User, Book
from engine.db import db 

app_route = Blueprint('route', __name__)

@app_route.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('route.profile'))
    else:
        return render_template('index.html')

@app_route.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('route.books'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('route.books'))
        else:
            flash('Invalid username or password')
    return render_template('login.html')

@app_route.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('route.profile'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        user = User.query.filter_by(username=username).first()
        if user:
            flash('Username already taken')
        else:
            hashed_password = generate_password_hash(password)
            new_user = User(username=username, password=hashed_password, email=email)
            db.session.add(new_user)
            db.session.commit()
            flash('Account created successfully')
            return redirect(url_for('route.login'))
    return render_template('register.html')

@app_route.route('/profile')
def profile():
    if current_user.is_authenticated:
        return render_template('profile.html', user=current_user)
    else:
        return redirect(url_for('route.login'))

@app_route.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('route.index'))

@app_route.route('/books', methods=['GET', 'POST'])
def books():
    if not current_user.is_authenticated:
        return redirect(url_for('route.login'))
    else:
        books = Book.query.all()
        if request.method == 'POST':
            match request.form['oper']:
                case "import":
                    return redirect(url_for('route.import_json'))
                case "export":
                    books_list = []
                    for book in books:
                        books_list.append({"название": book.title,
                                        "автор": book.author,
                                        "год": book.year,
                                        "описание": book.description})
                    with open(f'app/export/export_{date.today()}.json', 'w', encoding="utf-8") as file:
                        json.dump(books_list, file, ensure_ascii=False)
                        
                    flash('Экспорт файл завершен')
        return render_template('books.html', books=books)

@app_route.route('/import_json', methods=['GET', 'POST'])
def import_json():
    if not current_user.is_authenticated:
        return redirect(url_for('route.login'))
    else:
        if request.method == 'POST' and request.form['file'] != '':
            with open (request.form['file']) as file:
                books = json.load(file)
            for book in books:
                new_book = Book(title=book['название'],
                                author=book['автор'],
                                year=book['год публикации'],
                                description=book['описание'])
                db.session.add(new_book)
            db.session.commit()
            return redirect(url_for('route.books'))
    return render_template('import.html')

    
@app_route.route('/book/<int:book_id>')
def book_detail(book_id):
    book = Book.query.get_or_404(book_id)
    return render_template('book.html', book=book)

@app_route.route('/del_book/<int:book_id>', methods=['GET', 'POST'])
def book_delete(book_id):
    if not current_user.is_authenticated:
        return redirect(url_for('route.login'))
    else:
        del_book = Book.query.get_or_404(book_id)
        if request.method == 'POST':
            # del_book = Book.query.get_or_404(book_id)
            db.session.delete(del_book)
            db.session.commit()
            return redirect(url_for('route.books'))
    return render_template('del_book.html', book=del_book)

@app_route.route('/add_book', methods=['GET', 'POST'])
def add_book():
    if not current_user.is_authenticated:
        return redirect(url_for('route.login'))
    else:
        if request.method == 'POST':
            book_name = request.form['book_name']
            author = request.form['author']
            year = request.form['year']
            description = request.form['description']
            new_book = Book(title=book_name, author=author, year=year, description=description)
            db.session.add(new_book)
            db.session.commit()
            flash('Добавлена новая книга')
            return redirect(url_for('route.books'))
    return render_template('add_book.html')

@app_route.route('/update_book/<int:book_id>', methods=['GET', 'POST'])
def update_book(book_id):
    
    if not current_user.is_authenticated:
        return redirect(url_for('route.login'))
    else:
        update_book = Book.query.get_or_404(book_id)
        if request.method == 'POST':
            book_name = request.form['book_name']
            author = request.form['author']
            year = request.form['year']
            description = request.form['description']
            db.session.query(Book).filter(Book.id == book_id).update({"title": book_name,
                                                                    "author": author,
                                                                    "year": year,
                                                                    "description": description})
            db.session.commit()
            return redirect(url_for('route.books'))
    return render_template('update_book.html', book=update_book)

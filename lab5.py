from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'test'  # Change to a secure key
db = SQLAlchemy(app)
jwt = JWTManager(app)

# Models

class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    books = db.relationship('Book', backref='author', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Author {self.name}>'

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('author.id'), nullable=False)
    loans = db.relationship('BookLoan', backref='book', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Book {self.title}>'

class Reader(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    loans = db.relationship('BookLoan', backref='reader', lazy=True)

    def __repr__(self):
        return f'<Reader {self.name}>'

class BookLoan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    reader_id = db.Column(db.Integer, db.ForeignKey('reader.id'), nullable=False)
    due_date = db.Column(db.Date, nullable=False)

    def __repr__(self):
        return f'<BookLoan BookID={self.book_id} ReaderID={self.reader_id}>'

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'

with app.app_context():
    db.create_all()

# Routes

@app.route('/', methods=['GET'])
def test_connection():
    return 'Ready to work.\n Methods:\n POST(/login, /logout, /add_user, /add_author, /add_book)\n GET(/get_book, /get_author, /get_all_books)\n DELETE(/delete_book/<int:id>, /delete_author/<int:id>)\n PUT(/update_book/<int:id>)'

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username', None)
    password = data.get('password', None)

    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password, password):
        # Create access token
        access_token = create_access_token(identity=str(user.id))
        return {'access_token': access_token}, 200

    return {'message': 'Invalid credentials'}, 401

@app.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    # Optional: You can blacklist the JWT token here if needed.
    return {'message': 'Successfully logged out'}, 200

@app.route('/add_user', methods=['POST'])
def add_user():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    # Hash the password before storing
    hashed_password = generate_password_hash(password)

    new_user = User(username=username, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return f'User {new_user.username} added successfully!', 201

@app.route('/add_author', methods=['POST'])
@jwt_required()
def add_author():
    new_author = Author(name='J.K. Rowling')
    db.session.add(new_author)
    db.session.commit()
    return f'Author {new_author.name} added successfully!'

@app.route('/add_book', methods=['POST'])
@jwt_required()
def add_book():
    new_book = Book(title='Harry Potter and the Philosopher\'s Stone', author_id=1)
    db.session.add(new_book)
    db.session.commit()
    return f'Book {new_book.title} added successfully!'

@app.route('/get_book/<int:id>', methods=['GET'])
@jwt_required()
def get_book(id):
    current_user = get_jwt_identity()
    book = Book.query.get_or_404(id)
    return f'Book: {book.title}, Author: {book.author.name}'

@app.route('/get_author/<int:id>', methods=['GET'])
@jwt_required()
def get_author(id):
    author = Author.query.get_or_404(id)
    return f'Author: {author.name}'

@app.route('/update_book/<int:id>', methods=['PUT'])
@jwt_required()
def update_book(id):
    book = Book.query.get(id)
    if book:
        book.title = 'Updated Book Title'
        db.session.commit()
        return f'Book with ID {id} updated!'
    return 'Book not found!'

@app.route('/get_all_books', methods=['GET'])
@jwt_required()
def get_all_books():
    books = Book.query.all()
    return '<br>'.join([f'{book.title} by {book.author.name}' for book in books])

@app.route('/delete_book/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_book(id):
    book = Book.query.get_or_404(id)
    db.session.delete(book)
    db.session.commit()
    return f'Book {book.title} deleted successfully!'

@app.route('/delete_author/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_author(id):
    author = Author.query.get_or_404(id)
    db.session.delete(author)
    db.session.commit()
    return f'Author {author.name} and all associated books deleted successfully!'

if __name__ == '__main__':
    try:
        app.run(debug=False)
    except Exception as e:
        print(f"Error: {e}")

# python -m venv venv
# source venv/bin/activate
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import uuid

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///journal.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# In-memory session tokens for now to keep it simple
sessions = {}

notes = []

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.String(50), nullable=False)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

# Run one time:
'''with app.app_context():
    db.create_all()'''

@app.route('/')
def home():
    return "Welcome to the JournalApp Programming Interface"

# http://127.0.0.1:5000/

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data or 'email' not in data or 'password' not in data:
        return jsonify({"error": "Missing email or password"}), 400

    if User.query.filter_by(email=data['email']).first():
        return jsonify({"error": "Email already registered"}), 400

    hashed_pw = generate_password_hash(data['password'])
    new_user = User(email=data['email'], password_hash=hashed_pw)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User registered successfully"}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or 'email' not in data or 'password' not in data:
        return jsonify({"error": "Missing email or password"}), 400

    user = User.query.filter_by(email=data['email']).first()
    if user and check_password_hash(user.password_hash, data['password']):
        token = str(uuid.uuid4())
        sessions[token] = user.id
        return jsonify({"token": token})
    return jsonify({"error": "Invalid credentials"}), 401

def get_current_user():
    token = request.headers.get('Authorization')
    if not token or token not in sessions:
        return None
    return sessions[token]

@app.route('/notes', methods=['POST'])
def add_note():
    data = request.get_json()
    if not data or "content" not in data or "user_id" not in data:
        return jsonify({"error": "Missing content or user_id"}), 400

    note = Note(content=data["content"], user_id=data["user_id"])
    db.session.add(note)
    db.session.commit()

    return jsonify({"id": note.id, "user_id": note.user_id, "content": note.content}), 201

@app.route('/notes', methods=['GET'])
def get_notes():
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"error": "user_id required as query parameter"}), 400

    notes = Note.query.filter_by(user_id=user_id).order_by(Note.id).all()
    return jsonify([
        {"id": note.id, "user_id": note.user_id, "content": note.content, "created_at": note.created_at.isoformat()}
        for note in notes
    ])

@app.route('/notes/<int:note_id>', methods=['GET'])
def get_note(note_id):
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"error": "user_id required as query parameter"}), 400

    note = Note.query.get(note_id)
    if not note or note.user_id != user_id:
        return jsonify({"error": "Note not found or access denied"}), 404

    return jsonify({"id": note.id, "user_id": note.user_id, "content": note.content})

@app.route('/notes/<int:note_id>', methods=['PUT'])
def update_note(note_id):
    data = request.get_json()
    if not data or "content" not in data or "user_id" not in data:
        return jsonify({"error": "Missing 'content' or 'user_id'"}), 400

    note = Note.query.get(note_id)
    if not note or note.user_id != data["user_id"]:
        return jsonify({"error": "Note not found or access denied"}), 404

    note.content = data["content"]
    db.session.commit()

    return jsonify({"id": note.id, "user_id": note.user_id, "content": note.content})


@app.route('/notes/<int:note_id>', methods=['DELETE'])
def delete_note(note_id):
    data = request.get_json()
    if not data or "user_id" not in data:
        return jsonify({"error": "Missing user_id"}), 400

    note = Note.query.get(note_id)
    if not note or note.user_id != data["user_id"]:
        return jsonify({"error": "Note not found or access denied"}), 404

    db.session.delete(note)
    db.session.commit()
    return jsonify({"message": f"Note {note_id} successfully deleted"}), 200

# All CRUD functions work as of now, and edge cases are caught and error handling better.
# Notes are just stored in memory as program runs - BAD, but fine for testing
# Next, we store notes in a SQLite DB and clear some memory space.

if __name__ == '__main__':
    app.run(debug=True)
# python -m venv venv
# source venv/bin/activate
from flask import Flask, request, jsonify

app = Flask(__name__)

notes = []

@app.route('/')
def home():
    return "Welcome to the JournalApp Programming Interface"

# http://127.0.0.1:5000/

@app.route('/notes', methods=['POST'])
def add_note():
    data = request.get_json()
    if not data or "content" not in data:
        return jsonify({"error": "Missing 'content' field"}), 400

    note = {
        "id": len(notes) + 1,
        "content": data["content"]
    }
    notes.append(note)
    return jsonify(note), 201

@app.route('/notes', methods=['GET'])
def get_notes():
    return jsonify(notes)

@app.route('/notes/<int:note_id>', methods=['GET'])
def get_note(note_id):
    for note in notes:
        if note["id"] == note_id:
            return jsonify(note)
    return jsonify({"error": "Note not found"}), 404

@app.route('/notes/<int:note_id>', methods=['PUT'])
def update_note(note_id):
    data = request.json
    for note in notes:
        if note["id"] == note_id:
            note["content"] = data["content"]
            return jsonify(note)
    return jsonify({"error": "No note found"}), 404

@app.route('/notes/<int:note_id>', methods=['DELETE'])
def delete_note(note_id):
    global notes
    for i, note in enumerate(notes):
        if note["id"] == note_id:
            del notes[i]
            return jsonify({"message": f"Note {note_id} successfully deleted"}), 200
    return jsonify({"error": "Note not found"}), 404


# Using postman:
# Method = POST
# url = http://127.0.0.1:5000/notes
# Body -> Raw -> JSON = { "content": "This is my first note" }

# All CRUD functions work as of now, and edge cases are caught and error handling better.
# Notes are just stored in memory as program runs - BAD, but fine for testing
# Next, we encrypt. Then, we store notes in a file and clear some memory space.

if __name__ == '__main__':
    app.run(debug=True)
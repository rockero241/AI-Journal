from flask import Blueprint

journal_bp = Blueprint('journal', __name__)

@journal_bp.route('/create-entry', methods=['GET', 'POST'])
def create_entry():
    return "Create Journal Entry Page"

@journal_bp.route('/view-entries', methods=['GET'])
def view_entries():
    return "View Journal Entries Page"

from flask import Blueprint, request, jsonify, session
from models import db, Card, List, CardAssignment, Attachment, ChecklistItem, User
from routes.auth import login_required
from routes.boards import check_board_access, log_activity
from werkzeug.utils import secure_filename
from datetime import datetime
import os
from config import Config

cards_bp = Blueprint('cards', __name__)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

@cards_bp.route('', methods=['POST'])
@login_required
def create_card():
    """Create a new card"""
    data = request.get_json()
    user_id = session['user_id']
    
    if not data or not data.get('title') or not data.get('list_id'):
        return jsonify({'error': 'Title and list_id are required'}), 400
    
    list_obj = List.query.get(data['list_id'])
    
    if not list_obj:
        return jsonify({'error': 'List not found'}), 404
    
    board, has_access = check_board_access(list_obj.board_id, user_id)
    
    if not has_access:
        return jsonify({'error': 'Access denied'}), 403
    
    # Get the next position
    max_position = db.session.query(db.func.max(Card.position))\
        .filter_by(list_id=data['list_id']).scalar() or -1
    
    # Parse due date if provided
    due_date = None
    if data.get('due_date'):
        try:
            due_date = datetime.fromisoformat(data['due_date'].replace('Z', '+00:00'))
        except:
            pass
    
    card = Card(
        title=data['title'],
        description=data.get('description', ''),
        list_id=data['list_id'],
        position=max_position + 1,
        due_date=due_date
    )
    
    db.session.add(card)
    db.session.flush()  # Get card ID
    
    # Log activity
    log_activity(
        list_obj.board_id,
        user_id,
        'created',
        'card',
        card.id,
        f"added card '{card.title}' to list '{list_obj.title}'"
    )
    
    db.session.commit()
    
    return jsonify(card.to_dict()), 201

@cards_bp.route('/<int:card_id>', methods=['GET'])
@login_required
def get_card(card_id):
    """Get a specific card"""
    user_id = session['user_id']
    card = Card.query.get(card_id)
    
    if not card:
        return jsonify({'error': 'Card not found'}), 404
    
    list_obj = List.query.get(card.list_id)
    board, has_access = check_board_access(list_obj.board_id, user_id)
    
    if not has_access:
        return jsonify({'error': 'Access denied'}), 403
    
    return jsonify(card.to_dict()), 200

@cards_bp.route('/<int:card_id>', methods=['PUT'])
@login_required
def update_card(card_id):
    """Update a card"""
    user_id = session['user_id']
    card = Card.query.get(card_id)
    
    if not card:
        return jsonify({'error': 'Card not found'}), 404
    
    list_obj = List.query.get(card.list_id)
    board, has_access = check_board_access(list_obj.board_id, user_id)
    
    if not has_access:
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.get_json()
    
    if 'title' in data:
        card.title = data['title']
    
    if 'description' in data:
        card.description = data['description']
    
    if 'position' in data:
        card.position = data['position']
    
    if 'completed' in data:
        card.completed = data['completed']
        status = 'completed' if card.completed else 'reopened'
        log_activity(
            list_obj.board_id,
            user_id,
            status,
            'card',
            card_id,
            f"{status} card '{card.title}'"
        )
    
    if 'due_date' in data:
        if data['due_date']:
            try:
                card.due_date = datetime.fromisoformat(data['due_date'].replace('Z', '+00:00'))
            except:
                pass
        else:
            card.due_date = None
    
    # Handle list change (moving card between lists)
    if 'list_id' in data and data['list_id'] != card.list_id:
        old_list = List.query.get(card.list_id)
        new_list = List.query.get(data['list_id'])
        
        if new_list and new_list.board_id == list_obj.board_id:
            card.list_id = data['list_id']
            
            # Reset position to end of new list
            max_position = db.session.query(db.func.max(Card.position))\
                .filter_by(list_id=data['list_id']).scalar() or -1
            card.position = max_position + 1
            
            log_activity(
                list_obj.board_id,
                user_id,
                'moved',
                'card',
                card_id,
                f"moved card '{card.title}' from '{old_list.title}' to '{new_list.title}'"
            )
    
    card.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify(card.to_dict()), 200

@cards_bp.route('/<int:card_id>', methods=['DELETE'])
@login_required
def delete_card(card_id):
    """Delete a card"""
    user_id = session['user_id']
    card = Card.query.get(card_id)
    
    if not card:
        return jsonify({'error': 'Card not found'}), 404
    
    list_obj = List.query.get(card.list_id)
    board, has_access = check_board_access(list_obj.board_id, user_id)
    
    if not has_access:
        return jsonify({'error': 'Access denied'}), 403
    
    # Log activity
    log_activity(
        list_obj.board_id,
        user_id,
        'deleted',
        'card',
        card_id,
        f"deleted card '{card.title}' from list '{list_obj.title}'"
    )
    
    db.session.delete(card)
    db.session.commit()
    
    return jsonify({'message': 'Card deleted successfully'}), 200

@cards_bp.route('/<int:card_id>/assignments', methods=['POST'])
@login_required
def assign_user(card_id):
    """Assign a user to a card"""
    user_id = session['user_id']
    card = Card.query.get(card_id)
    
    if not card:
        return jsonify({'error': 'Card not found'}), 404
    
    list_obj = List.query.get(card.list_id)
    board, has_access = check_board_access(list_obj.board_id, user_id)
    
    if not has_access:
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.get_json()
    
    if not data or not data.get('user_id'):
        return jsonify({'error': 'user_id is required'}), 400
    
    # Check if assignment already exists
    existing = CardAssignment.query.filter_by(
        card_id=card_id,
        user_id=data['user_id']
    ).first()
    
    if existing:
        return jsonify({'error': 'User already assigned'}), 400
    
    # Verify user exists and has access to board
    assign_user_obj = User.query.get(data['user_id'])
    if not assign_user_obj:
        return jsonify({'error': 'User not found'}), 404
    
    assignment = CardAssignment(
        card_id=card_id,
        user_id=data['user_id']
    )
    
    db.session.add(assignment)
    
    # Log activity
    log_activity(
        list_obj.board_id,
        user_id,
        'assigned',
        'card',
        card_id,
        f"assigned {assign_user_obj.username} to card '{card.title}'"
    )
    
    db.session.commit()
    
    return jsonify(assignment.to_dict()), 201

@cards_bp.route('/<int:card_id>/assignments/<int:assignment_id>', methods=['DELETE'])
@login_required
def unassign_user(card_id, assignment_id):
    """Remove a user assignment from a card"""
    user_id = session['user_id']
    card = Card.query.get(card_id)
    
    if not card:
        return jsonify({'error': 'Card not found'}), 404
    
    list_obj = List.query.get(card.list_id)
    board, has_access = check_board_access(list_obj.board_id, user_id)
    
    if not has_access:
        return jsonify({'error': 'Access denied'}), 403
    
    assignment = CardAssignment.query.get(assignment_id)
    
    if not assignment or assignment.card_id != card_id:
        return jsonify({'error': 'Assignment not found'}), 404
    
    unassigned_user = assignment.user
    db.session.delete(assignment)
    
    # Log activity
    log_activity(
        list_obj.board_id,
        user_id,
        'unassigned',
        'card',
        card_id,
        f"unassigned {unassigned_user.username} from card '{card.title}'"
    )
    
    db.session.commit()
    
    return jsonify({'message': 'User unassigned successfully'}), 200

@cards_bp.route('/<int:card_id>/attachments', methods=['POST'])
@login_required
def upload_attachment(card_id):
    """Upload a file attachment to a card"""
    user_id = session['user_id']
    
    card = Card.query.get(card_id)
    
    if not card:
        return jsonify({'error': 'Card not found'}), 404
    
    list_obj = List.query.get(card.list_id)
    board, has_access = check_board_access(list_obj.board_id, user_id)
    
    if not has_access:
        return jsonify({'error': 'Access denied'}), 403
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Add timestamp to avoid conflicts
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{filename}"
        
        filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        attachment = Attachment(
            card_id=card_id,
            filename=file.filename,
            filepath=filename,
            file_size=os.path.getsize(filepath)
        )
        
        db.session.add(attachment)
        
        # Log activity
        log_activity(
            list_obj.board_id,
            user_id,
            'attached',
            'card',
            card_id,
            f"attached file '{file.filename}' to card '{card.title}'"
        )
        
        db.session.commit()
        
        return jsonify(attachment.to_dict()), 201
    
    return jsonify({'error': 'File type not allowed'}), 400

@cards_bp.route('/<int:card_id>/attachments/<int:attachment_id>', methods=['DELETE'])
@login_required
def delete_attachment(card_id, attachment_id):
    """Delete an attachment"""
    user_id = session['user_id']
    card = Card.query.get(card_id)
    
    if not card:
        return jsonify({'error': 'Card not found'}), 404
    
    list_obj = List.query.get(card.list_id)
    board, has_access = check_board_access(list_obj.board_id, user_id)
    
    if not has_access:
        return jsonify({'error': 'Access denied'}), 403
    
    attachment = Attachment.query.get(attachment_id)
    
    if not attachment or attachment.card_id != card_id:
        return jsonify({'error': 'Attachment not found'}), 404
    
    # Delete file from filesystem
    filepath = os.path.join(Config.UPLOAD_FOLDER, attachment.filepath)
    if os.path.exists(filepath):
        os.remove(filepath)
    
    db.session.delete(attachment)
    db.session.commit()
    
    return jsonify({'message': 'Attachment deleted successfully'}), 200

@cards_bp.route('/<int:card_id>/checklist', methods=['POST'])
@login_required
def add_checklist_item(card_id):
    """Add a checklist item to a card"""
    user_id = session['user_id']
    card = Card.query.get(card_id)
    
    if not card:
        return jsonify({'error': 'Card not found'}), 404
    
    list_obj = List.query.get(card.list_id)
    board, has_access = check_board_access(list_obj.board_id, user_id)
    
    if not has_access:
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.get_json()
    
    if not data or not data.get('title'):
        return jsonify({'error': 'Title is required'}), 400
    
    # Get next position
    max_position = db.session.query(db.func.max(ChecklistItem.position))\
        .filter_by(card_id=card_id).scalar() or -1
    
    item = ChecklistItem(
        card_id=card_id,
        title=data['title'],
        position=max_position + 1
    )
    
    db.session.add(item)
    db.session.commit()
    
    return jsonify(item.to_dict()), 201

@cards_bp.route('/<int:card_id>/checklist/<int:item_id>', methods=['PUT'])
@login_required
def update_checklist_item(card_id, item_id):
    """Update a checklist item"""
    user_id = session['user_id']
    card = Card.query.get(card_id)
    
    if not card:
        return jsonify({'error': 'Card not found'}), 404
    
    list_obj = List.query.get(card.list_id)
    board, has_access = check_board_access(list_obj.board_id, user_id)
    
    if not has_access:
        return jsonify({'error': 'Access denied'}), 403
    
    item = ChecklistItem.query.get(item_id)
    
    if not item or item.card_id != card_id:
        return jsonify({'error': 'Checklist item not found'}), 404
    
    data = request.get_json()
    
    if 'title' in data:
        item.title = data['title']
    
    if 'completed' in data:
        item.completed = data['completed']
    
    db.session.commit()
    
    return jsonify(item.to_dict()), 200

@cards_bp.route('/<int:card_id>/checklist/<int:item_id>', methods=['DELETE'])
@login_required
def delete_checklist_item(card_id, item_id):
    """Delete a checklist item"""
    user_id = session['user_id']
    card = Card.query.get(card_id)
    
    if not card:
        return jsonify({'error': 'Card not found'}), 404
    
    list_obj = List.query.get(card.list_id)
    board, has_access = check_board_access(list_obj.board_id, user_id)
    
    if not has_access:
        return jsonify({'error': 'Access denied'}), 403
    
    item = ChecklistItem.query.get(item_id)
    
    if not item or item.card_id != card_id:
        return jsonify({'error': 'Checklist item not found'}), 404
    
    db.session.delete(item)
    db.session.commit()
    
    return jsonify({'message': 'Checklist item deleted successfully'}), 200

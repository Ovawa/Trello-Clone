from flask import Blueprint, request, jsonify, session
from models import db, List, Board, BoardMember, Activity
from routes.auth import login_required
from routes.boards import check_board_access, log_activity

lists_bp = Blueprint('lists', __name__)

@lists_bp.route('', methods=['POST'])
@login_required
def create_list():
    """Create a new list"""
    data = request.get_json()
    user_id = session['user_id']
    
    if not data or not data.get('title') or not data.get('board_id'):
        return jsonify({'error': 'Title and board_id are required'}), 400
    
    board_id = data['board_id']
    board, has_access = check_board_access(board_id, user_id)
    
    if not board:
        return jsonify({'error': 'Board not found'}), 404
    
    if not has_access:
        return jsonify({'error': 'Access denied'}), 403
    
    # Get the next position
    max_position = db.session.query(db.func.max(List.position))\
        .filter_by(board_id=board_id).scalar() or -1
    
    new_list = List(
        title=data['title'],
        board_id=board_id,
        position=max_position + 1
    )
    
    db.session.add(new_list)
    
    # Log activity
    log_activity(
        board_id,
        user_id,
        'created',
        'list',
        new_list.id,
        f"added list '{new_list.title}'"
    )
    
    db.session.commit()
    
    return jsonify(new_list.to_dict()), 201

@lists_bp.route('/<int:list_id>', methods=['PUT'])
@login_required
def update_list(list_id):
    """Update a list"""
    user_id = session['user_id']
    list_obj = List.query.get(list_id)
    
    if not list_obj:
        return jsonify({'error': 'List not found'}), 404
    
    board, has_access = check_board_access(list_obj.board_id, user_id)
    
    if not has_access:
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.get_json()
    
    if 'title' in data:
        old_title = list_obj.title
        list_obj.title = data['title']
        log_activity(
            list_obj.board_id,
            user_id,
            'updated',
            'list',
            list_id,
            f"renamed list from '{old_title}' to '{list_obj.title}'"
        )
    
    if 'position' in data:
        list_obj.position = data['position']
    
    db.session.commit()
    
    return jsonify(list_obj.to_dict()), 200

@lists_bp.route('/<int:list_id>', methods=['DELETE'])
@login_required
def delete_list(list_id):
    """Delete a list"""
    user_id = session['user_id']
    list_obj = List.query.get(list_id)
    
    if not list_obj:
        return jsonify({'error': 'List not found'}), 404
    
    board, has_access = check_board_access(list_obj.board_id, user_id)
    
    if not has_access:
        return jsonify({'error': 'Access denied'}), 403
    
    # Log activity
    log_activity(
        list_obj.board_id,
        user_id,
        'deleted',
        'list',
        list_id,
        f"deleted list '{list_obj.title}'"
    )
    
    db.session.delete(list_obj)
    db.session.commit()
    
    return jsonify({'message': 'List deleted successfully'}), 200

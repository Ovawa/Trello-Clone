from flask import Blueprint, request, jsonify, session
from models import db, Board, BoardMember, User, Activity, Notification
from routes.auth import login_required
from datetime import datetime

boards_bp = Blueprint('boards', __name__)

def log_activity(board_id, user_id, action, entity_type, entity_id, description):
    """Helper function to log activities"""
    activity = Activity(
        board_id=board_id,
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        description=description
    )
    db.session.add(activity)

def check_board_access(board_id, user_id):
    """Check if user has access to board"""
    board = Board.query.get(board_id)
    if not board:
        return None, False
    
    # Owner has access
    if board.owner_id == user_id:
        return board, True
    
    # Check if user is a member
    member = BoardMember.query.filter_by(board_id=board_id, user_id=user_id).first()
    return board, member is not None

@boards_bp.route('', methods=['GET'])
@login_required
def get_boards():
    """Get all boards for current user"""
    user_id = session['user_id']
    
    # Get owned boards
    owned_boards = Board.query.filter_by(owner_id=user_id).all()
    
    # Get boards where user is a member
    memberships = BoardMember.query.filter_by(user_id=user_id).all()
    member_boards = [membership.board for membership in memberships]
    
    # Combine and remove duplicates
    all_boards = {board.id: board for board in owned_boards + member_boards}
    
    return jsonify([board.to_dict() for board in all_boards.values()]), 200

@boards_bp.route('', methods=['POST'])
@login_required
def create_board():
    """Create a new board"""
    data = request.get_json()
    user_id = session['user_id']
    
    if not data or not data.get('title'):
        return jsonify({'error': 'Title is required'}), 400
    
    board = Board(
        title=data['title'],
        description=data.get('description', ''),
        owner_id=user_id
    )
    
    db.session.add(board)
    db.session.commit()
    
    # Log activity
    log_activity(
        board.id,
        user_id,
        'created',
        'board',
        board.id,
        f"created board '{board.title}'"
    )
    db.session.commit()
    
    return jsonify(board.to_dict()), 201

@boards_bp.route('/<int:board_id>', methods=['GET'])
@login_required
def get_board(board_id):
    """Get a specific board with all its lists and cards"""
    user_id = session['user_id']
    board, has_access = check_board_access(board_id, user_id)
    
    if not board:
        return jsonify({'error': 'Board not found'}), 404
    
    if not has_access:
        return jsonify({'error': 'Access denied'}), 403
    
    return jsonify(board.to_dict(include_lists=True)), 200

@boards_bp.route('/<int:board_id>', methods=['PUT'])
@login_required
def update_board(board_id):
    """Update a board"""
    user_id = session['user_id']
    board, has_access = check_board_access(board_id, user_id)
    
    if not board:
        return jsonify({'error': 'Board not found'}), 404
    
    if not has_access:
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.get_json()
    
    if 'title' in data:
        old_title = board.title
        board.title = data['title']
        log_activity(
            board_id,
            user_id,
            'updated',
            'board',
            board_id,
            f"renamed board from '{old_title}' to '{board.title}'"
        )
    
    if 'description' in data:
        board.description = data['description']
    
    board.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify(board.to_dict()), 200

@boards_bp.route('/<int:board_id>', methods=['DELETE'])
@login_required
def delete_board(board_id):
    """Delete a board (owner only)"""
    user_id = session['user_id']
    board = Board.query.get(board_id)
    
    if not board:
        return jsonify({'error': 'Board not found'}), 404
    
    if board.owner_id != user_id:
        return jsonify({'error': 'Only the owner can delete the board'}), 403
    
    db.session.delete(board)
    db.session.commit()
    
    return jsonify({'message': 'Board deleted successfully'}), 200

@boards_bp.route('/<int:board_id>/members', methods=['GET'])
@login_required
def get_board_members(board_id):
    """Get all members of a board"""
    user_id = session['user_id']
    board, has_access = check_board_access(board_id, user_id)
    
    if not board:
        return jsonify({'error': 'Board not found'}), 404
    
    if not has_access:
        return jsonify({'error': 'Access denied'}), 403
    
    members = BoardMember.query.filter_by(board_id=board_id).all()
    
    # Include owner
    owner = User.query.get(board.owner_id)
    members_data = [{
        'user': owner.to_dict(),
        'role': 'owner',
        'joined_at': board.created_at.isoformat()
    }]
    
    members_data.extend([member.to_dict() for member in members])
    
    return jsonify(members_data), 200

@boards_bp.route('/<int:board_id>/members', methods=['POST'])
@login_required
def invite_member(board_id):
    """Invite a user to a board"""
    user_id = session['user_id']
    board = Board.query.get(board_id)
    
    if not board:
        return jsonify({'error': 'Board not found'}), 404
    
    # Only owner can invite members
    if board.owner_id != user_id:
        return jsonify({'error': 'Only the owner can invite members'}), 403
    
    data = request.get_json()
    
    if not data or not data.get('username'):
        return jsonify({'error': 'Username is required'}), 400
    
    # Find user to invite
    invite_user = User.query.filter_by(username=data['username']).first()
    
    if not invite_user:
        return jsonify({'error': 'User not found'}), 404
    
    # Check if user is already a member
    existing_member = BoardMember.query.filter_by(
        board_id=board_id,
        user_id=invite_user.id
    ).first()
    
    if existing_member:
        return jsonify({'error': 'User is already a member'}), 400
    
    # Check if user is the owner
    if invite_user.id == board.owner_id:
        return jsonify({'error': 'User is the owner of this board'}), 400
    
    # Create membership
    member = BoardMember(
        board_id=board_id,
        user_id=invite_user.id,
        role=data.get('role', 'member')
    )
    
    db.session.add(member)
    
    # Log activity
    log_activity(
        board_id,
        user_id,
        'added',
        'member',
        invite_user.id,
        f"added {invite_user.username} to the board"
    )
    
    db.session.commit()
    
    return jsonify(member.to_dict()), 201

@boards_bp.route('/<int:board_id>/members/<int:member_id>', methods=['DELETE'])
@login_required
def remove_member(board_id, member_id):
    """Remove a member from a board"""
    user_id = session['user_id']
    board = Board.query.get(board_id)
    
    if not board:
        return jsonify({'error': 'Board not found'}), 404
    
    # Only owner can remove members
    if board.owner_id != user_id:
        return jsonify({'error': 'Only the owner can remove members'}), 403
    
    member = BoardMember.query.get(member_id)
    
    if not member or member.board_id != board_id:
        return jsonify({'error': 'Member not found'}), 404
    
    removed_user = member.user
    db.session.delete(member)
    
    # Log activity
    log_activity(
        board_id,
        user_id,
        'removed',
        'member',
        removed_user.id,
        f"removed {removed_user.username} from the board"
    )
    
    db.session.commit()
    
    return jsonify({'message': 'Member removed successfully'}), 200

@boards_bp.route('/<int:board_id>/activities', methods=['GET'])
@login_required
def get_board_activities(board_id):
    """Get activity log for a board"""
    user_id = session['user_id']
    board, has_access = check_board_access(board_id, user_id)
    
    if not board:
        return jsonify({'error': 'Board not found'}), 404
    
    if not has_access:
        return jsonify({'error': 'Access denied'}), 403
    
    # Get recent activities (limit to 50)
    activities = Activity.query.filter_by(board_id=board_id)\
        .order_by(Activity.created_at.desc())\
        .limit(50)\
        .all()
    
    return jsonify([activity.to_dict() for activity in activities]), 200

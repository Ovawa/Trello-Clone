from flask import Blueprint, request, jsonify, session
from models import db, User, Card, CardAssignment
from routes.auth import login_required
from datetime import datetime

users_bp = Blueprint('users', __name__)

@users_bp.route('/search', methods=['GET'])
@login_required
def search_users():
    """Search for users by username"""
    query = request.args.get('q', '')
    
    if not query:
        return jsonify([]), 200
    
    users = User.query.filter(User.username.ilike(f'%{query}%')).limit(10).all()
    
    return jsonify([user.to_dict() for user in users]), 200

@users_bp.route('/me/tasks', methods=['GET'])
@login_required
def get_my_tasks():
    """Get all tasks assigned to the current user"""
    user_id = session['user_id']
    
    # Get all card assignments for the user
    assignments = CardAssignment.query.filter_by(user_id=user_id).all()
    
    tasks = []
    for assignment in assignments:
        card = assignment.card
        if card:
            task_data = card.to_dict()
            task_data['list'] = card.list.to_dict() if card.list else None
            task_data['board'] = card.list.board.to_dict() if card.list and card.list.board else None
            tasks.append(task_data)
    
    # Sort by due date
    tasks.sort(key=lambda x: (x['due_date'] is None, x['due_date'] or ''))
    
    return jsonify(tasks), 200

@users_bp.route('/me/calendar', methods=['GET'])
@login_required
def get_calendar_tasks():
    """Get tasks for calendar view"""
    user_id = session['user_id']
    
    # Get month and year from query params
    month = request.args.get('month', datetime.utcnow().month, type=int)
    year = request.args.get('year', datetime.utcnow().year, type=int)
    
    # Get all assignments for the user
    assignments = CardAssignment.query.filter_by(user_id=user_id).all()
    
    calendar_tasks = []
    for assignment in assignments:
        card = assignment.card
        if card and card.due_date:
            # Filter by month and year
            if card.due_date.month == month and card.due_date.year == year:
                task_data = {
                    'id': card.id,
                    'title': card.title,
                    'due_date': card.due_date.isoformat(),
                    'completed': card.completed,
                    'board_id': card.list.board_id if card.list else None,
                    'board_title': card.list.board.title if card.list and card.list.board else None
                }
                calendar_tasks.append(task_data)
    
    return jsonify(calendar_tasks), 200

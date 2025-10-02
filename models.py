from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    owned_boards = db.relationship('Board', backref='owner', lazy=True, foreign_keys='Board.owner_id')
    board_memberships = db.relationship('BoardMember', backref='user', lazy=True, cascade='all, delete-orphan')
    card_assignments = db.relationship('CardAssignment', backref='user', lazy=True, cascade='all, delete-orphan')
    activities = db.relationship('Activity', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat()
        }


class Board(db.Model):
    __tablename__ = 'boards'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    lists = db.relationship('List', backref='board', lazy=True, cascade='all, delete-orphan', order_by='List.position')
    members = db.relationship('BoardMember', backref='board', lazy=True, cascade='all, delete-orphan')
    activities = db.relationship('Activity', backref='board', lazy=True, cascade='all, delete-orphan', order_by='Activity.created_at.desc()')
    
    def to_dict(self, include_lists=False):
        data = {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'owner_id': self.owner_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
        if include_lists:
            data['lists'] = [lst.to_dict(include_cards=True) for lst in self.lists]
        return data


class BoardMember(db.Model):
    __tablename__ = 'board_members'
    
    id = db.Column(db.Integer, primary_key=True)
    board_id = db.Column(db.Integer, db.ForeignKey('boards.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    role = db.Column(db.String(20), default='member')  # owner, admin, member
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Unique constraint to prevent duplicate memberships
    __table_args__ = (db.UniqueConstraint('board_id', 'user_id', name='_board_user_uc'),)
    
    def to_dict(self):
        return {
            'id': self.id,
            'board_id': self.board_id,
            'user_id': self.user_id,
            'user': self.user.to_dict() if self.user else None,
            'role': self.role,
            'joined_at': self.joined_at.isoformat()
        }


class List(db.Model):
    __tablename__ = 'lists'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    board_id = db.Column(db.Integer, db.ForeignKey('boards.id'), nullable=False)
    position = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    cards = db.relationship('Card', backref='list', lazy=True, cascade='all, delete-orphan', order_by='Card.position')
    
    def to_dict(self, include_cards=False):
        data = {
            'id': self.id,
            'title': self.title,
            'board_id': self.board_id,
            'position': self.position,
            'created_at': self.created_at.isoformat()
        }
        if include_cards:
            data['cards'] = [card.to_dict() for card in self.cards]
        return data


class Card(db.Model):
    __tablename__ = 'cards'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    list_id = db.Column(db.Integer, db.ForeignKey('lists.id'), nullable=False)
    position = db.Column(db.Integer, default=0)
    due_date = db.Column(db.DateTime, nullable=True)
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    assignments = db.relationship('CardAssignment', backref='card', lazy=True, cascade='all, delete-orphan')
    attachments = db.relationship('Attachment', backref='card', lazy=True, cascade='all, delete-orphan')
    checklists = db.relationship('ChecklistItem', backref='card', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'list_id': self.list_id,
            'position': self.position,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'completed': self.completed,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'assignments': [a.to_dict() for a in self.assignments],
            'attachments': [att.to_dict() for att in self.attachments],
            'checklists': [item.to_dict() for item in self.checklists]
        }


class CardAssignment(db.Model):
    __tablename__ = 'card_assignments'
    
    id = db.Column(db.Integer, primary_key=True)
    card_id = db.Column(db.Integer, db.ForeignKey('cards.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Unique constraint to prevent duplicate assignments
    __table_args__ = (db.UniqueConstraint('card_id', 'user_id', name='_card_user_uc'),)
    
    def to_dict(self):
        return {
            'id': self.id,
            'card_id': self.card_id,
            'user_id': self.user_id,
            'user': self.user.to_dict() if self.user else None,
            'assigned_at': self.assigned_at.isoformat()
        }


class Attachment(db.Model):
    __tablename__ = 'attachments'
    
    id = db.Column(db.Integer, primary_key=True)
    card_id = db.Column(db.Integer, db.ForeignKey('cards.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    filepath = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'card_id': self.card_id,
            'filename': self.filename,
            'filepath': self.filepath,
            'file_size': self.file_size,
            'uploaded_at': self.uploaded_at.isoformat()
        }


class ChecklistItem(db.Model):
    __tablename__ = 'checklist_items'
    
    id = db.Column(db.Integer, primary_key=True)
    card_id = db.Column(db.Integer, db.ForeignKey('cards.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    position = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'card_id': self.card_id,
            'title': self.title,
            'completed': self.completed,
            'position': self.position,
            'created_at': self.created_at.isoformat()
        }


class Activity(db.Model):
    __tablename__ = 'activities'
    
    id = db.Column(db.Integer, primary_key=True)
    board_id = db.Column(db.Integer, db.ForeignKey('boards.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    action = db.Column(db.String(50), nullable=False)  # created, updated, deleted, moved, etc.
    entity_type = db.Column(db.String(50), nullable=False)  # board, list, card, etc.
    entity_id = db.Column(db.Integer)
    description = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'board_id': self.board_id,
            'user_id': self.user_id,
            'user': self.user.to_dict() if self.user else None,
            'action': self.action,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'description': self.description,
            'created_at': self.created_at.isoformat()
        }


class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(50), default='info')  # info, invite, assignment, due_date
    related_board_id = db.Column(db.Integer, db.ForeignKey('boards.id'), nullable=True)
    related_card_id = db.Column(db.Integer, db.ForeignKey('cards.id'), nullable=True)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='notifications', foreign_keys=[user_id])
    board = db.relationship('Board', foreign_keys=[related_board_id])
    card = db.relationship('Card', foreign_keys=[related_card_id])
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'message': self.message,
            'type': self.type,
            'related_board_id': self.related_board_id,
            'related_card_id': self.related_card_id,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat()
        }

from flask import Flask, render_template, session, redirect, url_for
from config import Config
from models import db
import os

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    
    # Initialize config
    Config.init_app(app)
    
    # Register blueprints
    from routes.auth import auth_bp
    from routes.boards import boards_bp
    from routes.lists import lists_bp
    from routes.cards import cards_bp
    from routes.users import users_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(boards_bp, url_prefix='/api/boards')
    app.register_blueprint(lists_bp, url_prefix='/api/lists')
    app.register_blueprint(cards_bp, url_prefix='/api/cards')
    app.register_blueprint(users_bp, url_prefix='/api/users')
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    # Main routes
    @app.route('/')
    def index():
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return render_template('dashboard.html')
    
    @app.route('/board/<int:board_id>')
    def board(board_id):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return render_template('board.html', board_id=board_id)
    
    @app.route('/profile')
    def profile():
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return render_template('profile.html')
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)

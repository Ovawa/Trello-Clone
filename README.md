#Boardify - Trello Clone

A full-featured project management tool built with Flask and SQLAlchemy, inspired by Trello.

## Features

### Core Functionality
- **Boards, Lists, and Cards**: Organize your projects with a Kanban-style interface
- **Drag and Drop**: Move cards between lists seamlessly
- **User Authentication**: Secure login and registration system
- **Board Collaboration**: Invite team members to collaborate on boards

### Card Features
- ✅ **Checklists**: Add task items with checkboxes that can be marked complete
- 📅 **Due Dates**: Set deadlines for cards with visual indicators for overdue/due soon
- 📎 **File Attachments**: Upload files to cards (up to 16MB)
- 👤 **User Assignments**: Assign team members to specific cards
- 📝 **Descriptions**: Add detailed descriptions to cards

### Additional Features
- **Activity Log**: Track all changes and actions on each board
- **User Profile**: View all assigned tasks in one place
- **Calendar View**: See tasks by due date in a calendar format
- **Modern UI**: Beautiful, responsive design with smooth animations

## Tech Stack

- **Backend**: Flask, SQLAlchemy
- **Database**: SQLite (easily switchable to PostgreSQL)
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Authentication**: Session-based with secure password hashing

## Installation

1. **Clone or navigate to the project directory**:
   ```bash
   cd Boardify
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python app.py
   ```

4. **Access the application**:
   Open your browser and navigate to `http://localhost:6000`

## Usage

### Getting Started
1. Register a new account or login
2. Create your first board
3. Add lists (e.g., "To Do", "In Progress", "Done")
4. Add cards to your lists
5. Invite team members to collaborate

### Managing Cards
- Click on a card to open the detail modal
- Add descriptions, checklists, due dates, and attachments
- Assign users to cards
- Drag and drop cards between lists

### Collaboration
- Invite users by username from the board page
- View all board members
- Track team activity in the activity log

### Profile & Calendar
- View all your assigned tasks in the Profile page
- Use the calendar to see tasks by due date
- Click on any task to navigate to its board

## Project Structure

```
Boardify/
├── app.py                 # Main application file
├── config.py             # Configuration settings
├── models.py             # Database models
├── requirements.txt      # Python dependencies
├── routes/
│   ├── auth.py          # Authentication routes
│   ├── boards.py        # Board management routes
│   ├── lists.py         # List management routes
│   ├── cards.py         # Card management routes
│   └── users.py         # User-related routes
├── templates/
│   ├── base.html        # Base template
│   ├── login.html       # Login page
│   ├── register.html    # Registration page
│   ├── dashboard.html   # Boards dashboard
│   ├── board.html       # Board view
│   └── profile.html     # User profile
├── static/
│   ├── css/
│   │   └── style.css    # Main stylesheet
│   └── js/
│       ├── utils.js     # Utility functions
│       ├── dashboard.js # Dashboard functionality
│       ├── board.js     # Board functionality
│       └── profile.js   # Profile functionality
└── uploads/             # File attachments storage
```

## Database Schema

- **Users**: User accounts with authentication
- **Boards**: Project boards owned by users
- **BoardMembers**: Many-to-many relationship for board access
- **Lists**: Columns within boards
- **Cards**: Tasks within lists
- **CardAssignments**: User assignments to cards
- **Attachments**: File uploads linked to cards
- **ChecklistItems**: Task items within cards
- **Activity**: Audit log of all board actions

## API Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login
- `POST /auth/logout` - Logout
- `GET /auth/me` - Get current user

### Boards
- `GET /api/boards` - Get all boards
- `POST /api/boards` - Create board
- `GET /api/boards/<id>` - Get board details
- `PUT /api/boards/<id>` - Update board
- `DELETE /api/boards/<id>` - Delete board
- `GET /api/boards/<id>/members` - Get board members
- `POST /api/boards/<id>/members` - Invite member
- `DELETE /api/boards/<id>/members/<id>` - Remove member
- `GET /api/boards/<id>/activities` - Get activity log

### Lists
- `POST /api/lists` - Create list
- `PUT /api/lists/<id>` - Update list
- `DELETE /api/lists/<id>` - Delete list

### Cards
- `POST /api/cards` - Create card
- `GET /api/cards/<id>` - Get card details
- `PUT /api/cards/<id>` - Update card
- `DELETE /api/cards/<id>` - Delete card
- `POST /api/cards/<id>/assignments` - Assign user
- `DELETE /api/cards/<id>/assignments/<id>` - Unassign user
- `POST /api/cards/<id>/attachments` - Upload file
- `DELETE /api/cards/<id>/attachments/<id>` - Delete file
- `POST /api/cards/<id>/checklist` - Add checklist item
- `PUT /api/cards/<id>/checklist/<id>` - Update checklist item
- `DELETE /api/cards/<id>/checklist/<id>` - Delete checklist item

### Users
- `GET /api/users/search` - Search users
- `GET /api/users/me/tasks` - Get assigned tasks
- `GET /api/users/me/calendar` - Get calendar tasks

## Security Features

- Password hashing with Werkzeug
- Session-based authentication
- CSRF protection ready
- SQL injection prevention via SQLAlchemy ORM
- XSS prevention with proper escaping
- File upload validation

## Configuration

Edit `config.py` to customize:
- Database URL
- Secret key
- Upload folder location
- Max file size
- Allowed file extensions

## Future Enhancements

- Real-time updates with WebSockets
- Email notifications
- Card labels and colors
- Board templates
- Advanced search and filtering
- Export boards to JSON/CSV
- Mobile app

## License

This project is open source and available for educational purposes.

## Author

Built as a demonstration of Flask, SQLAlchemy, and modern web development practices.

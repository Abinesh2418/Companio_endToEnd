# AI Companio - Digital Student Companion

A full-stack web application for goal management, intelligent task breakdown, and student productivity enhancement, built for Microsoft Imagine Cup.

## Project Structure

```
├── backend/          # FastAPI backend server
│   ├── main.py      # Main API server
│   ├── database.py  # PostgreSQL database configuration
│   ├── init_db.py   # Database initialization script
│   ├── ai/          # AI-powered features
│   │   ├── task_decomposer.py      # Intelligent task generation
│   │   ├── reminder_generator.py    # Smart reminder system
│   │   └── productivity_analyzer.py # Activity tracking
│   ├── models/      # SQLAlchemy & Pydantic models
│   │   ├── user.py        # User authentication
│   │   ├── goal.py        # Goal management
│   │   ├── task.py        # Task breakdown
│   │   └── productivity.py # Reminders & analytics
│   └── data/        # Data files
└── frontend/         # React + TypeScript frontend
    └── src/
        ├── components/  # Reusable UI components
        │   ├── Auth.tsx             # Login/Register
        │   ├── Layout.tsx           # App layout with sidebar
        │   ├── GoalsManagement.tsx  # Goal creation & management
        │   ├── TaskBreakdown.tsx    # Task breakdown & customization
        │   └── ProductivityMotivation.tsx # Smart reminders
        ├── pages/       # Feature pages
        └── context/     # React context (Authentication)
```

## Backend Setup

### Prerequisites
- Python 3.8+
- PostgreSQL 12+
- pip

### Installation

1. Navigate to the backend directory:
```bash
cd backend
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up PostgreSQL database:
   - Create a database named `companio`
   - Update database credentials in `database.py` if needed

4. Initialize the database:
```bash
python init_db.py
```

5. Run the server:
```bash
python main.py
```

Or using uvicorn directly:
```bash
uvicorn main:app --reload --port 8000
```

The backend server will run at `http://localhost:8000`

## Frontend Setup

### Prerequisites
- Node.js 16+
- npm or yarn

### Installation

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Run the development server:
```bash
npm run dev
```

The frontend will run at `http://localhost:5173`

## API Endpoints

### Health Check
- `GET /` - Server health status

### Authentication
- `POST /api/register` - Register new user
- `POST /api/login` - User login (session-based)
- `POST /api/logout` - User logout
- `GET /api/user` - Get current user info

### Goals
- `POST /api/goals` - Create a new goal
- `GET /api/goals` - Get all goals for user
- `GET /api/goals/{goal_id}` - Get specific goal
- `PUT /api/goals/{goal_id}` - Update a goal
- `DELETE /api/goals/{goal_id}` - Delete a goal

### Tasks (Intelligent Task Breakdown)
- `POST /api/goals/{goal_id}/tasks/generate` - Generate tasks for a goal
- `GET /api/goals/{goal_id}/tasks` - Get all tasks for a goal
- `GET /api/tasks/{task_id}` - Get specific task
- `PUT /api/tasks/{task_id}` - Update task details
- `POST /api/goals/{goal_id}/tasks` - Create custom task
- `DELETE /api/tasks/{task_id}` - Delete a task
- `POST /api/goals/{goal_id}/tasks/reorder` - Bulk reorder tasks

### Productivity & Reminders
- `POST /api/productivity/daily-checkin` - Generate daily check-in reminder (once per day)
- `POST /api/productivity/reminders/generate` - Generate smart contextual reminders
- `GET /api/productivity/reminders` - Get all reminders for user
- `DELETE /api/productivity/reminders/{reminder_id}` - Delete a reminder

### Example: Create Goal

```json
POST /api/goals
{
  "title": "Learn React",
  "duration_weeks": 3,
  "priority": "High",
  "intensity": "Normal"
}
```

Response:
```json
{
  "id": "uuid-here",
  "title": "Learn React",
  "duration_weeks": 3,
  "priority": "High",
  "intensity": "Normal",
  "start_date": "2025-12-14T10:30:00",
  "end_date": "2026-01-04T10:30:00",
  "created_at": "2025-12-14T10:30:00"
}
```

### Example: Generate Tasks

```json
POST /api/goals/{goal_id}/tasks/generate
```

Response:
```json
{
  "goal_id": "uuid-here",
  "goal_title": "Learn React",
  "tasks": [
    {
      "task": {
        "id": "task-uuid-1",
        "goal_id": "uuid-here",
        "week_number": 1,
        "title": "JSX Syntax",
        "status": "Not Started",
        "dependencies": [],
        "order": 0
      },
      "is_locked": false
    }
  ],
  "total_tasks": 9
}
```

## Features

### 1. User Authentication
- Secure session-based authentication
- PostgreSQL-backed user storage
- SHA-256 password hashing
- Login/logout with session tracking

### 2. Goal Management
- Create, view, edit, and delete learning goals
- Set goal duration (weeks), priority, and intensity
- Track goal progress and completion dates
- User-specific goal isolation

### 3. Intelligent Task Breakdown & Customization
- **AI-Powered Task Generation**: Automatically decompose goals into structured weekly tasks
- **Rule-based Intelligence**: Task generation based on goal topic and learning paths
- **Full Customization Suite**:
  - Edit task titles and descriptions inline
  - Reorder tasks with up/down arrows
  - Move tasks between weeks
  - Delete unwanted tasks
  - Add new custom tasks
- **Smart Dependencies**: Task locking based on prerequisites
- **Status Tracking**: Not Started, In Progress, Completed
- **Multi-Topic Support**: React, Python, JavaScript, Data Structures, and more
- **Intensity Levels**:
  - Light: 2 tasks/week
  - Normal: 3 tasks/week
  - Aggressive: 4 tasks/week

### 4. Productivity & Motivation
- **Smart Reminders**: Context-aware reminders based on goals and tasks
- **Daily Check-in**: Once-per-day motivation and progress tracking
- **Live Clock**: Real-time date and time display
- **Activity Monitoring**: Track user productivity patterns

### 5. Modern UI/UX
- React-based responsive interface
- Dark mode support across all components
- Sidebar navigation with feature organization
- Real-time updates and notifications
- Smooth animations and transitions

## Development

- Backend API docs available at: `http://localhost:8000/docs`
- Frontend hot-reload enabled for development
- CORS configured for local development
- PostgreSQL database with SQLAlchemy ORM
- UTC time handling with automatic timezone conversion

## Technology Stack

**Backend:**
- FastAPI - Modern async web framework
- PostgreSQL - Relational database
- SQLAlchemy - ORM for database operations
- Pydantic - Data validation
- Python 3.8+

**Frontend:**
- React 18 - UI library
- TypeScript - Type-safe JavaScript
- Vite - Fast build tool
- CSS3 - Custom styling with dark mode

**Authentication:**
- Session-based auth
- SHA-256 password hashing
- Secure cookie handling

## Project Status

This is an active Microsoft Imagine Cup project focused on enhancing student productivity through intelligent goal management and AI-powered task breakdown.

## License

Microsoft Imagine Cup Project

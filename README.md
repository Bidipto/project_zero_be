<div align="center">
  <img src="https://readme-typing-svg.herokuapp.com?font=Fira+Code&size=24&duration=3000&pause=1000&color=FFD700&center=true&vCenter=true&width=500&lines=🍍+pineapples+brewing...+🍍;Welcome+to+ProjectX+Backend!;FastAPI+%2B+SQLite+%2B+JWT+Auth" alt="Typing SVG" />
</div>

---

# ProjectX Backend - FastAPI Chat Application

A modern, real-time chat application backend built with FastAPI, featuring user authentication, private messaging, and GitHub OAuth integration.

## 🚀 Features

### 🔐 Authentication & Authorization
- **JWT Token-based Authentication** - Secure user sessions
- **Password Hashing** - bcrypt encryption for user passwords
- **GitHub OAuth Integration** - Social login with GitHub
- **Protected Routes** - Middleware-based route protection

### 💬 Chat System
- **Private Messaging** - One-on-one conversations between users
- **Real-time Chat Management** - Create, retrieve, and manage chats
- **Message Tracking** - Read/unread status, message timestamps
- **User Discovery** - Get list of available users for messaging

### 🛠️ Technical Features
- **FastAPI Framework** - Modern, fast web framework for building APIs
- **SQLite Database** - Lightweight, serverless database with SQLAlchemy ORM
- **CORS Support** - Cross-Origin Resource Sharing for frontend integration
- **Structured Logging** - Comprehensive logging with colorlog
- **Docker Support** - Containerized deployment ready
- **Pydantic Validation** - Request/response data validation

## 📁 Project Structure

```
project_zero_be/
├── pz_be_services/          # Main application directory
│   ├── main.py              # FastAPI application entry point
│   ├── core/                # Core utilities and configuration
│   │   ├── auth.py          # JWT authentication utilities
│   │   ├── config.py        # Environment variables and settings
│   │   ├── logger.py        # Logging configuration
│   │   └── password.py      # Password hashing utilities
│   ├── db/                  # Database layer
│   │   ├── database.py      # Database connection and setup
│   │   ├── models.py        # SQLAlchemy ORM models
│   │   └── crud/           # Database operations
│   │       ├── crud_user.py
│   │       ├── crud_chat.py
│   │       ├── crud_message.py
│   │       └── crud_password.py
│   ├── routers/            # API route handlers
│   │   └── v1/             # API version 1
│   │       ├── health_router.py    # Health check endpoints
│   │       ├── user_router.py      # User authentication & management
│   │       └── chat_router.py      # Chat and messaging endpoints
│   ├── schemas/            # Pydantic models for request/response
│   │   ├── user.py
│   │   ├── chat.py
│   │   └── message.py
│   └── services/           # Business logic layer
│       ├── user_auth_services/
│       └── chat_services/
├── requirements.txt        # Python dependencies
├── Dockerfile             # Docker container configuration
├── compose.yaml          # Docker Compose setup
└── README.md            # This file
```

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.11+
- pip (Python package manager)
- Git

### 1. Clone the Repository
```bash
git clone <repository-url>
cd project_zero_be
```

### 2. Create Virtual Environment
```powershell
python -m venv venv
venv\Scripts\activate  # Windows
# or
source venv/bin/activate  # Linux/Mac
```

### 3. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 4. Environment Configuration
Create a `.env` file in the root directory:
```env
# Database
SQLALCHEMY_DATABASE_URL=sqlite:///./ProjectX.db

# JWT Configuration
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
MIDDLEWARE_SECRET_KEY=your-middleware-secret-key

# GitHub OAuth (Optional)
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret

# URLs
FRONTEND_URL=http://localhost:3000
BACKEND_URL=http://localhost:8000
```

### 5. Run the Application
```powershell
fastapi dev pz_be_services\main.py
```

The API will be available at: http://localhost:8000

## 🐳 Docker Deployment

### Build and Run with Docker Compose
```bash
docker compose up --build
```

### Build Docker Image Manually
```bash
docker build -t projectx-backend .
docker run -p 8000:8000 projectx-backend
```

## 📚 API Documentation

Once the server is running, access the interactive API documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔗 API Endpoints

### Health Check
- `GET /v1/health` - Application health status

### User Authentication
- `POST /v1/user/register` - Register new user
- `POST /v1/user/login` - User login
- `GET /v1/user/login/github` - GitHub OAuth login
- `GET /v1/user/auth/github/callback` - GitHub OAuth callback
- `GET /v1/user/usernames` - Get list of all usernames

### Chat Management
- `POST /v1/chat/private` - Create or get private chat
- `GET /v1/chat/private` - Get user's private chats
- `GET /v1/chat/private/{chat_id}` - Get specific chat by ID

### Messaging
- `GET /v1/chat/{chat_id}/messages` - Get chat messages
- `POST /v1/chat/{chat_id}/messages` - Send message to chat
- `POST /v1/chat/{chat_id}/messages/mark-read` - Mark messages as read
- `GET /v1/chat/{chat_id}/messages/unread-count` - Get unread message count

## 🗄️ Database Schema

### Users Table
- `id` (Primary Key)
- `username` (Unique)
- `email` (Optional, Unique)
- `full_name` (Optional)
- `is_active` (Boolean)
- `created_at`, `updated_at` (Timestamps)

### Chats Table
- `id` (Primary Key)
- `title` (Optional)
- `chat_type` (private/group)
- `is_active` (Boolean)
- `created_at`, `updated_at`, `last_message_at` (Timestamps)

### Messages Table
- `id` (Primary Key)
- `chat_id` (Foreign Key)
- `sender_id` (Foreign Key)
- `content` (Text)
- `message_type` (text/image/file)
- `timestamp`, `is_read`, `is_edited` (Status fields)

### User Passwords Table
- `id` (Primary Key)
- `user_id` (Foreign Key)
- `hashed_password` (Encrypted)

## 🔧 Development

### Update Dependencies
```powershell
pip freeze > requirements.txt
```

### Database Operations
The application automatically creates database tables on startup. Database files:
- `ProjectX.db` - Main application database

### Logging
Application logs are stored in:
- `pz_be_services/logs/app.log` - Application logs
- `pz_be_services/logs/db.log` - Database operation logs

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License.

## 🛟 Support

For support, please create an issue in the repository or contact the development team.

---

<div align="center">
  <p>Built with ❤️ using FastAPI</p>
  <p>🍍 Happy Coding! 🍍</p>
</div>
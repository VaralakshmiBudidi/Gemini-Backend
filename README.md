# Gemini Backend

A modern, scalable backend API built with FastAPI that integrates Google's Gemini AI for intelligent chat functionality. This application provides user authentication, chatroom management, AI-powered conversations, and subscription handling with Stripe integration.

## 🚀 Features

### Core Functionality
- **User Authentication & Authorization**: Secure JWT-based authentication system
- **AI-Powered Chat**: Integration with Google Gemini 2.5 Flash for intelligent responses
- **Chatroom Management**: Create, join, and manage chat conversations
- **Real-time Messaging**: Redis-powered message handling and caching
- **Subscription System**: Pro tier management with Stripe payment processing
- **Rate Limiting**: Tier-based rate limiting for Basic and Pro users

### Technical Stack
- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Caching**: Redis for session management and caching
- **Authentication**: JWT tokens with bcrypt password hashing
- **AI Integration**: Google Generative AI (Gemini 2.5 Flash)
- **Payment Processing**: Stripe API integration
- **Deployment**: Render cloud platform

## 📋 Prerequisites

Before running this application, ensure you have:

- Python 3.11 or higher
- PostgreSQL database
- Redis server
- Google Gemini API key
- Stripe account and API keys

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Gemini-Backend
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv gvenv
   source gvenv/bin/activate  # On Windows: gvenv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a .env file from .env.example and mention your creds there.

5. **Initialize the database**
   The application will automatically create database tables on startup.

## 🚀 Running the Application

### Development Mode
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000` (development) or `http://localhost:10000` (production).

## 📚 API Documentation

Once the application is running, you can access:
- **Interactive API Documentation**: Available at `/docs` (Swagger UI)
- **Alternative Documentation**: Available at `/redoc` (ReDoc)

## 🏗️ Project Structure

```
Gemini-Backend/
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── models.py            # SQLAlchemy database models
│   ├── schemas.py           # Pydantic data validation schemas
│   ├── dependencies.py      # Database and dependency injection
│   ├── routes/              # API route handlers
│   │   ├── auth.py         # Authentication endpoints
│   │   ├── user.py         # User management endpoints
│   │   ├── chatroom.py     # Chatroom and messaging endpoints
│   │   ├── stripe.py       # Stripe payment endpoints
│   │   └── subscription.py # Subscription management endpoints
│   └── utils/
│       └── gemini.py       # Gemini AI integration utilities
├── requirements.txt         # Python dependencies
├── render.yaml             # Render deployment configuration
└── README.md              # This file
```

## 🔐 Authentication

The application uses JWT (JSON Web Tokens) for authentication. Users can:
- Register with mobile number and password
- Login to receive JWT tokens
- Access protected endpoints using Bearer token authentication

## 💬 Chat Features

### Chatroom Management
- Create new chatrooms
- Join existing chatrooms
- Send messages to chatrooms
- Receive AI-powered responses from Gemini

### AI Integration
- Powered by Google Gemini 2.5 Flash
- Context-aware conversations
- Intelligent response generation
- Rate limiting based on user tier

## 💳 Subscription System

### User Tiers
- **Basic**: Limited message rate
- **Pro**: Enhanced features and higher rate limits

### Payment Processing
- Stripe integration for secure payments
- Subscription management
- Payment history tracking

## 🚀 Deployment

This application is configured for deployment on Render. The `render.yaml` file contains the deployment configuration including:
- Python 3.11 runtime
- Environment variable configuration
- Build and start commands

## 🔧 Development

### Running Tests
```bash
python test-models.py
python test-redis.py
```

### Database Migrations
The application uses SQLAlchemy with automatic table creation. For production, consider using Alembic for database migrations.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Check the API documentation at `/docs`
- Review the project structure and code comments
- Open an issue on the repository

## Application Link

   https://gemini-backend-85ypdfvb.vercel.app/docs

## 🔮 Future Enhancements

- WebSocket support for real-time messaging
- File upload and sharing capabilities
- Advanced AI model selection
- Enhanced analytics and monitoring
- Multi-language support

Flea Market Application
This repository hosts a full-stack web application designed for a digital flea market, enabling users to post items for exchange and manage requests.

Project Overview
The Flea Market application facilitates a community-driven exchange of goods, promoting reuse and sustainability. It offers functionalities for user authentication, item listing, and a robust request management system, complemented by an administrative interface.

Key Features
User Authentication: Secure registration, login, and session management (JWT).

Item Management: Users can post items with details and images; browse and view items posted by others.

Item Request System: Users can send, view, accept, and reject requests for items.

Role-Based Access Control: Differentiated functionalities for regular users and administrators.

Admin Panel: Comprehensive management of users and all item requests within the system.

Responsive UI: Optimized for various devices using modern web technologies.

Technologies Used
The application employs a decoupled architecture with a Flask API backend and a React.js frontend.

Backend (API)
Python, Flask: Core API framework.

Flask-SQLAlchemy, PostgreSQL: Database ORM and persistent storage.

Flask-JWT-Extended, Flask-Bcrypt: Authentication and secure password handling.

Flask-CORS: Cross-origin request management.

Frontend (User Interface)
React.js, Vite: UI library and build tool.

Axios: HTTP client for API communication.

Tailwind CSS: Utility-first CSS framework for styling.

Local Development Setup
To run the application locally:

Clone the repository:

git clone https://github.com/BrianTallam2025/phase4proj-fleemrkt.git
cd phase4proj-fleemrkt

Backend Setup:

Navigate to backend/.

Install dependencies: pipenv install (ensure pipenv is installed).

Activate environment: pipenv shell.

Create .env with SECRET_KEY, JWT_SECRET_KEY, DATABASE_URL (e.g., sqlite:///site.db), and FLASK_APP=app.py.

Run migrations: flask db upgrade.

Start server: gunicorn app:app (or flask run). Backend runs on http://localhost:5000.

Frontend Setup:

Navigate to frontend/.

Install dependencies: npm install.

Create .env with VITE_API_BASE_URL=http://localhost:5000/api.

Start server: npm run dev. Frontend runs on http://localhost:5173.

Deployment
The application is deployed with the backend API on Render and the frontend UI on Vercel, leveraging environment variables for configuration.
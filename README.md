markdown
# 🛒 Flask E-Commerce API

A full-featured RESTful API for an e-commerce platform built with Flask, featuring user authentication, product management, shopping cart, offers, and image uploads.

## 🚀 Features

- **User Authentication**: JWT-based auth with access and refresh tokens
- **Product Management**: CRUD operations with category filtering
- **Shopping Cart**: Add, update, and checkout items
- **Offers & Discounts**: Time-based discount system (up to 20%)
- **Image Uploads**: Profile pictures and product images
- **Admin Panel**: Admin-only endpoints for managing products and offers

## 🛠️ Tech Stack

- **Framework**: Flask 3.x
- **Database**: SQLAlchemy (SQLite for dev, PostgreSQL-ready)
- **Authentication**: Flask-JWT-Extended
- **Validation**: Marshmallow
- **Password Hashing**: Flask-Bcrypt
- **File Handling**: Werkzeug

## 📦 Installation

### Prerequisites
- Python 3.8+
- pip
- virtualenv (recommended)

### Setup

1. **Clone the repository**
```bash
   git clone https://github.com/yourusername/flask-ecommerce.git
   cd flask-ecommerce
```

2. **Create virtual environment**
```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # macOS/Linux
   source .venv/bin/activate
```

3. **Install dependencies**
```bash
   pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
   # Create .env file
   touch .env
```
   
   Add to `.env`:
DATABASE_URL=sqlite:///ecommerce.db
JWT_SECRET_KEY=your-secret-key-here
ADMIN_PASSWORD=admin123


5. **Create required folders**
```bash
   mkdir -p static/users static/products
```

6. **Run the application**
```bash
   python app.py
```
# For any new interns, the following are the steps how approached to make this project

## Topics covered in Week 1:
- working with lower framework first like Flask
- learning why django chose MVT approach and what DRF solved in Django?
- learning different types of APIS
- What not to push in git

## Topics covered in Week 2:
- JSON format: 
- JWT authentication token
- Session based authentication
- Web services
- REST 
- RPC
- ODoo
- Task to build this api using Flask using jwt(token-based) authentication, using Insomnia as api client, build- CRUD (e-commerce service: product, order, cart, etc..)
- Following DRY and SOLID principles

## Topics covered in Week 3:
- use python error handling (try, except)
- use serializer (Marshmallow)
- research on date-time, timezone, timedelta, dst, utc, timezones
- adding featuring in this api: "Offer" service where comparing date-time between client and server (how to handle date-time between them)
- simply saying "a client choosing a product with an offer valid from a certain time range"
- using class-based views (MethodView)  
- Also adding "Categories" service 

## Topics covered in Week 4:
- Uploading image files in this api, (see the documentation of flask for uploading files)





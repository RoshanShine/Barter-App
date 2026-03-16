# Barter App

A Django-based web application for bartering products. Users can list products for exchange (money, barter, or both), browse products by category, and search for specific items.

## Features
- **Product Listing**: Users can add products with images, descriptions, and locations.
- **Categorization**: Browse products by categories like Mobiles, Electronics, Furniture, etc.
- **Search**: Search for products by name, description, location, or condition.
- **Barter Options**: Flexible exchange types - Money Only, Barter Only, or Both.
- **User Authentication**: Register and login to manage your listings.

## Setup Instructions

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd Barter-App
   ```

2. **Create and Activate Virtual Environment**:
   - **Windows**:
     ```bash
     python -m venv venv
     .\venv\Scripts\activate
     ```
   - **macOS/Linux**:
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Initialize the database**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

4. **Run the development server**:
   ```bash
   python manage.py runserver
   ```

5. **Access the application**:
   Open your browser and go to `http://127.0.0.1:8000/`.

## Technology Stack
- **Backend**: Django (Python)
- **Database**: SQLite3
- **Frontend**: Django Templates (HTML/CSS)
- **Image Processing**: Pillow

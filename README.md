# My Django App

This is a Django web application project.

## Setup Instructions (Local)

1. **Clone the repository:**
   ```
   git clone https://github.com/ReddyOrNotHereICode/Django.git
   cd Django
   ```

2. **Create a virtual environment:**
   ```
   python -m venv venv
   venv\Scripts\activate  # On Windows
   # or
   source venv/bin/activate  # On macOS/Linux
   ```

3. **Install the requirements:**
   ```
   pip install -r requirements.txt
   ```

4. **Run the migrations:**
   ```
   python manage.py migrate
   ```

5. **Start the development server:**
   ```
   python manage.py runserver
   ```

## Running with Docker

1. **Build and start the containers:**
   ```
   docker-compose up --build
   ```

2. **Access the application:**
   Open [http://localhost:8000/](http://localhost:8000/) in your web browser.

## Usage

Access the application by navigating to `http://127.0.0.1:8000/` in your web browser.

## Contributing

Feel free to submit issues or pull requests for improvements and bug fixes.
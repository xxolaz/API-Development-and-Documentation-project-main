# Trivia API Backend

## Overview

This project is the backend server for a trivia web application. It provides a set of API endpoints to serve trivia questions, manage the question database, and power a quiz game.

## Getting Started

### Prerequisites

- Python 3.7+
- Virtual Environment (`venv`)
- PostgreSQL

### Installing Dependencies and Setup

1.  **Clone the Repository**
    ```bash
    git clone 
    cd cd0037-API-Development-and-Documentation-project
    ```

2.  **Set up the Virtual Environment**
    From the project root directory:
    ```bash
    # On Mac/Linux
    python3 -m venv venv
    source venv/bin/activate

    # On Windows
    python -m venv venv
    .\venv\Scripts\activate
    ```

3.  **Install Backend Dependencies**
    Navigate to the `backend` directory and install dependencies:
    ```bash
    cd backend
    pip install -r requirements.txt
    ```

4.  **Set Up the Database**
    Make sure your PostgreSQL server is running. Then, create and populate the databases:
    ```bash
    createdb trivia
    createdb trivia_test
    psql trivia < trivia.psql
    psql trivia_test < trivia.psql
    ```

5.  **Run the Server**
    From the `backend` directory:
    ```bash
    # On Mac/Linux
    export FLASK_APP=flaskr
    export FLASK_ENV=development
    flask run

    # On Windows
    set FLASK_APP=flaskr
    set FLASK_ENV=development
    flask run
    ```
    The backend will be running at `http://127.0.0.1:5000`.

### Running the Tests
From the `backend` directory, run:
```bash
python test_flaskr.py
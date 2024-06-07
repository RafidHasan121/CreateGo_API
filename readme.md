# FastAPI Project

## Overview
Creatego APIs built by Rafid. 

## Installation
1. Clone the repository:
    ```bash
    git clone <repository_url>
    ```
2. Navigate to the project directory:
    ```bash
    cd <project_directory>
    ```
3. Create a virtual environment (optional but recommended):
    ```bash
    python3 -m venv venv
    ```
4. Activate the virtual environment:
    - On Windows:
        ```bash
        venv\Scripts\activate
        ```
    - On macOS and Linux:
        ```bash
        source venv/bin/activate
        ```
5. Install the dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Usage
1. Run the FastAPI application:
    ```bash
    uvicorn main:app --reload
    ```
   This will start the FastAPI application in development mode with auto-reload enabled.
   
2. Access the API documentation:
   Open your web browser and go to `http://localhost:8000/docs`. You will see the interactive Swagger UI documentation where you can explore and test the endpoints.

## Project Structure
The project structure is organized as follows:

- `main.py`: Entry point of the FastAPI application.
- `services.py` : Functions to handle complex tasks done on the OPENAI and Supabase Side.
- `requirements.txt`: File listing all Python dependencies for the project.
- `README.md`: This file.
- `.env.example` : Sample of .env file to be created using appropriate keys.
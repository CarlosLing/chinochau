# chinochau

Tools for learning Chinese with interactive flashcards.

## Features
- Interactive Streamlit web app for reviewing and creating Chinese flashcards
- Flashcards include Chinese, pinyin, definitions, and example sentences
- Definitions sourced from local dictionary or Google Translate fallback
- Example sentences generated via Deepseek API (OpenAI-compatible)
- Flashcards are cached in a CSV to minimize API usage
- Modular code for data, translation, and example management

## Usage
1. Install dependencies (recommended: use Poetry):
   ```sh
   poetry install
   ```
2. Run the Streamlit app:
   ```sh
   poetry run streamlit run app.py
   ```
3. Add or review words using the web interface. Input files should list one Chinese word per line.

## Project Structure
- `app.py`: Streamlit web app
- `chinochau/`: Core logic (data, translation, example generation)
- `input.txt`: Example input file
- `tests/`: Test scripts

## Backend Migration (FastAPI)

### Current Changes
- Added `backend/main.py` with a FastAPI app exposing endpoints for:
  - Retrieving all flashcards (to be implemented)
  - Retrieving a single flashcard by Chinese word
  - Creating a new flashcard
  - Getting example sentences for a word
- Reused core logic from `chinochau/` in the API endpoints

### Next Steps
- Implement the `/flashcards` GET endpoint to return all flashcards from the data source
- Add persistent database support (e.g., SQLite or PostgreSQL)
- Add CORS middleware for frontend integration
- Write tests for the API endpoints
- Scaffold the React frontend and connect it to the backend

## How to Start the Backend
1. Requirements:
   ```sh
   make install
   ```
2. Start the FastAPI server:
   ```sh
   make run-backend
   ```
3. The API will be available at `http://127.0.0.1:8000` and docs at `http://127.0.0.1:8000/docs`

## License
MIT License

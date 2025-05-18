# chinochau

Tools for learning Chinese with interactive flashcards.

## Features
- Modern FastAPI backend for flashcard management (CRUD)
- React + TypeScript Vite frontend for studying and adding flashcards
- Flashcards include Chinese, pinyin, definitions, and example sentences
- Definitions sourced from local dictionary or Google Translate fallback
- Example sentences generated via Deepseek API (OpenAI-compatible)
- Flashcards are cached in a CSV and stored in SQLite to minimize API usage
- Modular code for data, translation, and example management

## Usage


### Backend (FastAPI)
To set up and run the backend, simply use the Makefile commands:

```sh
make install        # Install all Python dependencies
make run-backend    # Start the FastAPI backend server
```
The API will be available at `http://127.0.0.1:8000` and docs at `http://127.0.0.1:8000/docs`


### Frontend (React + Vite)
Make sure you have Node.js (v18 or newer) and npm installed. You can use `nvm use 20` to switch to the correct version if you use nvm.

To start the frontend development server, use the Makefile command:

```sh
make run-frontend
```
Then open [http://localhost:5173](http://localhost:5173) in your browser.


---

## Project Structure
- `backend/`: FastAPI backend and database models
- `chinochau/`: Core logic (data, translation, example generation)
- `frontend/`: React + TypeScript Vite frontend
- `input.txt`: Example input file
- `tests/`: Test scripts
- `Makefile`: Common commands for development

## API
- The backend exposes endpoints for flashcard CRUD and example generation
- See `frontend/src/api/flashcards.ts` for usage examples

## Development Status
- [x] FastAPI backend with CORS and SQLite support
- [x] React frontend with flashcard study and add UI
- [x] Modular core logic for translation and examples
- [x] Database and CSV caching
- [ ] Full CRUD API (some endpoints may be incomplete)
- [ ] More robust error handling and tests

## Contributing
PRs and issues are welcome!

## License
MIT License

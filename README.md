# Agentic Mindmap - PDF to Knowledge Graph

An intelligent system that converts PDF lecture slides into interactive knowledge graphs using LangGraph and React.

## 🚀 Features

- **PDF Upload**: Upload lecture slides in PDF format
- **AI-Powered Processing**: Uses LangGraph with OpenAI to extract topics and relationships
- **Interactive Visualization**: Beautiful React-based graph visualization with ReactFlow
- **Hierarchical Structure**: Automatically organizes topics into main concepts and sub-topics
- **Real-time Processing**: See your mindmap generated in real-time

## 📋 Prerequisites

- Python 3.8+
- Node.js 16+
- OpenAI API Key

## 🛠️ Installation

### 🐳 Docker Setup (Recommended)

The easiest way to run the application is using Docker:

1. **Clone the repository and navigate to it**
   ```bash
   cd agentic_mindmap
   ```

2. **Set up environment variables**
   ```bash
   cp env.template .env
   ```
   Then edit `.env` and add your OpenAI API key:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   ```

3. **Build and run with Docker Compose**
   ```bash
   docker-compose up --build -d
   ```
   
   The application will be available at `http://localhost:8000`
   - Frontend: `http://localhost:8000`
   - API Docs: `http://localhost:8000/docs`
   - Health Check: `http://localhost:8000/health`

4. **View logs** (optional)
   ```bash
   docker-compose logs -f agentic-mindmap
   ```

5. **Stop the application**
   ```bash
   docker-compose down
   ```

### Manual Setup

### Backend Setup

1. **Clone the repository**
   ```bash
   cd agentic_mindmap-main
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the root directory:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   ```

5. **Run the backend server**
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
   The API will be available at `http://localhost:8000`

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start the development server**
   ```bash
   npm run dev
   ```
   The frontend will be available at `http://localhost:5173`

## 🎯 Usage

1. **Start both servers** (backend on port 8000, frontend on port 5173)

2. **Open your browser** and navigate to `http://localhost:5173`

3. **Upload a PDF**:
   - Click the upload area or drag & drop a PDF file
   - Maximum file size: 50MB
   - Only PDF files are accepted

4. **View the Graph**:
   - After processing, you'll be prompted to view the generated graph
   - Click "Yes" to navigate to the interactive visualization
   - Explore the mindmap with zoom, pan, and node interactions

## 📁 Project Structure

```
agentic_mindmap-main/
├── app/
│   ├── api/
│   │   └── endpoints.py          # FastAPI endpoints
│   ├── core/
│   │   ├── config.py             # Configuration
│   │   └── models.py             # Pydantic models
│   ├── langgraph/
│   │   ├── agents.py             # LangGraph workflow
│   │   ├── functions.py          # Agent functions
│   │   └── prompts.py            # LLM prompts
│   ├── services/
│   │   ├── pdf_processor.py     # PDF processing service
│   │   └── ...
│   └── main.py                   # FastAPI app
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   └── Header.jsx
│   │   ├── pages/
│   │   │   ├── UploadPage.jsx   # Upload interface
│   │   │   └── GraphPage.jsx    # Graph visualization
│   │   ├── services/
│   │   │   └── apiService.js    # API client
│   │   └── App.jsx
│   └── package.json
├── uploads/                       # Uploaded PDFs
├── output/                        # Processing results
└── requirements.txt
```

## 🔌 API Endpoints

### Upload PDF
```http
POST /api/upload-pdf
Content-Type: multipart/form-data

Response:
{
  "success": true,
  "message": "PDF uploaded and processed successfully",
  "filename": "example.pdf",
  "processing_result": {
    "graph": {
      "nodes": [...],
      "edges": [...]
    },
    "metadata": {
      "total_pages": 10,
      "total_topics": 5,
      "total_nodes": 25,
      "total_edges": 30
    }
  }
}
```

### Delete PDF
```http
DELETE /api/delete-pdf/{filename}
```

## 🎨 Frontend Configuration

The frontend configuration can be modified in `frontend/src/config/config.js`:

```javascript
export const CONFIG = {
    API_BASE_URL: 'http://localhost:8000',
    MAX_FILE_SIZE: 50 * 1024 * 1024, // 50MB
    ALLOWED_FILE_TYPES: ['application/pdf'],
};
```

## 🧪 Testing

Run backend tests:
```bash
python -m pytest test/
```

## 🐛 Troubleshooting

### Backend not connecting
- Ensure the backend is running on port 8000
- Check CORS settings in `app/main.py`
- Verify OpenAI API key is set

### Frontend not loading graph
- Check browser console for errors
- Verify the API response structure in Network tab
- Ensure sessionStorage is enabled

### Processing errors
- Check PDF file is not corrupted
- Verify sufficient OpenAI API credits
- Check backend logs for detailed error messages

## 📝 License

MIT License

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

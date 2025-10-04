# Agentic Mindmap - Frontend

A modular frontend application for uploading PDF slides and generating interactive mindmaps.

## 📁 Project Structure

```
frontend/
├── index.html                    # Main HTML entry point
├── pages/                        # HTML page templates
│   └── upload.html              # Upload page template
├── css/                          # Stylesheets
│   ├── main.css                 # Global styles and variables
│   └── components/              # Component-specific styles
│       └── upload.css           # Upload component styles
├── js/                          # JavaScript modules
│   ├── app.js                   # Application entry point
│   ├── config.js                # Configuration settings
│   ├── router.js                # Page routing system
│   ├── services/                # API and backend services
│   │   └── api.service.js       # API communication
│   ├── components/              # UI components
│   │   └── upload.component.js  # Upload functionality
│   └── utils/                   # Utility functions
│       └── helpers.js           # Helper functions
└── assets/                      # Static assets (future use)
```

## 🚀 Getting Started

### Prerequisites
- Python 3.8+ (for running local server)
- FastAPI backend running on http://localhost:8000

### Run the Frontend

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Start a local HTTP server:**
   
   Using Python:
   ```bash
   python -m http.server 8080
   ```
   
   Or using Node.js (if installed):
   ```bash
   npx http-server -p 8080
   ```

3. **Open in browser:**
   ```
   http://localhost:8080
   ```

## 🏗️ Architecture

### Modular Design

The application follows a modular architecture with clear separation of concerns:

- **Configuration Layer** (`config.js`): Centralized settings
- **Service Layer** (`services/`): API communication
- **Component Layer** (`components/`): Reusable UI components
- **Utility Layer** (`utils/`): Helper functions
- **Routing Layer** (`router.js`): Page navigation

### Key Features

✅ **ES6 Modules**: Modern JavaScript module system  
✅ **Component-Based**: Reusable and maintainable code  
✅ **Single Page Application**: Dynamic page loading  
✅ **Drag & Drop**: Intuitive file upload  
✅ **Responsive Design**: Works on all screen sizes  
✅ **Error Handling**: Comprehensive error messages  
✅ **Extensible**: Easy to add new features

## 📝 Usage

### Upload a PDF

1. Click the upload area or drag and drop a PDF file
2. The file will be validated (PDF only, max 50MB)
3. Click "Upload PDF" to send to backend
4. View the response from the server

### Configuration

Edit `js/config.js` to customize:
- API endpoints
- File size limits
- Feature flags
- Routes

## 🔧 Adding New Features

### Adding a New Page

1. Create HTML template in `pages/`:
   ```html
   <!-- pages/mynewpage.html -->
   <div class="my-page">
     <!-- Your content -->
   </div>
   ```

2. Create component in `js/components/`:
   ```javascript
   // js/components/mynewpage.component.js
   class MyNewPageComponent {
     init() { /* initialization */ }
   }
   export const myNewPageComponent = new MyNewPageComponent();
   ```

3. Add CSS in `css/components/`:
   ```css
   /* css/components/mynewpage.css */
   .my-page { /* styles */ }
   ```

4. Register route in `app.js`:
   ```javascript
   router.register('mynewpage', async () => {
     await router.loadPage('mynewpage');
     myNewPageComponent.init();
   });
   ```

5. Add navigation link in `index.html`:
   ```html
   <a href="#mynewpage" class="nav-link">My Page</a>
   ```

## 🎨 Styling

The application uses CSS custom properties (variables) for consistent theming:

```css
:root {
  --primary-color: #667eea;
  --primary-dark: #764ba2;
  --success-color: #10b981;
  --error-color: #ef4444;
  /* ... more variables */
}
```

Modify these in `css/main.css` to change the theme.

## 🔮 Future Enhancements

- [ ] Graph visualization component (D3.js, Cytoscape.js)
- [ ] Real-time processing updates
- [ ] Export functionality
- [ ] Dark mode
- [ ] Multi-file upload
- [ ] Progressive Web App (PWA)

## 🤝 Integration with Backend

The frontend expects the following API endpoints:

- `POST /api/upload-pdf` - Upload PDF file
- `DELETE /api/delete-pdf/{filename}` - Delete uploaded file

Response format:
```json
{
  "success": true,
  "message": "PDF uploaded successfully",
  "filename": "example.pdf",
  "saved_filename": "20231004_120000_example.pdf",
  "file_size": 1234567,
  "file_path": "uploads/20231004_120000_example.pdf",
  "processing_result": { /* processing data */ }
}
```

## 📄 License

This project is part of the Agentic Mindmap application.


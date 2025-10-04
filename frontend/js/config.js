// Configuration file
export const CONFIG = {
    // API Configuration
    API_BASE_URL: 'http://localhost:8000',
    API_ENDPOINTS: {
        UPLOAD_PDF: '/api/upload-pdf',
        DELETE_PDF: '/api/delete-pdf',
    },
    
    // File Upload Configuration
    MAX_FILE_SIZE: 50 * 1024 * 1024, // 50MB
    ALLOWED_FILE_TYPES: ['application/pdf'],
    ALLOWED_FILE_EXTENSIONS: ['.pdf'],
    
    // UI Configuration
    ROUTES: {
        UPLOAD: 'upload',
        GRAPH: 'graph',
    },
    
    // Feature Flags (for future features)
    FEATURES: {
        GRAPH_VIEW: false, // Enable when ready
        ADVANCED_PROCESSING: false,
    }
};


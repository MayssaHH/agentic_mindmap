// Configuration file
export const CONFIG = {
    // API Configuration
    // Use relative URL in production (Docker), absolute URL in development
    API_BASE_URL: import.meta.env.PROD ? '' : 'http://localhost:8000',
    API_ENDPOINTS: {
        UPLOAD_PDF: '/api/upload-pdf',
        DELETE_PDF: '/api/delete-pdf',
        GET_GRAPH: '/api/get-graph',
    },
    
    // File Upload Configuration
    MAX_FILE_SIZE: 50 * 1024 * 1024, // 50MB
    ALLOWED_FILE_TYPES: ['application/pdf'],
    ALLOWED_FILE_EXTENSIONS: ['.pdf'],
    
    // UI Configuration
    ROUTES: {
        UPLOAD: '/',
        GRAPH: '/graph',
    },
};


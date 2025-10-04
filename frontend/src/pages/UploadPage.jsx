import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiService } from '../services/apiService';
import { CONFIG } from '../config/config';
import '../styles/Upload.css';

export default function UploadPage() {
    const [selectedFile, setSelectedFile] = useState(null);
    const [isDragging, setIsDragging] = useState(false);
    const [isUploading, setIsUploading] = useState(false);
    const [response, setResponse] = useState(null);
    const navigate = useNavigate();

    const formatFileSize = (bytes) => {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
    };

    const validateFile = (file) => {
        if (!file) return { valid: false, error: 'No file selected' };
        
        if (!CONFIG.ALLOWED_FILE_TYPES.includes(file.type)) {
            return { valid: false, error: 'Invalid file type. Please select a PDF file.' };
        }
        
        if (file.size > CONFIG.MAX_FILE_SIZE) {
            return { 
                valid: false, 
                error: `File size exceeds ${CONFIG.MAX_FILE_SIZE / (1024 * 1024)}MB. Your file is ${formatFileSize(file.size)}`
            };
        }

        if (file.size === 0) {
            return { valid: false, error: 'The file is empty.' };
        }

        return { valid: true };
    };

    const handleFileSelect = (file) => {
        const validation = validateFile(file);
        
        if (!validation.valid) {
            setResponse({
                type: 'error',
                title: '❌ Invalid File',
                content: validation.error
            });
            return;
        }

        setSelectedFile(file);
        setResponse(null);
    };

    const handleDrop = (e) => {
        e.preventDefault();
        setIsDragging(false);
        const file = e.dataTransfer.files[0];
        handleFileSelect(file);
    };

    const handleDragOver = (e) => {
        e.preventDefault();
        setIsDragging(true);
    };

    const handleDragLeave = () => {
        setIsDragging(false);
    };

    const handleUpload = async () => {
        if (!selectedFile) return;

        setIsUploading(true);
        setResponse(null);

        try {
            const result = await apiService.uploadPDF(selectedFile);

            if (result.success) {
                // Extract graph data from processing_result
                const graphData = result.data?.processing_result?.graph;
                
                setResponse({
                    type: 'success',
                    title: '✅ Upload Successful!',
                    content: `PDF processed successfully!\n\n` +
                             `Total Pages: ${result.data.processing_result?.metadata?.total_pages || 0}\n` +
                             `Topics Found: ${result.data.processing_result?.metadata?.total_topics || 0}\n` +
                             `Graph Nodes: ${result.data.processing_result?.metadata?.total_nodes || 0}\n` +
                             `Graph Edges: ${result.data.processing_result?.metadata?.total_edges || 0}\n\n` +
                             `File: ${result.data.filename}\n` +
                             `Size: ${formatFileSize(result.data.file_size)}`
                });
                
                // Store graph data if available and navigate
                if (graphData && graphData.nodes && graphData.edges) {
                    sessionStorage.setItem('latestGraph', JSON.stringify(graphData));
                    
                    setTimeout(() => {
                        if (window.confirm('Graph generated successfully! Would you like to view it now?')) {
                            navigate('/graph');
                        }
                    }, 500);
                } else {
                    console.warn('No graph data found in response:', result.data);
                }
            } else {
                const errorMessage = result.error
                    ? `Network Error: ${result.error}\n\nMake sure your backend is running:\nuvicorn app.main:app --reload --port 8000`
                    : `Status ${result.status}\n\n${JSON.stringify(result.data, null, 2)}`;
                
                setResponse({
                    type: 'error',
                    title: '❌ Upload Failed',
                    content: errorMessage
                });
            }
        } catch (error) {
            setResponse({
                type: 'error',
                title: '❌ Unexpected Error',
                content: error.message
            });
        } finally {
            setIsUploading(false);
        }
    };

    return (
        <div className="upload-page">
            <div className="page-header">
                <h2>Upload PDF Document</h2>
                <p className="subtitle">Transform your lecture slides into an interactive knowledge graph</p>
            </div>

            <div className="upload-container">
                <div 
                    className={`upload-area ${isDragging ? 'dragover' : ''}`}
                    onClick={() => document.getElementById('fileInput').click()}
                    onDrop={handleDrop}
                    onDragOver={handleDragOver}
                    onDragLeave={handleDragLeave}
                >
                    <input
                        id="fileInput"
                        type="file"
                        accept=".pdf"
                        onChange={(e) => handleFileSelect(e.target.files[0])}
                        style={{ display: 'none' }}
                    />
                    <div className="upload-icon">📄</div>
                    <h3>Drop PDF file here or click to browse</h3>
                    <p>Maximum file size: 50MB</p>
                </div>

                {selectedFile && (
                    <div className="file-info show">
                        <div className="file-details">
                            <span className="file-name" id="fileName">{selectedFile.name}</span>
                            <span className="file-size" id="fileSize">Size: {formatFileSize(selectedFile.size)}</span>
                        </div>
                        <button 
                            className="btn btn-secondary btn-sm"
                            onClick={() => {
                                setSelectedFile(null);
                                setResponse(null);
                            }}
                        >
                            Remove
                        </button>
                    </div>
                )}

                <button 
                    className="btn btn-primary btn-upload"
                    onClick={handleUpload}
                    disabled={!selectedFile || isUploading}
                >
                    {isUploading ? (
                        <>
                            <span className="loader"></span>
                            <span>Uploading...</span>
                        </>
                    ) : (
                        <span>Upload PDF</span>
                    )}
                </button>

                {response && (
                    <div className={`response-box show ${response.type}`}>
                        <div className="response-header">
                            <h4 className="response-title">{response.title}</h4>
                            <button 
                                className="close-btn"
                                onClick={() => setResponse(null)}
                            >
                                ×
                            </button>
                        </div>
                        <pre className="response-content">{response.content}</pre>
                    </div>
                )}
            </div>
        </div>
    );
}


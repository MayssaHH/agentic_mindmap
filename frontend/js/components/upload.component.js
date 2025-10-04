// Upload Component
import { CONFIG } from '../config.js';
import { apiService } from '../services/api.service.js';
import {
    formatFileSize,
    validateFileType,
    validateFileSize,
    getElement,
    showElement,
    hideElement,
    enableElement,
    disableElement,
} from '../utils/helpers.js';

class UploadComponent {
    constructor() {
        this.selectedFile = null;
        this.elements = {};
    }

    init() {
        this.cacheElements();
        this.attachEventListeners();
    }

    cacheElements() {
        this.elements = {
            uploadArea: getElement('uploadArea'),
            fileInput: getElement('fileInput'),
            fileInfo: getElement('fileInfo'),
            fileName: getElement('fileName'),
            fileSize: getElement('fileSize'),
            removeFile: getElement('removeFile'),
            uploadBtn: getElement('uploadBtn'),
            btnText: getElement('btnText'),
            loader: getElement('loader'),
            responseBox: getElement('responseBox'),
            responseTitle: getElement('responseTitle'),
            responseContent: getElement('responseContent'),
            closeResponse: getElement('closeResponse'),
            apiUrl: getElement('apiUrl'),
        };
    }

    attachEventListeners() {
        const { uploadArea, fileInput, removeFile, uploadBtn, closeResponse } = this.elements;

        // Upload area click
        uploadArea?.addEventListener('click', () => fileInput?.click());

        // File input change
        fileInput?.addEventListener('change', (e) => this.handleFileSelect(e.target.files[0]));

        // Drag and drop
        uploadArea?.addEventListener('dragover', (e) => this.handleDragOver(e));
        uploadArea?.addEventListener('dragleave', () => this.handleDragLeave());
        uploadArea?.addEventListener('drop', (e) => this.handleDrop(e));

        // Remove file
        removeFile?.addEventListener('click', () => this.clearFile());

        // Upload button
        uploadBtn?.addEventListener('click', () => this.handleUpload());

        // Close response
        closeResponse?.addEventListener('click', () => this.hideResponse());
    }

    handleDragOver(e) {
        e.preventDefault();
        this.elements.uploadArea?.classList.add('dragover');
    }

    handleDragLeave() {
        this.elements.uploadArea?.classList.remove('dragover');
    }

    handleDrop(e) {
        e.preventDefault();
        this.elements.uploadArea?.classList.remove('dragover');
        this.handleFileSelect(e.dataTransfer.files[0]);
    }

    handleFileSelect(file) {
        if (!file) return;

        // Validate file type
        if (!validateFileType(file, CONFIG.ALLOWED_FILE_TYPES)) {
            this.showResponse('error', '❌ Invalid File Type', 'Please select a PDF file.');
            return;
        }

        // Validate file size
        if (!validateFileSize(file, CONFIG.MAX_FILE_SIZE)) {
            const message = file.size === 0
                ? 'The file is empty.'
                : `File size exceeds ${CONFIG.MAX_FILE_SIZE / (1024 * 1024)}MB. Your file is ${formatFileSize(file.size)}`;
            this.showResponse('error', '❌ Invalid File Size', message);
            return;
        }

        this.selectedFile = file;
        this.displayFileInfo(file);
        this.hideResponse();
    }

    displayFileInfo(file) {
        this.elements.fileName.textContent = file.name;
        this.elements.fileSize.textContent = `Size: ${formatFileSize(file.size)}`;
        showElement(this.elements.fileInfo);
        enableElement(this.elements.uploadBtn);
    }

    clearFile() {
        this.selectedFile = null;
        this.elements.fileInput.value = '';
        hideElement(this.elements.fileInfo);
        disableElement(this.elements.uploadBtn);
        this.hideResponse();
    }

    async handleUpload() {
        if (!this.selectedFile) return;

        const customEndpoint = this.elements.apiUrl?.value.trim();
        if (customEndpoint) {
            // Extract base URL and endpoint
            const url = new URL(customEndpoint);
            apiService.setBaseURL(url.origin);
        }

        disableElement(this.elements.uploadBtn);
        this.elements.btnText.textContent = 'Uploading...';
        showElement(this.elements.loader);
        this.hideResponse();

        try {
            const result = await apiService.uploadPDF(
                this.selectedFile,
                customEndpoint ? new URL(customEndpoint).pathname : undefined
            );

            if (result.success) {
                this.showResponse(
                    'success',
                    '✅ Upload Successful!',
                    JSON.stringify(result.data, null, 2)
                );
            } else {
                const errorMessage = result.error
                    ? `Network Error: ${result.error}\n\nMake sure your backend is running:\nuvicorn app.main:app --reload`
                    : `Status ${result.status}\n\n${JSON.stringify(result.data, null, 2)}`;
                
                this.showResponse('error', '❌ Upload Failed', errorMessage);
            }
        } catch (error) {
            this.showResponse('error', '❌ Unexpected Error', error.message);
        } finally {
            hideElement(this.elements.loader);
            this.elements.btnText.textContent = 'Upload PDF';
            enableElement(this.elements.uploadBtn);
        }
    }

    showResponse(type, title, content) {
        this.elements.responseBox.className = `response-box show ${type}`;
        this.elements.responseTitle.textContent = title;
        this.elements.responseContent.textContent = content;
    }

    hideResponse() {
        hideElement(this.elements.responseBox);
    }

    destroy() {
        // Cleanup if needed
        this.selectedFile = null;
        this.elements = {};
    }
}

export const uploadComponent = new UploadComponent();


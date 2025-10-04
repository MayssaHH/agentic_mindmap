// Utility helper functions

export function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

export function validateFileType(file, allowedTypes) {
    return allowedTypes.includes(file.type);
}

export function validateFileSize(file, maxSize) {
    return file.size <= maxSize && file.size > 0;
}

export function getElement(id) {
    return document.getElementById(id);
}

export function showElement(element) {
    element?.classList.add('show');
}

export function hideElement(element) {
    element?.classList.remove('show');
}

export function enableElement(element) {
    if (element) element.disabled = false;
}

export function disableElement(element) {
    if (element) element.disabled = true;
}

export function showNotification(type, message) {
    // Future: implement toast notifications
    console.log(`[${type.toUpperCase()}]: ${message}`);
}


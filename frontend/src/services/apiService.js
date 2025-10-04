// API Service for backend communication
import { CONFIG } from '../config/config';

class APIService {
    constructor(baseURL = CONFIG.API_BASE_URL) {
        this.baseURL = baseURL;
    }

    async uploadPDF(file, endpoint = CONFIG.API_ENDPOINTS.UPLOAD_PDF) {
        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch(`${this.baseURL}${endpoint}`, {
                method: 'POST',
                body: formData,
            });

            const data = await response.json();

            return {
                success: response.ok,
                status: response.status,
                data: data,
            };
        } catch (error) {
            return {
                success: false,
                status: 0,
                error: error.message,
            };
        }
    }

    async deletePDF(filename) {
        try {
            const response = await fetch(
                `${this.baseURL}${CONFIG.API_ENDPOINTS.DELETE_PDF}/${filename}`,
                {
                    method: 'DELETE',
                }
            );

            const data = await response.json();

            return {
                success: response.ok,
                status: response.status,
                data: data,
            };
        } catch (error) {
            return {
                success: false,
                status: 0,
                error: error.message,
            };
        }
    }

    async getGraph(filename) {
        try {
            const response = await fetch(
                `${this.baseURL}${CONFIG.API_ENDPOINTS.GET_GRAPH}/${filename}`,
                {
                    method: 'GET',
                }
            );

            const data = await response.json();

            return {
                success: response.ok,
                status: response.status,
                data: data,
            };
        } catch (error) {
            return {
                success: false,
                status: 0,
                error: error.message,
            };
        }
    }

    setBaseURL(url) {
        this.baseURL = url;
    }
}

// Export singleton instance
export const apiService = new APIService();


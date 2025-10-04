// Simple router for page navigation
import { CONFIG } from './config.js';

class Router {
    constructor() {
        this.routes = {};
        this.currentRoute = null;
    }

    register(path, loadFunction) {
        this.routes[path] = loadFunction;
    }

    async navigate(path) {
        const route = this.routes[path];
        if (!route) {
            console.error(`Route not found: ${path}`);
            return;
        }

        this.currentRoute = path;
        await route();
        this.updateActiveNav(path);
    }

    updateActiveNav(path) {
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href') === `#${path}`) {
                link.classList.add('active');
            }
        });
    }

    async loadPage(pageName) {
        try {
            const response = await fetch(`pages/${pageName}.html`);
            const html = await response.text();
            const mainContent = document.getElementById('main-content');
            if (mainContent) {
                mainContent.innerHTML = html;
            }
        } catch (error) {
            console.error(`Error loading page: ${pageName}`, error);
        }
    }

    init() {
        // Handle navigation clicks
        document.addEventListener('click', (e) => {
            if (e.target.matches('.nav-link')) {
                e.preventDefault();
                const path = e.target.getAttribute('href').substring(1);
                this.navigate(path);
            }
        });

        // Handle initial route
        const initialRoute = window.location.hash.substring(1) || CONFIG.ROUTES.UPLOAD;
        this.navigate(initialRoute);
    }
}

export const router = new Router();


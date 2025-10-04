// Main application entry point
import { CONFIG } from './config.js';
import { router } from './router.js';
import { uploadComponent } from './components/upload.component.js';

class App {
    constructor() {
        this.initialized = false;
    }

    async init() {
        if (this.initialized) return;

        console.log('🚀 Initializing Agentic Mindmap App...');

        // Register routes
        this.registerRoutes();

        // Initialize router
        router.init();

        this.initialized = true;
        console.log('✅ App initialized successfully');
    }

    registerRoutes() {
        // Upload route
        router.register(CONFIG.ROUTES.UPLOAD, async () => {
            await router.loadPage('upload');
            uploadComponent.init();
        });

        // Graph route (future)
        router.register(CONFIG.ROUTES.GRAPH, async () => {
            if (CONFIG.FEATURES.GRAPH_VIEW) {
                // await router.loadPage('graph');
                // graphComponent.init();
                console.log('Graph view - Coming soon!');
            } else {
                alert('Graph view is not yet available. Coming soon!');
                router.navigate(CONFIG.ROUTES.UPLOAD);
            }
        });
    }
}

// Initialize app when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        const app = new App();
        app.init();
    });
} else {
    const app = new App();
    app.init();
}


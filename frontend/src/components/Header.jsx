import { Link, useLocation } from 'react-router-dom';
import '../styles/Header.css';

export default function Header() {
    const location = useLocation();

    return (
        <header className="app-header">
            <div className="container">
                <h1 className="logo">🧠 Agentic Mindmap</h1>
                <nav className="nav">
                    <Link 
                        to="/" 
                        className={`nav-link ${location.pathname === '/' ? 'active' : ''}`}
                    >
                        Upload
                    </Link>
                    <Link 
                        to="/graph" 
                        className={`nav-link ${location.pathname === '/graph' ? 'active' : ''}`}
                    >
                        Graph View
                    </Link>
                </nav>
            </div>
        </header>
    );
}


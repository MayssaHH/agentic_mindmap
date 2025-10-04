import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Header from './components/Header';
import UploadPage from './pages/UploadPage';
import GraphPage from './pages/GraphPage';
import './App.css';

function App() {
    return (
        <Router>
            <div className="app">
                <Header />
                <main className="main-content">
                    <Routes>
                        <Route path="/" element={<UploadPage />} />
                        <Route path="/graph" element={<GraphPage />} />
                    </Routes>
                </main>
            </div>
        </Router>
    );
}

export default App;

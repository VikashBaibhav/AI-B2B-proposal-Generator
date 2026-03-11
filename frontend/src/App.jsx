import React from 'react';
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import { Bot } from 'lucide-react';

import HomePage from './pages/HomePage';
import ProposalFormPage from './pages/ProposalFormPage';
import ProposalPreviewPage from './pages/ProposalPreviewPage';

const App = () => {
    return (
        <BrowserRouter>
            <div className="app-container">

                {/* Persistent Top Navbar */}
                <nav className="navbar">
                    <Link to="/" className="logo">
                        <Bot color="var(--accent-primary)" size={28} />
                        PropAI<span style={{ color: 'var(--text-secondary)', fontWeight: 300 }}>Gen</span>
                    </Link>

                    <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
                        <a href="http://localhost:8000/docs" target="_blank" rel="noreferrer" className="btn btn-secondary">
                            API Docs
                        </a>
                        <Link to="/new" className="btn btn-primary">
                            Generate Proposal
                        </Link>
                    </div>
                </nav>

                {/* Page Routing */}
                <Routes>
                    <Route path="/" element={<HomePage />} />
                    <Route path="/new" element={<ProposalFormPage />} />
                    <Route path="/proposal/:id" element={<ProposalPreviewPage />} />
                </Routes>

            </div>
        </BrowserRouter>
    );
};

export default App;

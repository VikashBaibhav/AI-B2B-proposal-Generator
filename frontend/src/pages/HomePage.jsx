import React from 'react';
import { Link } from 'react-router-dom';
import { FileText, Cpu, ShieldCheck, Zap } from 'lucide-react';

const HomePage = () => {
    return (
        <div className="main-content">
            {/* Hero Section */}
            <div style={{ textAlign: 'center', margin: '4rem 0 6rem 0' }}>
                <h1 className="text-gradient" style={{ fontSize: '4.5rem', letterSpacing: '-0.02em', marginBottom: '1.5rem' }}>
                    Close Deals Faster with AI
                </h1>
                <p style={{ fontSize: '1.25rem', color: 'var(--text-secondary)', maxWidth: '600px', margin: '0 auto 3rem auto' }}>
                    Generate hyper-personalized, high-converting B2B proposals in seconds.
                    Stop writing documents and start closing revenue.
                </p>
                <Link to="/new" className="btn btn-primary" style={{ fontSize: '1.1rem', padding: '0.8rem 2rem' }}>
                    <Zap size={20} /> Create Your First Proposal
                </Link>
            </div>

            {/* Architecture Highlights */}
            <h2 style={{ textAlign: 'center', marginBottom: '3rem', fontSize: '2rem' }}>Enterprise-Grade Architecture</h2>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '2rem', marginBottom: '4rem' }}>

                <div className="glass-panel" style={{ padding: '2rem' }}>
                    <div style={{ width: '3rem', height: '3rem', borderRadius: 'var(--radius-md)', backgroundColor: 'rgba(99, 102, 241, 0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '1.5rem', color: 'var(--accent-primary)' }}>
                        <Cpu size={24} />
                    </div>
                    <h3 style={{ fontSize: '1.25rem' }}>Clean Architecture</h3>
                    <p style={{ color: 'var(--text-secondary)' }}>
                        Domain logic strictly decoupled from frameworks. Swap AI providers or databases with zero changes to business use cases.
                    </p>
                </div>

                <div className="glass-panel" style={{ padding: '2rem' }}>
                    <div style={{ width: '3rem', height: '3rem', borderRadius: 'var(--radius-md)', backgroundColor: 'rgba(16, 185, 129, 0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '1.5rem', color: 'var(--accent-success)' }}>
                        <ShieldCheck size={24} />
                    </div>
                    <h3 style={{ fontSize: '1.25rem' }}>JSON Schema Validation</h3>
                    <p style={{ color: 'var(--text-secondary)' }}>
                        Strict validation layer guarantees the application only receives well-formed, semantically correct data from the LLM.
                    </p>
                </div>

                <div className="glass-panel" style={{ padding: '2rem' }}>
                    <div style={{ width: '3rem', height: '3rem', borderRadius: 'var(--radius-md)', backgroundColor: 'rgba(245, 158, 11, 0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '1.5rem', color: 'var(--accent-warning)' }}>
                        <FileText size={24} />
                    </div>
                    <h3 style={{ fontSize: '1.25rem' }}>Interaction Logging</h3>
                    <p style={{ color: 'var(--text-secondary)' }}>
                        Every AI request is tracked. Monitor token usage, latency, and model outputs for continuous quality improvement.
                    </p>
                </div>
            </div>
        </div>
    );
};

export default HomePage;

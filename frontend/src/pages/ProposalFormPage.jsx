import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Sparkles, ArrowRight, Loader2 } from 'lucide-react';
import { proposalService } from '../services/proposalService';

const ProposalFormPage = () => {
    const navigate = useNavigate();
    const [isGenerating, setIsGenerating] = useState(false);
    const [error, setError] = useState(null);

    const [formData, setFormData] = useState({
        companyName: '',
        contactName: '',
        contactEmail: '',
        industry: 'technology',
        companySize: '',
        budgetLimitUsd: '',
        painPoints: '',
        goals: '',
    });

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setIsGenerating(true);
        setError(null);

        try {
            const proposal = await proposalService.generateProposal(formData);
            navigate(`/proposal/${proposal.proposal_id}`);
        } catch (err) {
            setError(err.message);
            window.scrollTo(0, 0);
        } finally {
            setIsGenerating(false);
        }
    };

    return (
        <div className="main-content">
            <div style={{ maxWidth: '800px', margin: '0 auto' }}>
                <div style={{ marginBottom: '2rem', textAlign: 'center' }}>
                    <h1 className="text-gradient" style={{ fontSize: '3rem', marginBottom: '1rem' }}>
                        Generate New Proposal
                    </h1>
                    <p style={{ color: 'var(--text-secondary)', fontSize: '1.1rem' }}>
                        Provide details about your prospect. Our AI will analyze their industry,
                        calculate optimized pricing tiers, and generate a tailored proposal.
                    </p>
                </div>

                {error && (
                    <div style={{
                        backgroundColor: 'rgba(239, 68, 68, 0.1)',
                        border: '1px solid var(--accent-error)',
                        color: '#fca5a5',
                        padding: '1rem',
                        borderRadius: 'var(--radius-md)',
                        marginBottom: '2rem'
                    }}>
                        <strong>Generation Failed:</strong> {error}
                    </div>
                )}

                <div className="glass-panel" style={{ padding: '2.5rem' }}>
                    <form onSubmit={handleSubmit}>

                        <h3 style={{ borderBottom: '1px solid var(--border-light)', paddingBottom: '0.5rem', marginBottom: '1.5rem', color: 'var(--accent-primary)' }}>
                            1. Client Overview
                        </h3>

                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
                            <div className="form-group">
                                <label className="form-label">Target Company Name *</label>
                                <input
                                    type="text"
                                    name="companyName"
                                    className="form-control"
                                    required
                                    placeholder="e.g., Acme Cloud Corp"
                                    value={formData.companyName}
                                    onChange={handleChange}
                                />
                            </div>

                            <div className="form-group">
                                <label className="form-label">Industry *</label>
                                <select
                                    name="industry"
                                    className="form-control"
                                    required
                                    value={formData.industry}
                                    onChange={handleChange}
                                >
                                    <option value="technology">Technology & Software</option>
                                    <option value="healthcare">Healthcare & Life Sciences</option>
                                    <option value="finance">Financial Services</option>
                                    <option value="retail">Retail & E-commerce</option>
                                    <option value="manufacturing">Manufacturing</option>
                                    <option value="education">Education</option>
                                    <option value="other">Other</option>
                                </select>
                            </div>
                        </div>

                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '1.5rem' }}>
                            <div className="form-group">
                                <label className="form-label">Contact Name *</label>
                                <input
                                    type="text"
                                    name="contactName"
                                    className="form-control"
                                    required
                                    placeholder="Jane Doe"
                                    value={formData.contactName}
                                    onChange={handleChange}
                                />
                            </div>

                            <div className="form-group">
                                <label className="form-label">Contact Email *</label>
                                <input
                                    type="email"
                                    name="contactEmail"
                                    className="form-control"
                                    required
                                    placeholder="jane@acme.com"
                                    value={formData.contactEmail}
                                    onChange={handleChange}
                                />
                            </div>

                            <div className="form-group">
                                <label className="form-label">Company Size (Employees) *</label>
                                <input
                                    type="number"
                                    name="companySize"
                                    className="form-control"
                                    required
                                    min="1"
                                    placeholder="e.g., 150"
                                    value={formData.companySize}
                                    onChange={handleChange}
                                />
                            </div>
                        </div>

                        <div className="form-group">
                            <label className="form-label">Budget Limit (USD)</label>
                            <input
                                type="number"
                                name="budgetLimitUsd"
                                className="form-control"
                                min="0"
                                step="1000"
                                placeholder="e.g., 100000"
                                value={formData.budgetLimitUsd}
                                onChange={handleChange}
                            />
                            <small style={{ color: 'var(--text-secondary)', marginTop: '0.5rem', display: 'block' }}>
                                Annual budget allocation limit for cost breakdown (optional)
                            </small>
                        </div>

                        <h3 style={{ borderBottom: '1px solid var(--border-light)', paddingBottom: '0.5rem', marginBottom: '1.5rem', marginTop: '2rem', color: 'var(--accent-primary)' }}>
                            2. Discovery Context
                        </h3>

                        <div className="form-group">
                            <label className="form-label">Specific Pain Points (one per line) *</label>
                            <textarea
                                name="painPoints"
                                className="form-control"
                                required
                                placeholder="- Manual processes take too long&#10;- Lack of visibility into data&#10;- High error rates"
                                value={formData.painPoints}
                                onChange={handleChange}
                                rows={4}
                            />
                        </div>

                        <div className="form-group">
                            <label className="form-label">Client Goals (one per line)</label>
                            <textarea
                                name="goals"
                                className="form-control"
                                placeholder="- Reduce processing time by 50%&#10;- Centralize reporting framework"
                                value={formData.goals}
                                onChange={handleChange}
                                rows={3}
                            />
                        </div>

                        <div style={{ marginTop: '3rem', display: 'flex', justifyContent: 'flex-end', gap: '1rem' }}>
                            <button
                                type="button"
                                className="btn btn-secondary"
                                onClick={() => navigate('/')}
                                disabled={isGenerating}
                            >
                                Cancel
                            </button>

                            <button
                                type="submit"
                                className="btn btn-primary"
                                disabled={isGenerating}
                                style={{ minWidth: '200px' }}
                            >
                                {isGenerating ? (
                                    <>
                                        <Loader2 className="spinner" size={18} />
                                        Generating AI Proposal...
                                    </>
                                ) : (
                                    <>
                                        <Sparkles size={18} />
                                        Generate Proposal <ArrowRight size={18} />
                                    </>
                                )}
                            </button>
                        </div>

                    </form>
                </div>
            </div>
        </div>
    );
};

export default ProposalFormPage;

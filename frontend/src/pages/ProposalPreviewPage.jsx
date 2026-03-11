import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { proposalService } from '../services/proposalService';
import { ChevronLeft, Download, Send, CheckCircle, Cpu } from 'lucide-react';

const ProposalPreviewPage = () => {
    const { id } = useParams();
    const [proposal, setProposal] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchProposal = async () => {
            try {
                const data = await proposalService.getProposal(id);
                setProposal(data);
            } catch (err) {
                setError(err.message);
            } finally {
                setLoading(false);
            }
        };

        fetchProposal();
    }, [id]);

    if (loading) {
        return (
            <div className="main-content flex-center" style={{ minHeight: '60vh', flexDirection: 'column', gap: '1rem' }}>
                <div className="spinner" style={{ width: '3rem', height: '3rem', borderWidth: '4px', borderColor: 'rgba(99, 102, 241, 0.2)', borderTopColor: 'var(--accent-primary)' }}></div>
                <h3 style={{ color: 'var(--text-secondary)' }}>Retrieving Document...</h3>
            </div>
        );
    }

    if (error || !proposal) {
        return (
            <div className="main-content flex-center">
                <div className="card" style={{ maxWidth: '500px', textAlign: 'center' }}>
                    <h2 style={{ color: 'var(--accent-error)' }}>Error Loading Proposal</h2>
                    <p style={{ color: 'var(--text-secondary)', marginBottom: '2rem' }}>{error || 'Proposal not found.'}</p>
                    <Link to="/new" className="btn btn-primary">Create New Proposal</Link>
                </div>
            </div>
        );
    }

    return (
        <div className="main-content">
            {/* Header Panel */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '2rem' }}>
                <div>
                    <Link to="/" className="btn btn-secondary" style={{ padding: '0.4rem 0.8rem', marginBottom: '1rem' }}>
                        <ChevronLeft size={16} /> Back to Dashboard
                    </Link>
                    <h1 style={{ margin: 0 }}>{proposal.title}</h1>
                    <div style={{ display: 'flex', gap: '1rem', marginTop: '0.5rem', fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
                        <span style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                            <CheckCircle size={14} color="var(--accent-success)" /> Status: Generated
                        </span>
                        <span style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                            <Cpu size={14} /> AI Model: {proposal.ai_model_used}
                        </span>
                    </div>
                </div>

                <div style={{ display: 'flex', gap: '1rem' }}>
                    <button className="btn btn-secondary" onClick={() => window.print()}>
                        <Download size={16} /> PDF Export
                    </button>
                    <button className="btn btn-primary">
                        <Send size={16} /> Send to Client
                    </button>
                </div>
            </div>

            {/* Actual Printable Document View */}
            <div className="proposal-document">

                {/* Cover Section */}
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'end', marginBottom: '4rem' }}>
                    <div>
                        <h1 style={{ border: 'none', margin: 0, padding: 0 }}>Partnership Proposal</h1>
                        <p style={{ fontSize: '1.5rem', color: '#64748b', marginTop: '0.5rem' }}>Prepared for {proposal.company_name}</p>
                    </div>
                    <div style={{ textAlign: 'right', color: '#64748b' }}>
                        <p><strong>Date:</strong> {new Date(proposal.created_at).toLocaleDateString()}</p>
                        <p><strong>ID:</strong> {proposal.proposal_id.split('-')[0].toUpperCase()}</p>
                    </div>
                </div>

                <h2>Executive Summary</h2>
                <p>{proposal.executive_summary}</p>

                <h2>Problem Statement</h2>
                <p>{proposal.problem_statement}</p>

                <h2>Proposed Solution</h2>
                <p>{proposal.proposed_solution}</p>

                <h3>Key Benefits</h3>
                <ul>
                    {proposal.key_benefits?.map((benefit, i) => (
                        <li key={i}>{benefit}</li>
                    ))}
                </ul>

                <h2>Implementation Timeline</h2>
                <p>{proposal.implementation_timeline}</p>

                <h2>Investment & Pricing</h2>
                <p>Based on our analysis of your organization ({proposal.company_name}), we recommend the following pricing options structured around your needs.</p>

                <div className="tier-grid" style={{ marginBottom: '3rem' }}>
                    {proposal.pricing_tiers?.map((tier) => {
                        // Recommendation heurstic: suggest the middle option or logic we wrote in backend
                        const isRecommended = tier.tier_name === 'Professional';

                        return (
                            <div key={tier.tier_name} className={`tier-card ${isRecommended ? 'recommended' : ''}`}>
                                <h3 style={{ margin: 0, border: 'none', fontSize: '1.25rem' }}>{tier.tier_name} Option</h3>
                                <div className="tier-price">
                                    ${tier.effective_price.toLocaleString()} <span style={{ fontSize: '1rem', color: '#64748b', fontWeight: 'normal' }}>/{tier.billing_cycle === 'annual' ? 'mo (billed annually)' : 'mo'}</span>
                                </div>

                                {tier.discount_percentage > 0 && (
                                    <div style={{ color: '#10b981', fontSize: '0.85rem', fontWeight: 'bold', marginBottom: '1rem' }}>
                                        Includes {tier.discount_percentage}% volume discount
                                    </div>
                                )}

                                <ul className="tier-features">
                                    {tier.features?.map((f, i) => (
                                        <li key={i}>{f}</li>
                                    ))}
                                    {tier.setup_fee_usd > 0 && (
                                        <li>One-time setup: ${tier.setup_fee_usd.toLocaleString()}</li>
                                    )}
                                </ul>
                            </div>
                        );
                    })}
                </div>

                <h2>Terms & Conditions</h2>
                <p>{proposal.terms_and_conditions}</p>

                <h2>Next Steps</h2>
                <p><strong>{proposal.call_to_action}</strong></p>

                <div style={{ marginTop: '4rem', display: 'flex', justifyContent: 'space-between', borderTop: '1px solid #e2e8f0', paddingTop: '2rem' }}>
                    <div style={{ width: '45%' }}>
                        <p style={{ color: '#64748b', marginBottom: '3rem' }}>Agreed and accepted by client:</p>
                        <div style={{ borderBottom: '1px solid #94a3b8', height: '1.5rem' }}></div>
                        <p style={{ fontSize: '0.8rem', color: '#64748b', marginTop: '0.5rem' }}>Authorized Signature</p>
                    </div>
                    <div style={{ width: '45%' }}>
                        <p style={{ color: '#64748b', marginBottom: '3rem' }}>Agreed and accepted by provider:</p>
                        <div style={{ borderBottom: '1px solid #94a3b8', height: '1.5rem' }}></div>
                        <p style={{ fontSize: '0.8rem', color: '#64748b', marginTop: '0.5rem' }}>Provider Signature</p>
                    </div>
                </div>

            </div>
        </div>
    );
};

export default ProposalPreviewPage;

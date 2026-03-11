import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const apiClient = axios.create({
    baseURL: `${API_BASE_URL}/api`,
    headers: {
        'Content-Type': 'application/json',
    },
});

export const proposalService = {
    /**
     * Generate a new proposal
     * @param {Object} formData - The client profile data
     * @returns {Promise<Object>} The generated proposal
     */
    generateProposal: async (formData) => {
        try {
            // Map frontend form data to backend API schema
            const payload = {
                client: {
                    company_name: formData.companyName,
                    contact_name: formData.contactName,
                    contact_email: formData.contactEmail,
                    industry: formData.industry,
                    company_size: parseInt(formData.companySize, 10),
                    pain_points: formData.painPoints.split('\n').filter(p => p.trim()),
                    goals: formData.goals.split('\n').filter(g => g.trim()),
                    budget_limit_usd: formData.budgetLimitUsd ? parseFloat(formData.budgetLimitUsd) : null,
                },
                contract_duration_months: 12
            };

            const response = await apiClient.post('/proposals/generate', payload);
            return response.data;
        } catch (error) {
            if (error.response?.data?.detail) {
                throw new Error(error.response.data.detail);
            }
            throw new Error(error.message || 'An error occurred during generation');
        }
    },

    /**
     * Fetch a previously generated proposal by ID
     * @param {string} id - Proposal ID
     * @returns {Promise<Object>}
     */
    getProposal: async (id) => {
        const response = await apiClient.get(`/proposals/${id}`);
        return response.data;
    }
};

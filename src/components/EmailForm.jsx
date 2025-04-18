import React, { useState } from 'react';
import { WebhookService } from '../services/webhook.service';

const EmailForm = () => {
    const [formData, setFormData] = useState({
        to: '',
        subject: '',
        content: ''
    });
    const [status, setStatus] = useState({
        loading: false,
        error: null,
        success: false
    });

    const webhookService = new WebhookService(process.env.NODE_ENV === 'production');

    const handleSubmit = async (e) => {
        e.preventDefault();
        setStatus({ loading: true, error: null, success: false });

        try {
            const response = await webhookService.sendEmailRequest(formData);
            setStatus({ loading: false, error: null, success: true });
            setFormData({ to: '', subject: '', content: '' });
            console.log('Response:', response);
        } catch (error) {
            setStatus({ 
                loading: false, 
                error: 'Failed to send email. Please try again.', 
                success: false 
            });
        }
    };

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
    };

    return (
        <div className="max-w-2xl mx-auto p-4">
            <h2 className="text-2xl font-bold mb-4">Send Email</h2>
            <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                    <label className="block text-sm font-medium mb-1">
                        To:
                        <input
                            type="email"
                            name="to"
                            value={formData.to}
                            onChange={handleChange}
                            className="w-full p-2 border rounded mt-1"
                            required
                        />
                    </label>
                </div>
                <div>
                    <label className="block text-sm font-medium mb-1">
                        Subject:
                        <input
                            type="text"
                            name="subject"
                            value={formData.subject}
                            onChange={handleChange}
                            className="w-full p-2 border rounded mt-1"
                            required
                        />
                    </label>
                </div>
                <div>
                    <label className="block text-sm font-medium mb-1">
                        Content:
                        <textarea
                            name="content"
                            value={formData.content}
                            onChange={handleChange}
                            className="w-full p-2 border rounded mt-1 h-32"
                            required
                        />
                    </label>
                </div>

                {status.error && (
                    <div className="text-red-500 text-sm">{status.error}</div>
                )}
                {status.success && (
                    <div className="text-green-500 text-sm">Email sent successfully!</div>
                )}

                <button
                    type="submit"
                    disabled={status.loading}
                    className={`w-full p-2 text-white rounded ${
                        status.loading 
                            ? 'bg-gray-400' 
                            : 'bg-blue-500 hover:bg-blue-600'
                    }`}
                >
                    {status.loading ? 'Sending...' : 'Send Email'}
                </button>
            </form>
        </div>
    );
};

export default EmailForm;
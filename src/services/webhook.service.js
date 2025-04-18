import { webhookConfig } from '../config/webhook.config.js';

export class WebhookService {
    constructor(isProduction = false) {
        this.baseUrl = isProduction ? webhookConfig.URLS.PRODUCTION : webhookConfig.URLS.TEST;
        this.auth = webhookConfig.AUTH;
    }

    generateAuthHeader() {
        return 'Basic ' + btoa(`${this.auth.username}:${this.auth.password}`);
    }

    async sendEmailRequest(emailData) {
        try {
            const response = await fetch(this.baseUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': this.generateAuthHeader()
                },
                body: JSON.stringify({
                    emailContent: emailData.content,
                    to: emailData.to,
                    subject: emailData.subject
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Webhook request failed:', error);
            throw error;
        }
    }
}
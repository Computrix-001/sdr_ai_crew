export interface EmailData {
    to: string;
    subject: string;
    content: string;
}

export interface WebhookResponse {
    status: string;
    emailSent: boolean;
    response: string;
}
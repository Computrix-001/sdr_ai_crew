import { WebhookService } from '../services/webhook.service';

describe('WebhookService', () => {
    let webhookService;

    beforeEach(() => {
        webhookService = new WebhookService(false);
    });

    test('should create correct auth header', () => {
        const authHeader = webhookService.generateAuthHeader();
        expect(authHeader).toContain('Basic ');
    });

    test('should send email request successfully', async () => {
        const mockEmailData = {
            to: 'test@example.com',
            subject: 'Test Subject',
            content: 'Test Content'
        };

        global.fetch = jest.fn(() =>
            Promise.resolve({
                ok: true,
                json: () => Promise.resolve({
                    status: 'success',
                    emailSent: true,
                    response: 'Test response'
                })
            })
        );

        const response = await webhookService.sendEmailRequest(mockEmailData);
        expect(response.status).toBe('success');
        expect(response.emailSent).toBe(true);
    });
});
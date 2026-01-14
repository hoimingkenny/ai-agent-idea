export class OpenRouterService {
    private apiKey: string;
    
    constructor(apiKey: string) {
        this.apiKey = apiKey;
    }
    
    async streamResponse(messages: any[], onToken: (token: string) => void) {
        try {
            const response = await fetch("https://openrouter.ai/api/v1/chat/completions", {
                method: "POST",
                headers: {
                    "Authorization": `Bearer ${this.apiKey}`,
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    model: "xiaomi/mimo-v2-flash:free",
                    messages: messages,
                    stream: true
                })
            });
            
            // Handle streaming response (simplified)
            // In RN, fetch streaming support varies.
        } catch (e) {
            console.error("OpenRouter API error", e);
        }
    }
}

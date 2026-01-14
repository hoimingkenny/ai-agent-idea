export interface MessageLike {
    role: string;
    content: string;
}

export class ContextPruner {
    static buildPrompt(messages: MessageLike[], limit: number = 2048): string {
        // Simple sliding window
        // Calculate tokens (rough estimate: 4 chars = 1 token)
        let prompt = "";
        let currentLength = 0;
        
        // Take last N messages that fit
        for (let i = messages.length - 1; i >= 0; i--) {
            const msg = messages[i];
            const content = `${msg.role === 'user' ? 'User' : 'Assistant'}: ${msg.content}\n`;
            const estTokens = content.length / 4;
            
            if (currentLength + estTokens > limit) break;
            
            prompt = content + prompt;
            currentLength += estTokens;
        }
        
        return prompt;
    }
}

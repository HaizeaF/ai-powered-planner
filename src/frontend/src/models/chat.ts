export interface ChatMessage {
    role: "user" | "agent" | "error"
    content: string
}

export interface ChatRequest {
    question: string;
    thread_id: string;
    history?: Record<string, string>[];
}

export interface ChatResponse {
    agent_response: string;
}
import { Injectable, inject } from "@angular/core";
import { HttpClient } from "@angular/common/http";
import { first, firstValueFrom } from "rxjs";
import { environment } from "../environments/environment";
import { ChatRequest, ChatResponse } from "../models/chat";

@Injectable({ providedIn: "root" })
export class ChatService {
    private readonly http = inject(HttpClient);
    private readonly baseUrl = environment.apiUrl;
    private readonly threadId = crypto.randomUUID();

    async send(question: string): Promise<string> {
        const payload: ChatRequest = { question, thread_id: this.threadId};
        const response = await firstValueFrom(this.http.post<ChatResponse>(`${this.baseUrl}/chat`, payload));
        return response.agent_response;
    }
}
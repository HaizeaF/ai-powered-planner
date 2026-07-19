import { Component, ElementRef, ViewChild, inject, signal } from "@angular/core";
import { CommonModule } from "@angular/common";
import { FormsModule } from "@angular/forms";
import { LucideArrowUp, LucideMessageCircle, LucideRotateCcw, LucideX } from "@lucide/angular";
import { ChatService } from "../../services/chat";
import { ChatMessage } from "../../models/chat";
import { TaskService } from "../../services/task";
import { ProjectService } from "../../services/project";

@Component({
    selector: "app-chatbot",
    imports: [CommonModule, FormsModule, LucideArrowUp, LucideMessageCircle, LucideRotateCcw, LucideX],
    templateUrl: "./chatbot.html",
    styleUrl: "./chatbot.css"
})
export class Chatbot {
    private readonly chatService = inject(ChatService);
    private readonly taskService = inject(TaskService);
    private readonly projectService = inject(ProjectService);

    @ViewChild("chatWindow") chatWindowRef?: ElementRef<HTMLDivElement>;

    readonly open = signal(false);
    readonly messages = signal<ChatMessage[]>([]);
    readonly sending = signal(false);
    question = "";

    toggle(): void {
        this.open.update((v) => !v);
    }

    clearChat(): void {
        this.messages.set([]);
    }

    async send(): Promise<void> {
        const question = this.question.trim();
        if (!question || this.sending()) return;

        this.messages.update((list) => [...list, { role: "user", content: question }]);
        this.question = "";
        this.sending.set(true);
        this.scrollToBottom();

        try {
        const response = await this.chatService.send(question);
        this.messages.update((list) => [...list, { role: "agent", content: response }]);
        await Promise.all([this.taskService.loadAll(), this.projectService.loadAll()]);
        } catch {
        this.messages.update((list) => [
            ...list,
            { role: "error", content: "Couldn't reach the assistant. Please try again." },
        ]);
        } finally {
        this.sending.set(false);
        this.scrollToBottom();
        }
    }

    private scrollToBottom(): void {
        queueMicrotask(() => {
        const el = this.chatWindowRef?.nativeElement;
        if (el) el.scrollTop = el.scrollHeight;
        });
    }
}
import { Component, EventEmitter, Output, effect, inject, input, signal } from "@angular/core";
import { CommonModule } from "@angular/common";
import { FormsModule } from "@angular/forms";
import { LucideX, LucideCheck, LucideTrash2 } from "@lucide/angular";
import { TaskService } from "../../../services/task";
import { ProjectService } from "../../../services/project";
import { COLOR_PALETTE, DEFAULT_COLOR, TaskType } from "../../../models/enums";
import { Task, TaskCreate, TaskUpdate } from "../../../models/task";
import { formatTimeLabel } from "../../../utils/dateUtils";

export type TaskModalState = { mode: "create"; defaultDate: string } | { mode: "edit"; task: Task };

@Component({
    selector: "app-task-modal",
    imports: [CommonModule, FormsModule, LucideCheck, LucideTrash2, LucideX],
    templateUrl: "./taskModal.html",
    styleUrl: "./taskModal.css"
})
export class TaskModal {
    private readonly taskService = inject(TaskService);
    private readonly projectService = inject(ProjectService);

    readonly state = input<TaskModalState | null>(null);
    @Output() close = new EventEmitter<void>();

    readonly colors = COLOR_PALETTE;
    readonly TaskType = TaskType;
    readonly projects = this.projectService.projects;

    title = "";
    description = "";
    date = "";
    hasTime = false;
    time = "09:00";
    type: TaskType = TaskType.TASK;
    isFeatured = false;
    color = DEFAULT_COLOR;
    projectId: number | null = null;
    saving = signal(false);

    constructor() {
        effect(() => {
            const state = this.state();
            if (!state) return;

            if (state.mode === "create") {
                this.resetForm(state.defaultDate);
            } else {
                this.loadFromTask(state.task);
            }
        });
    }

    private resetForm(date: string): void {
        this.title = "";
        this.description = "";
        this.date = date;
        this.hasTime = false;
        this.time = "09:00";
        this.type = TaskType.TASK;
        this.isFeatured = false;
        this.color = DEFAULT_COLOR;
        this.projectId = null;
    }

    private loadFromTask(task: Task): void {
        const dt = new Date(task.start_datetime);
        this.title = task.title;
        this.description = task.description ?? "";
        this.date = task.start_datetime.slice(0, 10);
        this.hasTime = this.taskService.hasTime(task);
        this.time = formatTimeLabel(dt);
        this.type = task.type;
        this.isFeatured = task.is_featured;
        this.color = task.color;
        this.projectId = task.project_id ?? null;
    }

    get isEdit(): boolean {
        return this.state()?.mode === "edit";
    }

    get isCompletable(): boolean {
        return this.projectId != null || this.type === TaskType.TASK;
    }

    toggleHasTime(): void {
        this.hasTime = !this.hasTime;
    }

    toggleFeatured(): void {
        this.isFeatured = !this.isFeatured;
    }

    private buildStartDatetime(date: string): string {
        const time = this.hasTime ? this.time : "00:00";
        return `${date}T${time}:00`;
    }

    private buildPayload(date: string): TaskCreate | TaskUpdate {
        return {
            title: this.title.trim(),
            description: this.description.trim() || null,
            start_datetime: this.buildStartDatetime(date),
            type: this.type,
            is_featured: this.isFeatured,
            color: this.color,
            project_id: this.projectId
        };
    }


    async onSubmit(): Promise<void> {
        if (!this.title.trim() || !this.date) return;
        this.saving.set(true);

        try {
            const state = this.state();
            if (state?.mode === "edit") {
                await this.taskService.update(state.task.id, this.buildPayload(this.date));
            } else {
                await this.taskService.create(this.buildPayload(this.date) as TaskCreate);
            }

            this.close.emit();
        } finally {
            this.saving.set(false);
        }
    }

    async onDelete(): Promise<void> {
        const state = this.state();
        if (state?.mode !== "edit") return;
        this.saving.set(true);
        try {
            await this.taskService.delete(state.task.id);
            this.close.emit();
        } finally {
            this.saving.set(false);
        }
    }

    onBackdropClick(): void {
        this.close.emit();
    }
}
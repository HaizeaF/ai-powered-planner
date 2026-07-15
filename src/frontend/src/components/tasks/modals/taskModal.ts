import { Component, EventEmitter, Input, Output, effect, inject, signal } from "@angular/core";
import { CommonModule } from "@angular/common";
import { FormsModule } from "@angular/forms";
import { LucideX } from "@lucide/angular";
import { TaskService } from "../../../services/task";
import { ProjectService } from "../../../services/project";
import { COLOR_PALETTE, DEFAULT_COLOR, RecurrenceType, TaskType } from "../../../models/enums";
import { Task, TaskCreate, TaskUpdate } from "../../../models/task";
import { formatTimeLabel } from "../../../utils/dateUtils";

export type TaskModalState = { mode: "create"; defaultDate: string } | { mode: "edit"; task: Task };

@Component({
    selector: "app-task-modal",
    imports: [CommonModule, FormsModule, LucideX],
    templateUrl: "./taskModal.html",
    styleUrl: "./taskModal.css",
})
export class TaskModal {
    private readonly taskService = inject(TaskService);
    private readonly projectService = inject(ProjectService);

    @Input() state: TaskModalState | null = null;
    @Output() close = new EventEmitter<void>();

    readonly colors = COLOR_PALETTE;
    readonly TaskType = TaskType;
    readonly RecurrenceType = RecurrenceType;
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
    recurrence: RecurrenceType = RecurrenceType.NONE;
    saving = signal(false);

    constructor() {
        effect(() => {
            const s = this.state;
            if (!s) return;

            if (s.mode === "create") {
                this.resetForm(s.defaultDate);
            } else {
                this.loadFromTask(s.task);
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
        this.recurrence = RecurrenceType.NONE;
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
        this.recurrence = task.recurrence;
    }

    get isEdit(): boolean {
        return this.state?.mode === "edit";
    }

    get isCompletable(): boolean {
        return this.projectId != null || this.type === TaskType.TASK;
    }

    private buildStartDatetime(): string {
        const time = this.hasTime ? this.time : "00:00";
        return `${this.date}T${time}:00`;
    }

    async onSubmit(): Promise<void> {
        if (!this.title.trim() || !this.date) return;
        this.saving.set(true);

        const payload: TaskCreate | TaskUpdate = {
            title: this.title.trim(),
            description: this.description.trim() || null,
            start_datetime: this.buildStartDatetime(),
            recurrence: this.recurrence,
            type: this.type,
            is_featured: this.isFeatured,
            color: this.color,
            project_id: this.projectId
        };

        try {
        if (this.state?.mode === "edit") {
            await this.taskService.update(this.state.task.id, payload);
        } else {
            await this.taskService.create(payload as TaskCreate);
        }
            this.close.emit();
        } finally {
            this.saving.set(false);
        }
    }

    async onDelete(): Promise<void> {
        if (this.state?.mode !== "edit") return;
        this.saving.set(true);
        try {
            await this.taskService.delete(this.state.task.id);
            this.close.emit();
        } finally {
            this.saving.set(false);
        }
    }

    onBackdropClick(): void {
        this.close.emit();
    }
}
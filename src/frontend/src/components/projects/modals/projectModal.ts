import { Component, EventEmitter, Output, computed, effect, inject, input, signal } from "@angular/core";
import { CommonModule } from "@angular/common";
import { FormsModule } from "@angular/forms";
import { LucideCheck, LucideTrash2, LucideX } from "@lucide/angular";
import { ProjectService } from "../../../services/project";
import { TaskService } from "../../../services/task";
import { COLOR_PALETTE, DEFAULT_COLOR } from "../../../models/enums";
import { Project, ProjectCreate, ProjectUpdate } from "../../../models/project";
import { Task } from "../../../models/task";
import { formatTimeLabel } from "../../../utils/dateUtils";

export type ProjectModalState = { mode: "create" } | { mode: "edit"; project: Project };

@Component({
    selector: "app-project-modal",
    imports: [CommonModule, FormsModule, LucideCheck, LucideTrash2, LucideX],
    templateUrl: "./projectModal.html",
    styleUrl: "./projectModal.css",
})
export class ProjectModal {
    private readonly projectService = inject(ProjectService);
    private readonly taskService = inject(TaskService);

    readonly state = input<ProjectModalState | null>(null);
    @Output() close = new EventEmitter<void>();

    readonly colors = COLOR_PALETTE;
    readonly saving = signal(false);
    readonly editingDetails = signal(false);
    readonly attemptedSubmit = signal(false);

    name = "";
    description = "";
    endDate = "";
    color = DEFAULT_COLOR;

    readonly projectTasks = computed<Task[]>(() => {
        const s = this.state();
        if (s?.mode !== "edit") return [];
        const projectId = s.project.id;
        return this.taskService
            .tasks()
            .filter((t) => t.project_id === projectId)
            .sort((a, b) => a.start_datetime.localeCompare(b.start_datetime));
    });

    readonly completedCount = computed(() => this.projectTasks().filter((t) => t.completed).length);
    readonly totalCount = computed(() => this.projectTasks().length);

    constructor() {
        effect(() => {
            const s = this.state();
            if (!s) return;
            this.editingDetails.set(s.mode === "create");
            this.attemptedSubmit.set(false);

            if (s.mode === "create") {
                this.name = "";
                this.description = "";
                this.endDate = "";
                this.color = DEFAULT_COLOR;
            } else {
                this.name = s.project.name;
                this.description = s.project.description ?? "";
                this.endDate = s.project.end_date ?? "";
                this.color = s.project.color;
            }
        });
    }

    get isEdit(): boolean {
        return this.state()?.mode === "edit";
    }

    get editingProject(): Project | null {
        const s = this.state();
        return s?.mode === "edit" ? s.project : null;
    }

    formatDate(iso: string): string {
        const [y, m, d] = iso.slice(0, 10).split("-");
        return `${d}/${m}/${y}`;
    }

    formatTime(task: Task): string {
        return formatTimeLabel(new Date(task.start_datetime));
    }

    async onSubmit(): Promise<void> {
        this.attemptedSubmit.set(true);
        if (!this.name.trim()) return;
        this.saving.set(true);

        const payload: ProjectCreate | ProjectUpdate = {
            name: this.name.trim(),
            description: this.description.trim() || null,
            end_date: this.endDate || null,
            color: this.color,
        };

        try {
            const s = this.state();
            if (s?.mode === "edit") {
                await this.projectService.update(s.project.id, payload);
                this.editingDetails.set(false);
            } else {
                await this.projectService.create(payload as ProjectCreate);
                this.close.emit();
            }
        } finally {
            this.saving.set(false);
        }
    }

    async onDelete(): Promise<void> {
        const s = this.state();
        if (s?.mode !== "edit") return;
        this.saving.set(true);
        try {
            await this.projectService.delete(s.project.id);
            await this.taskService.loadAll();
            this.close.emit();
        } finally {
            this.saving.set(false);
        }
    }

    async toggleTaskComplete(task: Task): Promise<void> {
        await this.taskService.toggleComplete(task);
    }

    onBackdropClick(): void {
        this.close.emit();
    }

    isCompletable(task: Task): boolean {
        return this.taskService.isCompletable(task);
    }
}
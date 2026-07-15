import { Component, EventEmitter, Output, computed, inject } from "@angular/core";
import { CommonModule } from "@angular/common";
import { LucideCheck } from "@lucide/angular";
import { TaskService } from "../../services/task";
import { SelectedDateService } from "../../services/selectedDate";
import { Task } from "../../models/task";
import { MONTH_LABELS } from "../../utils/dateLabels";
import { formatTimeLabel } from "../../utils/dateUtils";

@Component({
    selector: "app-agenda",
    imports: [CommonModule, LucideCheck],
    templateUrl: "./agenda.html",
    styleUrl: "./agenda.css",
})
export class Agenda {
    private readonly taskService = inject(TaskService);
    private readonly selectedDateService = inject(SelectedDateService);

    @Output() addTask = new EventEmitter<string>();
    @Output() editTask = new EventEmitter<Task>();

    readonly selectedDate = this.selectedDateService.selectedDate;

    readonly dateLabel = computed(() => {
        const [year, month, day] = this.selectedDate().split("-").map(Number);
        return `${MONTH_LABELS[month - 1]} ${day}, ${year}`;
    });

    readonly dayTasks = computed(() => {
        const all = this.taskService.tasks();
        const date = this.selectedDate();
        const tasks = this.taskService.tasksForDay(all, date);

        const withoutTime = tasks.filter((t) => !this.taskService.hasTime(t));
        const withTime = tasks
            .filter((t) => this.taskService.hasTime(t))
            .sort((a, b) => a.start_datetime.localeCompare(b.start_datetime));

        return [...withoutTime, ...withTime];
    });

    readonly progress = computed(() => {
        const completable = this.dayTasks().filter((t) => this.isCompletable(t));
        if (completable.length === 0) return 0;
        const done = completable.filter((t) => t.completed).length;
        return Math.round((done / completable.length) * 100);
    });

    readonly progressStyle = computed(() => ({
        background: `conic-gradient(var(--color-primary) ${this.progress()}%, #e5e0f7 0)`,
    }));

    isCompletable(task: Task): boolean {
        return this.taskService.isCompletable(task);
    }

    hasTime(task: Task): boolean {
        return this.taskService.hasTime(task);
    }

    formatTime(task: Task): string {
        return formatTimeLabel(new Date(task.start_datetime));
    }

    async toggleComplete(event: Event, task: Task): Promise<void> {
        event.stopPropagation();
        await this.taskService.toggleComplete(task);
    }

    onEditTask(task: Task): void {
        this.editTask.emit(task);
    }

    onAddTask(): void {
        this.addTask.emit(this.selectedDate());
    }
}
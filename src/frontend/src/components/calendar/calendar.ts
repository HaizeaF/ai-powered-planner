import { Component, EventEmitter, Output, computed, inject, signal } from "@angular/core";
import { CommonModule } from "@angular/common";
import { LucideChevronLeft, LucideChevronRight, LucideFlag, LucidePlus } from "@lucide/angular";
import { TaskService } from "../../services/task";
import { ProjectService } from "../../services/project";
import { SelectedDateService } from "../../services/selectedDate";
import { Task } from "../../models/task";
import { MONTH_LABELS, WEEKDAY_LABELS } from "../../utils/dateLabels";
import { toIsoDate } from "../../utils/dateUtils";

interface FeaturedItem {
    title: string;
    color: string;
    isDeadline: boolean;
}

interface DayCell {
    date: string;
    dayNumber: number;
    inCurrentMonth: boolean;
    isToday: boolean;
    featuredTasks: FeaturedItem[];
    overflowCount: number;
    totalCount: number;
}

@Component({
    selector: "app-calendar",
    imports: [CommonModule, LucideChevronLeft, LucideChevronRight, LucidePlus, LucideFlag],
    templateUrl: "./calendar.html",
    styleUrl: "./calendar.css"
})
export class Calendar {
    private readonly taskService = inject(TaskService);
    private readonly projectService = inject(ProjectService);
    private readonly selectedDateService = inject(SelectedDateService);

    @Output() addTask = new EventEmitter<string>();

    readonly weekdays = WEEKDAY_LABELS;
    readonly viewDate = signal(new Date());
    readonly selectedDate = this.selectedDateService.selectedDate;
    readonly today = this.selectedDateService.today;

    readonly monthLabel = computed(() => {
        const date = this.viewDate();
        return `${MONTH_LABELS[date.getMonth()]} ${date.getFullYear()}`;
    });

    readonly weeks = computed<DayCell[][]>(() => {
        const tasks = this.taskService.tasks();
        const projects = this.projectService.projects();
        const view = this.viewDate();
        const firstOfMonth = new Date(view.getFullYear(), view.getMonth(), 1);
        const leadingBlank = (firstOfMonth.getDay() + 6) % 7;
        const start = new Date(firstOfMonth);
        start.setDate(start.getDate() - leadingBlank);

        const tasksByDay = new Map<string, Task[]>();
        for (const task of tasks) {
            const day = task.start_datetime.slice(0, 10);
            const list = tasksByDay.get(day) ?? [];
            list.push(task);
            tasksByDay.set(day, list);
        }

        const deadlinesByDay = new Map<string, FeaturedItem[]>();
        for (const project of projects) {
            if (!project.end_date) continue;
            const day = project.end_date.slice(0, 10);
            const list = deadlinesByDay.get(day) ?? [];
            list.push({ title: `${project.name} deadline`, color: project.color, isDeadline: true });
            deadlinesByDay.set(day, list);
        }

        const cells: DayCell[] = [];
        for (let i = 0; i < 42; i++) {
            const date = new Date(start);
            date.setDate(start.getDate() + i);
            const iso = toIsoDate(date);
            const dayTasks = tasksByDay.get(iso) ?? [];
            const deadlines = deadlinesByDay.get(iso) ?? [];
            const remainingSlots = Math.max(3 - deadlines.length, 0);

            const featuredCandidates = dayTasks.filter((t) => t.is_featured);
            const withoutTime = featuredCandidates.filter((t) => !this.taskService.hasTime(t));
            const withTime = featuredCandidates
                .filter((t) => this.taskService.hasTime(t))
                .sort((a, b) => a.start_datetime.localeCompare(b.start_datetime));
            const orderedFeaturedTasks = [...withoutTime, ...withTime]
                .slice(0, remainingSlots)
                .map((t): FeaturedItem => ({ title: t.title, color: t.color, isDeadline: false }));

            const featured = [...deadlines, ...orderedFeaturedTasks];

            cells.push({
                date: iso,
                dayNumber: date.getDate(),
                inCurrentMonth: date.getMonth() === view.getMonth(),
                isToday: iso === this.today,
                featuredTasks: featured,
                overflowCount: Math.max(dayTasks.length - orderedFeaturedTasks.length, 0),
                totalCount: dayTasks.length,
            });
        }

        const weeks: DayCell[][] = [];
        for (let i = 0; i < cells.length; i += 7) {
            weeks.push(cells.slice(i, i + 7));
        }
        const last = weeks[weeks.length - 1];
        if (last.every((c) => !c.inCurrentMonth)) weeks.pop();

        return weeks;
    });

    constructor() {
        this.taskService.loadAll();
        this.projectService.loadAll();
    }

    prevMonth(): void {
        const d = this.viewDate();
        this.viewDate.set(new Date(d.getFullYear(), d.getMonth() - 1, 1));
    }

    nextMonth(): void {
        const d = this.viewDate();
        this.viewDate.set(new Date(d.getFullYear(), d.getMonth() + 1, 1));
    }

    selectDay(cell: DayCell): void {
        this.selectedDateService.select(cell.date);
    }

    onAddTask(event: Event, date: string): void {
        event.stopPropagation();
        this.addTask.emit(date);
    }
}
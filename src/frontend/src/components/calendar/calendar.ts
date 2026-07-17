import { Component, EventEmitter, Output, computed, inject, signal } from "@angular/core";
import { CommonModule } from "@angular/common";
import { LucideChevronLeft, LucideChevronRight, LucidePlus } from "@lucide/angular";
import { TaskService } from "../../services/task";
import { SelectedDateService } from "../../services/selectedDate";
import { Task } from "../../models/task";
import { MONTH_LABELS, WEEKDAY_LABELS } from "../../utils/dateLabels";
import { toIsoDate } from "../../utils/dateUtils";

interface DayCell {
    date: string;
    dayNumber: number;
    inCurrentMonth: boolean;
    isToday: boolean;
    featuredTasks: Task[];
    overflowCount: number;
    totalCount: number;
}

@Component({
    selector: "app-calendar",
    imports: [CommonModule, LucideChevronLeft, LucideChevronRight, LucidePlus],
    templateUrl: "./calendar.html",
    styleUrl: "./calendar.css"
})
export class Calendar {
    private readonly taskService = inject(TaskService);
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

        const cells: DayCell[] = [];
        for (let i = 0; i < 42; i++) {
            const date = new Date(start);
            date.setDate(start.getDate() + i);
            const iso = toIsoDate(date);
            const dayTasks = tasksByDay.get(iso) ?? [];
            const featured = dayTasks.filter((t) => t.is_featured).slice(0, 3);

            cells.push({
                date: iso,
                dayNumber: date.getDate(),
                inCurrentMonth: date.getMonth() === view.getMonth(),
                isToday: iso === this.today,
                featuredTasks: featured,
                overflowCount: Math.max(dayTasks.length - featured.length, 0),
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
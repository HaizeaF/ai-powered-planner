import { Injectable, inject, signal } from "@angular/core";
import { HttpClient } from "@angular/common/http";
import { firstValueFrom } from "rxjs";
import { environment } from "../environments/environment";
import { Task, TaskCreate, TaskUpdate } from "../models/task";

@Injectable({ providedIn: "root" })
export class TaskService {
    private readonly http = inject(HttpClient);
    private readonly baseUrl = `${environment.apiUrl}/tasks`;

    readonly tasks = signal<Task[]>([]);

    async loadAll(): Promise<Task[]> {
        const tasks = await firstValueFrom(this.http.get<Task[]>(this.baseUrl));
        this.tasks.set(tasks);
        return tasks;
    }

    async loadByDay(date: string): Promise<Task[]> {
        return firstValueFrom(this.http.get<Task[]>(this.baseUrl, { params: { task_date: date } }));
    }

    async create(task: TaskCreate): Promise<Task> {
        const created = await firstValueFrom(this.http.post<Task>(this.baseUrl, task));
        this.tasks.update((list) => [...list, created]);
        return created;
    }

    async update(id: number, task: TaskUpdate): Promise<Task> {
        const updated = await firstValueFrom(this.http.patch<Task>(`${this.baseUrl}/${id}`, task));
        this.tasks.update((list) => list.map((t) => (t.id === id ? updated : t)));
        return updated;
    }

    async toggleComplete(task: Task): Promise<Task> {
        return this.update(task.id, { completed: !task.completed });
    }

    async delete(id: number): Promise<void> {
        await firstValueFrom(this.http.delete<void>(`${this.baseUrl}/${id}`));
        this.tasks.update((list) => list.filter((t) => t.id !== id));
    }

    hasTime(task: Pick<Task, 'start_datetime'>): boolean {
        const d = new Date(task.start_datetime);
        return d.getHours() !== 0 || d.getMinutes() !== 0;
    }

    isCompletable(task: Pick<Task, 'type' | 'project_id'>): boolean {
        return task.project_id != null || task.type === 'task';
    }

    tasksForDay(tasks: Task[], date: string): Task[] {
        return tasks.filter((t) => t.start_datetime.slice(0, 10) === date);
    }
}
import { Injectable, inject, signal } from "@angular/core";
import { HttpClient } from "@angular/common/http";
import { firstValueFrom } from "rxjs";
import { environment } from "../environments/environment";
import { Project, ProjectCreate, ProjectUpdate } from "../models/project";

@Injectable({ providedIn: "root" })
export class ProjectService {
    private readonly http = inject(HttpClient);
    private readonly baseUrl = `${environment.apiUrl}/projects`;

    readonly projects = signal<Project[]>([]);

    async loadAll(): Promise<Project[]> {
        const projects = await firstValueFrom(this.http.get<Project[]>(this.baseUrl));
        this.projects.set(projects);
        return projects;
    }

    async create(project: ProjectCreate): Promise<Project> {
        const created = await firstValueFrom(this.http.post<Project>(this.baseUrl, project));
        this.projects.update((list) => [...list, created]);
        return created;
    }

    async update(id: number, project: ProjectUpdate): Promise<Project> {
        const updated = await firstValueFrom(this.http.patch<Project>(`${this.baseUrl}/${id}`, project));
        this.projects.update((list) => list.map((p) => (p.id === id ? updated : p)));
        return updated;
    }

    async delete(id: number): Promise<void> {
        await firstValueFrom(this.http.delete<void>(`${this.baseUrl}/${id}`));
        this.projects.update((list) => list.filter((p) => p.id !== id));
    }
}
import { Component, EventEmitter, Output, computed, inject } from "@angular/core";
import { CommonModule } from "@angular/common";
import { LucidePlus } from "@lucide/angular";
import { ProjectService } from "../../services/project";
import { TaskService } from "../../services/task";
import { ProjectStats } from "../../models/project";
import { TaskType } from "../../models/enums";

@Component({
    selector: "app-projects",
    imports: [CommonModule, LucidePlus],
    templateUrl: "./projects.html",
    styleUrl: "./projects.css",
})
export class Projects {
    private readonly projectService = inject(ProjectService);
    private readonly taskService = inject(TaskService);

    @Output() addProject = new EventEmitter<void>();
    @Output() openProject = new EventEmitter<ProjectStats>();

    readonly projects = computed<ProjectStats[]>(() => {
        const projects = this.projectService.projects();
        const tasks = this.taskService.tasks();

        return projects
        .map((project) => {
            const projectTasks = tasks.filter((t) => t.project_id === project.id && t.type == TaskType.TASK);
            const completedCount = projectTasks.filter((t) => t.completed).length;
            return { ...project, completedCount, totalCount: projectTasks.length };
        })
        .sort((a, b) => {
            if (!a.end_date && !b.end_date) return 0;
            if (!a.end_date) return 1;
            if (!b.end_date) return -1;
            return b.end_date.localeCompare(a.end_date);
        });
    });

    constructor() {
        this.projectService.loadAll();
    }
}
import { Component, EventEmitter, Output, computed, inject } from "@angular/core";
import { CommonModule } from "@angular/common";
import { LucidePlus } from "@lucide/angular";
import { ProjectService } from "../../services/project";
import { TaskService } from "../../services/task";
import { ProjectStats } from "../../models/project";

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
        .filter((p) => !p.archived)
        .map((project) => {
            const projectTasks = tasks.filter((t) => t.project_id === project.id);
            const completedCount = projectTasks.filter((t) => t.completed).length;
            return { ...project, completedCount, totalCount: projectTasks.length };
        });
    });

    constructor() {
        this.projectService.loadAll();
    }
}
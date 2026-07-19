import { Component, signal } from "@angular/core";
import { Calendar } from "../calendar/calendar";
import { Agenda } from "../agenda/agenda";
import { Projects } from "../projects/projects";
import { TaskModal, TaskModalState } from "../tasks/modals/taskModal";
import { ProjectModal, ProjectModalState } from "../projects/modals/projectModal";
import { Task } from "../../models/task";
import { Project } from "../../models/project";

@Component({
    selector: "app-dashboard",
    imports: [Calendar, Agenda, Projects, TaskModal, ProjectModal],
    templateUrl: "./dashboard.html",
    styleUrl: "./dashboard.css",
})
export class Dashboard {
    readonly taskModalState = signal<TaskModalState | null>(null);
    readonly projectModalState = signal<ProjectModalState | null>(null);

    openNewTask(defaultDate: string): void {
        this.taskModalState.set({ mode: "create", defaultDate });
    }

    openEditTask(task: Task): void {
        this.taskModalState.set({ mode: "edit", task });
    }

    openNewProject(): void {
        this.projectModalState.set({ mode: "create" });
    }

    openProject(project: Project): void {
        this.projectModalState.set({ mode: "edit", project });
    }
}
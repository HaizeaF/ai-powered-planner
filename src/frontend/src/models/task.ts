import { Project } from "./project"
import { TaskType } from "./enums"

export interface TaskBase {
    title: string;
    description?: string | null;
    start_datetime: string;
    end_datetime?: string | null;
    type: TaskType;
    is_featured: boolean;
    color: string;
    project_id?: number | null;
}

export type TaskCreate = TaskBase;

export interface TaskUpdate {
    title?: string;
    description?: string | null;
    start_datetime?: string;
    end_datetime?: string | null;
    type?: TaskType;
    is_featured?: boolean;
    color?: string;
    project_id?: number | null;
    completed?: boolean
}

export interface Task extends TaskBase {
    id: number;
    completed: boolean;
    created_at: string;
    project?: Project | null;
}
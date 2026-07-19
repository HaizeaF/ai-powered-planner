export interface ProjectBase {
    name: string;
    description?: string | null;
    end_date?: string | null;
    color: string;
}

export type ProjectCreate = ProjectBase;

export interface ProjectUpdate {
    name?: string;
    description?: string | null;
    end_date?: string | null;
    color?: string;
}

export interface Project extends ProjectBase {
    id: number;
    created_at: string;
}

export interface ProjectStats extends Project {
    completedCount: number;
    totalCount: number;
}
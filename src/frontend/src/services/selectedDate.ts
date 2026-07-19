import { Injectable, signal } from "@angular/core";
import { toIsoDate } from '../utils/dateUtils';


@Injectable({ providedIn: "root" })
export class SelectedDateService {
    readonly today = toIsoDate(new Date())
    readonly selectedDate = signal<string>(this.today);
    
    select(date: string): void {
        this.selectedDate.set(date);
    }
}
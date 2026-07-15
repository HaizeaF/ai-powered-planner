import { Component, signal } from "@angular/core";
import { Dashboard } from "../components/dashboard/dashboard";
import { Chatbot } from "../components/chatbot/chatbot"

@Component({
  selector: 'app-root',
  imports: [Dashboard, Chatbot],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App {
}

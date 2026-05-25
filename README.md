# 🏫 JIIT Campus Assistant (NavBot)

A conversational AI chatbot for the **Jaypee Institute of Information Technology (JIIT)** campus. It helps students navigate the campus, find professors, look up room locations, and get links to useful academic resources — all through a natural chat interface powered by Google Gemini.

---

## ✨ Features

- 🗺️ **Campus Navigation** — Get turn-by-turn directions between buildings, rooms, and landmarks (e.g., Cafe, Library, OAT, Lawn)
- 👨‍🏫 **Professor Lookup** — Find a professor's office location and department by name
- 🚪 **Room Info** — Look up which building and floor any room (e.g., `CR301`) is on
- 📚 **Study Resources** — Directs students to [PYQ JIIT](https://pyqjiit.rushilk.dev) for study material and previous year questions
- 📅 **Attendance & Timetable** — Directs students to [Bunk My JIIT](https://bunkmyjiit.rushilk.dev) for attendance tracking, datesheets, and timetables
- 🗺️ **Map Animation** — Visual map highlighting the route between buildings

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, Flask |
| AI Model | Google Gemini 2.5 Flash (via `google-generativeai`) |
| Routing Algorithm | BFS (Breadth-First Search) on a campus graph |
| Deployment | Gunicorn + Heroku (via `Procfile`) |
| Environment | `python-dotenv` |

---

## 📁 Project Structure

```
├── app.py                  # Main Flask app, Gemini tool definitions, routes
├── requirements.txt        # Python dependencies
├── Procfile                # Heroku deployment config
├── .env                    # Environment variables (not committed)
├── data/
│   ├── campus_graph.json   # Graph of campus zones/nodes for BFS routing
│   ├── campus_nodes_abb1.json  # Room data for ABB1 building
│   ├── campus_nodes_abb3.json  # Room data for ABB3 building
│   └── professors.json     # Professor name, location, and department data
├── utils/
│   └── router.py           # BFS routing logic
└── templates/
    └── index.html          # Frontend chat UI
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- A [Google Gemini API key](https://aistudio.google.com/app/apikey)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/jiit-navbot.git
   cd jiit-navbot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**

   Create a `.env` file in the project root:
   ```
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

4. **Run the app**
   ```bash
   python app.py
   ```

   The app will be available at `http://127.0.0.1:5000`.

---

## ☁️ Deployment (Heroku)

This project includes a `Procfile` for Heroku deployment:

```
web: gunicorn app:app
```

Set your environment variable on Heroku:
```bash
heroku config:set GEMINI_API_KEY=your_gemini_api_key_here
```

---

## 💬 Example Queries

| Query | Response |
|---|---|
| *"How do I get to CR301?"* | Step-by-step directions to the room |
| *"Where is Prof. Sharma's office?"* | Building, room, and department |
| *"Which floor is room AB204 on?"* | Building and floor info |
| *"Where can I find PYQs?"* | Link to [pyqjiit.rushilk.dev](https://pyqjiit.rushilk.dev) |
| *"How do I check my attendance?"* | Link to [bunkmyjiit.rushilk.dev](https://bunkmyjiit.rushilk.dev) |

---

## 🗺️ Campus Zones

The BFS router uses the following zones:

- `GATE_1` — Main campus entrance
- `ABB1_ENTRANCE` — Academic Block B1
- `ABB3_ENTRANCE` — Academic Block B3 (also covers Cafe, Library/LRC, Portico, Basketball court)
- `OAT_ROAD` — Open Air Theatre
- `LAWN` — Campus lawn area

---

## 📄 License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

---

## 🙏 Credits

Developed by **Naisha Sharma**.  
External resources integrated:
- [PYQ JIIT](https://pyqjiit.rushilk.dev) by Rushil K
- [Bunk My JIIT](https://bunkmyjiit.rushilk.dev) by Rushil K

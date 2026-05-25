# Copyright (c) 2025 Naisha Sharma
# Licensed under the MIT License
from flask import Flask, render_template, request, jsonify, session
import json
import re
import os
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv
import google.generativeai as genai
from utils.router import bfs_route

load_dotenv()
API_KEY = os.environ.get("GEMINI_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)

# Change working directory to the directory of app.py to resolve relative paths
os.chdir(os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__)
app.secret_key = "navbot-secret-key"

# ---------------- LOAD DATA ----------------
with open("data/campus_graph.json") as f:
    campus_graph = json.load(f)

with open("data/campus_nodes_abb1.json") as f:
    abb1 = json.load(f)["ABB1"]

with open("data/campus_nodes_abb3.json") as f:
    abb3 = json.load(f)["ABB3"]

try:
    with open("data/professors.json") as f:
        professors_data = json.load(f)
except FileNotFoundError:
    professors_data = []

# ---------------- HELPERS ----------------
ALL_ROOMS = set()
for floor_rooms in abb1.values():
    ALL_ROOMS.update(floor_rooms.keys())
for floor_rooms in abb3.values():
    ALL_ROOMS.update(floor_rooms.keys())

LANDMARK_ZONES = {
    "CAFE": "ABB3_ENTRANCE",
    "PORTICO": "ABB3_ENTRANCE",
    "BASKETBALL": "ABB3_ENTRANCE",
    "LIBRARY": "ABB3_ENTRANCE",
    "LRC": "ABB3_ENTRANCE",
    "OAT": "OAT_ROAD",
    "LAWN": "LAWN"
}

def find_room_building(room):
    for floor, rooms in abb1.items():
        if room in rooms:
            return "ABB1"
    for floor, rooms in abb3.items():
        if room in rooms:
            return "ABB3"
    return None

def find_room_floor(room):
    for floor, rooms in abb1.items():
        if room in rooms:
            return "ABB1", floor
    for floor, rooms in abb3.items():
        if room in rooms:
            return "ABB3", floor
    return None, None

def building_to_zone(building):
    if building == "ABB1":
        return "ABB1_ENTRANCE"
    if building == "ABB3":
        return "ABB3_ENTRANCE"
    return "GATE_1"

def detect_landmark_zone(text):
    for key, zone in LANDMARK_ZONES.items():
        if key in text.upper():
            return zone
    return None

# ---------------- GEMINI TOOLS ----------------
def get_navigation_route(start_location: str, end_location: str) -> str:
    """
    Calculate the route from start_location to end_location.
    Locations can be room numbers (e.g. 'CR301'), or landmarks like 'LIBRARY', 'CAFE', 'GATE_1'.
    If start_location is unknown, use 'GATE_1' as default entrance.
    """
    start_location = start_location.upper()
    end_location = end_location.upper()
    
    start_zone = detect_landmark_zone(start_location)
    start_building = "ABB3" if start_zone else find_room_building(start_location)
    if not start_zone:
        start_zone = building_to_zone(start_building) if start_building else "GATE_1"
        start_building = start_building or "GATE"

    end_building = find_room_building(end_location)
    if not end_building:
        end_zone = detect_landmark_zone(end_location)
        if end_zone:
            end_building = "ABB3"
            destination_zone = end_zone
        else:
            return f"Could not find destination: {end_location}"
    else:
        destination_zone = building_to_zone(end_building)
    
    # Save to session for map animation
    if start_building in ["ABB1", "ABB3", "OAT"] and end_building in ["ABB1", "ABB3", "OAT"]:
        session["map_start"] = start_building
        session["map_end"] = end_building

    if start_zone == destination_zone:
        return f"You are already in {end_building}. Proceed to {end_location}."
        
    path = bfs_route(campus_graph, start_zone, destination_zone)
    if not path:
        return "Could not find a valid route."
        
    if start_zone != "GATE_1":
        path = [p for p in path if "Gate" not in p]
        
    path.append(f"Once inside {end_building}, proceed to {end_location}.")
    return " -> ".join(path)

def find_professor(name: str) -> str:
    """
    Search for a professor's location and department by name.
    """
    name_lower = name.lower()
    matches = [p for p in professors_data if name_lower in p["name"].lower()]
    if matches:
        return "\n".join([f"- **{p['name']}**: {p['location']} ({p['department']})" for p in matches])
    return "Professor not found in records."

def get_room_details(room: str) -> str:
    """
    Get the building and floor for a specific room number (e.g., 'CR301').
    """
    building, floor = find_room_floor(room.upper())
    if building:
        return f"Room {room.upper()} is located in **{building}** on the **{floor.replace('_', ' ').lower()}**."
    return "Room not found."

# ---------------- SYSTEM INSTRUCTION ----------------
SYSTEM_INSTRUCTION = """You are the JIIT Campus Assistant, a helpful AI bot for the Jaypee Institute of Information Technology (JIIT).
You help students with:
1. Navigation around campus (use the get_navigation_route tool).
2. Finding professors' locations (use the find_professor tool).
3. Finding which floor/building a room is on (use the get_room_details tool).
4. For Study Material and Previous Year Questions (PYQs), tell students to visit: [PYQ JIIT](https://pyqjiit.rushilk.dev)
5. For Attendance tracking, Datesheets, and timetable, tell students to visit: [Bunk My JIIT](https://bunkmyjiit.rushilk.dev)

CRITICAL INSTRUCTION: Your primary goal when asked about study material, PYQs, attendance, or datesheets is to point the user to the respective link above. Do not try to answer those questions yourself, just give them a short, helpful message with the link.
Be conversational, polite, and use markdown for formatting (bold, links, lists).
When you give directions, present them clearly. 
Do not mention that you are using tools, just provide the answer seamlessly.
"""

# ---------------- ROUTES ----------------
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/get", methods=["POST"])
def chat():
    text = request.form.get("msg", "").strip()
    if not text:
        return jsonify("Please enter something.")

    if not API_KEY:
        return jsonify("The Gemini API key is missing. Please add it to the .env file in the root directory.")

    # Clear previous map route from session
    session.pop("map_start", None)
    session.pop("map_end", None)

    try:
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            tools=[get_navigation_route, find_professor, get_room_details],
            system_instruction=SYSTEM_INSTRUCTION
        )
        
        chat_session = model.start_chat(enable_automatic_function_calling=True)
        response = chat_session.send_message(text)
        
        response_data = {
            "text": response.text
        }
        
        if "map_start" in session and "map_end" in session:
            response_data["start"] = session["map_start"]
            response_data["end"] = session["map_end"]
            
        return jsonify(response_data)
        
    except Exception as e:
        print(f"Error: {e}")
        return jsonify("Sorry, I encountered an error while processing your request. Check console for details.")

if __name__ == "__main__":
    app.run(debug=True)

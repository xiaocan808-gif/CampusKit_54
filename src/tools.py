#!/usr/bin/env python3
"""CampusKit_54 - Campus Utility Toolkit"""

import argparse
import json
import sqlite3
from datetime import datetime
from pathlib import Path


def calculate_gpa(grades_str, scale=5.0):
    """Calculate weighted GPA."""
    courses = []
    total_points = 0.0
    total_credits = 0.0
    for item in grades_str.split(","):
        parts = item.strip().split(":")
        name = parts[0].strip()
        score = float(parts[1].strip())
        credit = float(parts[2].strip()) if len(parts) > 2 else 1.0
        if scale == 5.0:
            if score >= 90: gp = 5.0
            elif score >= 80: gp = 4.0
            elif score >= 70: gp = 3.0
            elif score >= 60: gp = 2.0
            else: gp = 1.0
        else:
            if score >= 90: gp = 4.0
            elif score >= 85: gp = 3.7
            elif score >= 82: gp = 3.3
            elif score >= 78: gp = 3.0
            elif score >= 75: gp = 2.7
            elif score >= 72: gp = 2.3
            elif score >= 68: gp = 2.0
            elif score >= 64: gp = 1.5
            elif score >= 60: gp = 1.0
            else: gp = 0.0
        total_points += gp * credit
        total_credits += credit
        courses.append({"name": name, "score": score, "credit": credit, "grade_point": gp})
    gpa = total_points / total_credits if total_credits > 0 else 0.0
    return {"gpa": round(gpa, 2), "scale": scale, "total_credits": total_credits, "courses": courses}


def get_db_path():
    db_dir = Path.home() / ".campus54"
    db_dir.mkdir(exist_ok=True)
    return db_dir / "data.db"


def add_course(name, day, period, room, teacher=""):
    conn = sqlite3.connect(str(get_db_path()))
    conn.execute("""CREATE TABLE IF NOT EXISTS courses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL, day_of_week TEXT NOT NULL,
        period TEXT, room TEXT, teacher TEXT)""")
    conn.execute("INSERT INTO courses (name, day_of_week, period, room, teacher) VALUES (?,?,?,?,?)",
                 (name, day, period, room, teacher))
    conn.commit()
    conn.close()
    return {"status": "success", "message": f"Course '{name}' added."}


def query_schedule(day=None):
    conn = sqlite3.connect(str(get_db_path()))
    cursor = conn.cursor()
    if day:
        cursor.execute("SELECT * FROM courses WHERE day_of_week=? ORDER BY period", (day,))
    else:
        cursor.execute("SELECT * FROM courses ORDER BY day_of_week, period")
    rows = cursor.fetchall()
    conn.close()
    return [{"name": r[1], "day": r[2], "period": r[3], "room": r[4]} for r in rows]


def countdown(target_date, event_name="Event"):
    target = datetime.strptime(target_date, "%Y-%m-%d")
    delta = (target - datetime.now()).days
    if delta < 0:
        return {"event": event_name, "status": "passed", "days_ago": abs(delta)}
    elif delta == 0:
        return {"event": event_name, "status": "today"}
    else:
        return {"event": event_name, "status": "upcoming", "days_remaining": delta}


def main():
    parser = argparse.ArgumentParser(description="CampusKit_54 - Campus Utility Toolkit")
    subparsers = parser.add_subparsers(dest="command")
    gpa_p = subparsers.add_parser("gpa", help="Calculate GPA")
    gpa_p.add_argument("--grades", required=True)
    gpa_p.add_argument("--scale", type=float, default=5.0)
    sched_p = subparsers.add_parser("schedule", help="Manage schedule")
    sched_sub = sched_p.add_subparsers(dest="action")
    add_p = sched_sub.add_parser("add")
    add_p.add_argument("--name", required=True)
    add_p.add_argument("--day", required=True)
    add_p.add_argument("--period", default="")
    add_p.add_argument("--room", default="")
    add_p.add_argument("--teacher", default="")
    cd_p = subparsers.add_parser("countdown", help="Countdown to date")
    cd_p.add_argument("--date", required=True)
    cd_p.add_argument("--name", default="Event")
    args = parser.parse_args()
    if args.command == "gpa":
        print(json.dumps(calculate_gpa(args.grades, args.scale), ensure_ascii=False, indent=2))
    elif args.command == "schedule":
        if args.action == "add":
            print(json.dumps(add_course(args.name, args.day, args.period, args.room, args.teacher), ensure_ascii=False, indent=2))
        else:
            print(json.dumps(query_schedule(args.day), ensure_ascii=False, indent=2))
    elif args.command == "countdown":
        print(json.dumps(countdown(args.date, args.name), ensure_ascii=False, indent=2))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

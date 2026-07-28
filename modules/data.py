"""
Data management for FEST application.
Handles CRUD operations for student records and GPA scale.
"""

import os
import json
import pandas as pd


class DataManager:
    """Manages student records and GPA scale data."""

    def __init__(self):
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.students_file = os.path.join(self.base_dir, "students.csv")
        self.gpa_scale_file = os.path.join(self.base_dir, "gpa_scale.json")
        self.student_fields = ["student_id", "name", "major", "course_code",
                               "course_title", "points", "gpa"]

        # Default GPA scale
        self.default_gpa_scale = [
            (97, 100, "A+", 4.0), (93, 96, "A", 4.0), (90, 92, "A-", 3.7),
            (87, 89, "B+", 3.3), (83, 86, "B", 3.0), (80, 82, "B-", 2.7),
            (77, 79, "C+", 2.3), (73, 76, "C", 2.0), (70, 72, "C-", 1.7),
            (67, 69, "D+", 1.3), (63, 66, "D", 1.0), (60, 62, "D-", 0.7),
            (0, 59, "F", 0.0),
        ]
        self.gpa_scale = list(self.default_gpa_scale)
        self.load_gpa_scale()

    def load_students(self):
        """Load all student records from CSV."""
        if not os.path.exists(self.students_file):
            return []
        try:
            df = pd.read_csv(self.students_file, dtype=str, keep_default_na=False)
            return df.to_dict("records")
        except pd.errors.EmptyDataError:
            return []

    def save_students(self, records):
        """Save all student records to CSV."""
        df = pd.DataFrame(records, columns=self.student_fields)
        df.to_csv(self.students_file, index=False)

    def append_student(self, record):
        """Append a single student record to CSV."""
        exists = os.path.exists(self.students_file)
        row = pd.DataFrame([record], columns=self.student_fields)
        row.to_csv(self.students_file, mode="a", header=not exists, index=False)

    def get_student_by_id(self, student_id):
        """Get all records for a specific student ID."""
        records = self.load_students()
        return [r for r in records if r["student_id"] == student_id]

    def get_unique_students(self):
        """Get unique student IDs and their first record."""
        records = self.load_students()
        student_dict = {}
        for r in records:
            if r["student_id"] not in student_dict:
                student_dict[r["student_id"]] = r
        return list(student_dict.values())

    def load_gpa_scale(self):
        """Load GPA scale from JSON file."""
        if os.path.exists(self.gpa_scale_file):
            try:
                with open(self.gpa_scale_file) as f:
                    data = json.load(f)
                self.gpa_scale = [tuple(row) for row in data]
                return
            except Exception:
                pass
        self.gpa_scale = list(self.default_gpa_scale)

    def save_gpa_scale(self):
        """Save GPA scale to JSON file."""
        with open(self.gpa_scale_file, "w") as f:
            json.dump(self.gpa_scale, f, indent=2)

    def reset_gpa_scale(self):
        """Reset GPA scale to defaults."""
        self.gpa_scale = list(self.default_gpa_scale)
        self.save_gpa_scale()

    def points_to_grade(self, points):
        """Convert points to letter grade and GPA."""
        p = max(0, min(100, round(float(points))))
        for lo, hi, letter, gpa in self.gpa_scale:
            if lo <= p <= hi:
                return letter, gpa
        return "F", 0.0

    def grade_category(self, points):
        """Get grade category for color coding."""
        p = float(points)
        if p >= 90: return "A (90-100)"
        if p >= 80: return "B (80-89)"
        if p >= 70: return "C (70-79)"
        if p >= 60: return "D (60-69)"
        return "F (0-59)"

    def get_student_statistics(self):
        """
        Calculate comprehensive statistics about students.
        This is the new feature: Academic Statistics Dashboard.
        """
        records = self.load_students()
        if not records:
            return None

        # Basic statistics
        total_students = len({r["student_id"] for r in records})
        total_courses = len(records)

        # GPA statistics
        gpas = []
        student_gpas = {}
        for r in records:
            try:
                gpa = float(r["gpa"])
                gpas.append(gpa)
                student_gpas.setdefault(r["student_id"], []).append(gpa)
            except (ValueError, TypeError):
                continue

        avg_gpa = sum(gpas) / len(gpas) if gpas else 0
        max_gpa = max(gpas) if gpas else 0
        min_gpa = min(gpas) if gpas else 0

        # Per-student average GPA
        student_avg_gpas = [sum(gpas_list) / len(gpas_list)
                            for gpas_list in student_gpas.values()]
        avg_student_gpa = sum(student_avg_gpas) / len(student_avg_gpas) if student_avg_gpas else 0

        # Grade distribution
        grade_dist = {"A": 0, "B": 0, "C": 0, "D": 0, "F": 0}
        for r in records:
            try:
                letter, _ = self.points_to_grade(float(r["points"]))
                grade_dist[letter[0]] = grade_dist.get(letter[0], 0) + 1
            except (ValueError, TypeError):
                grade_dist["F"] = grade_dist.get("F", 0) + 1

        # Major distribution
        major_counts = {}
        for r in records:
            major = r.get("major", "Unknown").strip()
            major_counts[major] = major_counts.get(major, 0) + 1

        # Course statistics
        course_stats = {}
        for r in records:
            course = r.get("course_title", "Unknown")
            if course not in course_stats:
                course_stats[course] = {"scores": [], "students": set()}
            try:
                course_stats[course]["scores"].append(float(r["points"]))
            except (ValueError, TypeError):
                pass
            course_stats[course]["students"].add(r.get("student_id", ""))

        # Calculate course averages
        course_averages = {}
        for course, stats in course_stats.items():
            if stats["scores"]:
                course_averages[course] = {
                    "avg": sum(stats["scores"]) / len(stats["scores"]),
                    "students": len(stats["students"])
                }

        # Top performing students
        student_avg_dict = {}
        for sid, gpas_list in student_gpas.items():
            if gpas_list:
                student_avg_dict[sid] = sum(gpas_list) / len(gpas_list)

        top_students = sorted(student_avg_dict.items(),
                              key=lambda x: x[1], reverse=True)[:5]

        return {
            "total_students": total_students,
            "total_courses": total_courses,
            "avg_gpa": avg_gpa,
            "max_gpa": max_gpa,
            "min_gpa": min_gpa,
            "avg_student_gpa": avg_student_gpa,
            "grade_distribution": grade_dist,
            "major_distribution": major_counts,
            "course_averages": course_averages,
            "top_students": top_students,
        }
def get_grade(marks: float) -> str:
    """Returns the letter grade based on marks."""
    if marks >= 90:
        return "A+"
    elif marks >= 80:
        return "A"
    elif marks >= 70:
        return "B+"
    elif marks >= 60:
        return "B"
    elif marks >= 50:
        return "C"
    elif marks >= 40:
        return "D"
    return "F"


def get_grade_point(marks: float) -> int:
    """Returns the grade point based on marks."""
    if marks >= 90:
        return 10
    elif marks >= 80:
        return 9
    elif marks >= 70:
        return 8
    elif marks >= 60:
        return 7
    elif marks >= 50:
        return 6
    elif marks >= 40:
        return 5
    return 0


def calculate_sgpa(subjects: list[dict]) -> float:
    """
    Calculates SGPA from a list of subject dictionaries.
    Each dictionary should have 'marks' and 'credits' keys.
    """
    if not subjects:
        return 0.0

    total_points = 0
    total_credits = 0

    for subject in subjects:
        # Using dictionary keys avoids rigid index-matching bugs
        marks = subject.get("marks", 0)
        credits = subject.get("credits", 0)

        grade_point = get_grade_point(marks)
        total_points += grade_point * credits
        total_credits += credits

    if total_credits == 0:
        return 0.0

    return round(total_points / total_credits, 2)


# --- Example Usage ---
if __name__ == "__main__":
    semester_subjects = [
        {"name": "Mathematics", "marks": 85, "credits": 4},
        {"name": "Physics", "marks": 72, "credits": 3},
        {"name": "Computer Science", "marks": 95, "credits": 4},
        {"name": "English", "marks": 45, "credits": 2},
    ]

    sgpa = calculate_sgpa(semester_subjects)
    print(f"Your SGPA for this semester is: {sgpa}")

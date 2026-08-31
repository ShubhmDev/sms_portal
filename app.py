import streamlit as st
import pandas as pd

from database import (
    create_tables,
    add_student,
    get_students,
    update_student,
    delete_student,
    add_marks,
    get_marks,
    delete_marks
)

from calculations import (
    get_grade,
    calculate_sgpa
)

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------
st.set_page_config(
    page_title="Student Management System",
    page_icon="🎓",
    layout="wide"
)

# --------------------------------------------------
# CREATE DATABASE
# --------------------------------------------------
create_tables()

# --------------------------------------------------
# TITLE
# --------------------------------------------------
st.title("🎓 Student Management & CGPA Dashboard")
st.write("Manage students, subjects, marks and academic performance.")

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Go to",
    ["Dashboard", "Students", "Marks & CGPA"]
)

# ==================================================
# DASHBOARD
# ==================================================
if page == "Dashboard":
    st.header("📊 Dashboard")
    students = get_students()
    total_students = len(students)

    st.metric("Total Students", total_students)

    if students:
        student_data = []

        for student in students:
            student_id = student[0]
            name = student[1]
            course = student[3]
            semester = student[4]

            # Fetch database marks: list of tuples (id, subject, marks, credits)
            db_marks = get_marks(student_id)
            
            # Map database tuples into structured dictionaries expected by calculations.py
            formatted_marks = [
                {"subject": row[1], "marks": row[2], "credits": row[3]} 
                for row in db_marks
            ]

            sgpa = calculate_sgpa(formatted_marks)

            student_data.append({
                "Name": name,
                "Course": course,
                "Semester": semester,
                "SGPA": sgpa
            })

        df = pd.DataFrame(student_data)

        col1, col2, col3 = st.columns(3)
        col1.metric("Class Average", round(df["SGPA"].mean(), 2))
        col2.metric("Highest SGPA", round(df["SGPA"].max(), 2))
        col3.metric("Lowest SGPA", round(df["SGPA"].min(), 2))

        st.subheader("📋 Student Performance")
        st.dataframe(df, use_container_width=True)

        st.subheader("📈 SGPA Distribution")
        chart_data = df.set_index("Name")["SGPA"]
        st.bar_chart(chart_data)
    else:
        st.info("No students available. Add students from the Students page.")

# ==================================================
# STUDENTS
# ==================================================
elif page == "Students":
    st.header("👨‍🎓 Student Management")
    tab1, tab2, tab3 = st.tabs(["Add Student", "View Students", "Delete Student"])

    # ----------------------------------------------
    # ADD STUDENT
    # ----------------------------------------------
    with tab1:
        st.subheader("Add New Student")
        with st.form("student_form"):
            name = st.text_input("Student Name")
            email = st.text_input("Email")
            course = st.selectbox("Course", ["BBA", "BCA", "B.Com", "B.Sc", "MBA", "MCA"])
            semester = st.number_input("Semester", min_value=1, max_value=8, step=1)
            submitted = st.form_submit_button("Add Student")

            if submitted:
                if name.strip() == "":
                    st.error("Please enter the student's name.")
                else:
                    add_student(name, email, course, semester)
                    st.success(f"{name} added successfully!")
                    st.rerun()

    # ----------------------------------------------
    # VIEW STUDENTS
    # ----------------------------------------------
    with tab2:
        students = get_students()
        if students:
            df = pd.DataFrame(students, columns=["ID", "Name", "Email", "Course", "Semester"])
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No students found.")

    # ----------------------------------------------
    # DELETE STUDENT
    # ----------------------------------------------
    with tab3:
        students = get_students()
        if students:
            student_options = {f"{s[1]} (ID: {s[0]})": s[0] for s in students}
            selected_student = st.selectbox("Select Student to Delete", list(student_options.keys()))
            student_id = student_options[selected_student]

            if st.button("Delete Student", type="primary"):
                delete_student(student_id)
                st.success("Student deleted successfully.")
                st.rerun()
        else:
            st.info("No students available.")

# ==================================================
# MARKS & CGPA
# ==================================================
elif page == "Marks & CGPA":
    st.header("📝 Marks & Performance Tracking")
    students = get_students()

    if not students:
        st.warning("Please add students first.")
    else:
        student_options = {f"{s[1]} (ID: {s[0]})": s[0] for s in students}
        selected_student = st.selectbox("Select Student", list(student_options.keys()))
        student_id = student_options[selected_student]

        col1, col2 = st.columns([1, 2])

        # ------------------------------------------
        # ADD MARKS FORM
        # ------------------------------------------
        with col1:
            st.subheader("Add Subject Marks")
            with st.form("marks_form", clear_on_submit=True):
                subject = st.text_input("Subject Name")
                marks = st.number_input("Marks", min_value=0.0, max_value=100.0, step=1.0)
                credits = st.number_input("Credits", min_value=1, max_value=6, value=3)
                submitted = st.form_submit_button("Add Marks")

                if submitted:
                    if subject.strip() == "":
                        st.error("Please enter a subject name.")
                    else:
                        add_marks(student_id, subject, marks, credits)
                        st.success(f"Added marks for {subject} successfully!")
                        st.rerun()

        # ------------------------------------------
        # VIEW MARKS & CURRENT SGPA
        # ------------------------------------------
        with col2:
            st.subheader("Report Card & SGPA Summary")
            db_marks = get_marks(student_id)

            if db_marks:
                # Structure the data for display and logic conversions
                marks_data = []
                formatted_for_calc = []

                for row in db_marks:
                    m_id, sub, m_val, cred = row
                    letter_grade = get_grade(m_val)
                    
                    marks_data.append({
                        "Mark ID": m_id,
                        "Subject": sub,
                        "Marks": m_val,
                        "Credits": cred,
                        "Grade": letter_grade
                    })
                    
                    formatted_for_calc.append({
                        "marks": m_val,
                        "credits": cred
                    })

                df_marks = pd.DataFrame(marks_data)
                
                # Show Calculated SGPA Metric prominently
                current_sgpa = calculate_sgpa(formatted_for_calc)
                st.metric(label="Current Semester SGPA", value=f"{current_sgpa} / 10.0")

                # Show details table
                st.dataframe(df_marks.drop(columns=["Mark ID"]), use_container_width=True)

                # Delete specific subject mark entry option
                st.markdown("---")
                st.caption("Remove Incorrect Entry")
                mark_options = {f"{row['Subject']} ({row['Marks']} Marks)": row['Mark ID'] for row in marks_data}
                selected_mark_to_delete = st.selectbox("Select entry to delete", list(mark_options.keys()))
                
                if st.button("Remove Entry", type="secondary"):
                    delete_marks(mark_options[selected_mark_to_delete])
                    st.success("Entry removed.")
                    st.rerun()
            else:
                st.info("No marks entries recorded for this student yet.")

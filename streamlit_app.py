import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="☕ Prof. Haikel Hichri Java Lab", layout="wide")

API_URL = "https://java-grader-backend.fly.dev"  # Update with your actual Fly.io URL

st.title("☕ Prof. Haikel Hichri Java Lab")

# Sidebar navigation
page = st.sidebar.radio("Navigation", ["Submit Lab", "Admin Dashboard"])

# ========== SUBMIT LAB PAGE ==========
if page == "Submit Lab":
    st.header("Submit Your Lab")
  
    student_id = st.text_input("Student ID", placeholder="e.g., s001")
  
    # Auto-lookup student name
    student_name = ""
    if student_id:
        try:
            resp = requests.post(f"{API_URL}/lookup_student", json={"student_id": student_id})
            if resp.status_code == 200:
                student_name = resp.json()["name"]
                st.success(f"✅ Welcome, **{student_name}**!")
            else:
                st.error("❌ Student ID not found. Please check with your instructor.")
        except Exception as e:
            st.error(f"Connection error: {e}")
    ####################################################################################
    lab_id = st.selectbox("Select Lab", ["lab07", "lab06", "lab05", "lab04", "lab03", "lab02", "lab01"])
    # 2. Select Problem (only show for Lab 06 or others with multiple problems)
    problem_id = "none"
    if lab_id == "lab06" or lab_id == "lab07":  # Assuming lab07 also has multiple problems
        problem_id = st.selectbox("Select Problem", ["p1", "p2", "p3", "p4"])
    else:
        # For older labs that don't have sub-problems
        problem_id = "none"
    # Track lab/problem selection and reset uploader key when selection changes
    current_selection = f"{lab_id}_{problem_id}"
    if st.session_state.get("last_selection") != current_selection:
        st.session_state["last_selection"] = current_selection
        st.session_state["uploader_key"] = st.session_state.get("uploader_key", 0) + 1

    # File uploader for multiple .java files (key forces reset when lab/problem changes)
    uploaded_files = st.file_uploader(
        """
        YOU MUST UPLOAD ALL REQUIRED .JAVA FILES FOR YOUR LAB PROBLEM.
        YOU MUST ALSO UPLOAD YOUR FINAL SOLUTION ON MOODLE TO GET FULL CREDIT.
        Upload your .java files of the Campus Fleet Management System
        """,
        type=["java"],
        accept_multiple_files=True,
        help="For labs with multiple classes, upload all required .java files",
        key=f"file_uploader_{st.session_state.get('uploader_key', 0)}"
    )
    #######################################################################################
    if st.button("Submit", type="primary"):
        if not student_id:
            st.error("Please enter your Student ID")
        elif not uploaded_files:
            st.error("Please upload at least one .java file")
        else:
            # Combine all files with FILE markers
            code_parts = []
            for uploaded_file in uploaded_files:
                file_content = uploaded_file.read().decode("utf-8")
                code_parts.append(f"// FILE: {uploaded_file.name}\n{file_content}")
          
            combined_code = "\n\n".join(code_parts)
          
            # Send to backend
            with st.spinner("Grading your submission..."):
                try:
                    # Combine them for the backend: "lab06_p1" or just "lab05"
                    final_lab_id = f"{lab_id}_{problem_id}" if problem_id != "none" else lab_id
                    payload = {
                        "student_id": student_id,
                        "lab_id": final_lab_id,
                        "code": combined_code
                    }
                    resp = requests.post(f"{API_URL}/grade", json=payload, timeout=30)
                  
                    if resp.status_code == 200:
                        result = resp.json()
                        st.success(f"✅ Graded! Score: **{result['score']}/{result['max_score']}**")
                        st.text_area("Feedback", result["feedback"], height=400)
                    else:
                        st.error(f"Error {resp.status_code}: {resp.json().get('detail', 'Unknown error')}")
                except Exception as e:
                    st.error(f"Submission failed: {e}")


# ========== VIEW MY GRADES PAGE ==========
elif page == "View My Grades":
    st.header("My Submissions")
  
    student_id = st.text_input("Enter your Student ID", placeholder="e.g., s001")
  
    if st.button("Load My Grades"):
        if not student_id:
            st.error("Please enter your Student ID")
        else:
            try:
                resp = requests.get(f"{API_URL}/student/{student_id}/submissions")
                if resp.status_code == 200:
                    data = resp.json()
                    if data["submissions"]:
                        df = pd.DataFrame(data["submissions"])
                        st.dataframe(df, use_container_width=True)
                    else:
                        st.info("No submissions yet.")
                else:
                    st.error(f"Error: {resp.json().get('detail', 'Unknown error')}")
            except Exception as e:
                st.error(f"Failed to load grades: {e}")

# ========== ADMIN DASHBOARD PAGE ==========
elif page == "Admin Dashboard":
    st.header("🔒 Admin Dashboard")
  
    # Initialize session state for login
    if "admin_logged_in" not in st.session_state:
        st.session_state.admin_logged_in = False
        st.session_state.admin_username = ""
        st.session_state.admin_password = ""
  
    # Login form
    if not st.session_state.admin_logged_in:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
      
        if st.button("Login"):
            try:
                resp = requests.get(
                    f"{API_URL}/admin/all_submissions",
                    auth=(username, password)
                )
                if resp.status_code == 200:
                    st.session_state.admin_logged_in = True
                    st.session_state.admin_username = username
                    st.session_state.admin_password = password
                    st.rerun()
                else:
                    st.error("❌ Invalid credentials")
            except Exception as e:
                st.error(f"Login failed: {e}")
  
    # Show dashboard if logged in
    else:
        col1, col2 = st.columns([6, 1])
        with col1:
            st.success(f"✅ Logged in as {st.session_state.admin_username}")
        with col2:
            if st.button("Logout"):
                st.session_state.admin_logged_in = False
                st.rerun()
      
        try:
            # Fetch all submissions
            resp = requests.get(
                f"{API_URL}/admin/all_submissions",
                auth=(st.session_state.admin_username, st.session_state.admin_password)
            )
          
            if resp.status_code == 200:
                data = resp.json()
                st.info(f"Total submissions: {data['total']}")
              
                if data["submissions"]:
                    df = pd.DataFrame(data["submissions"])
                    st.dataframe(df, use_container_width=True)
                  
                    # Fetch CSV for download
                    csv_resp = requests.get(
                        f"{API_URL}/admin/export_csv",
                        auth=(st.session_state.admin_username, st.session_state.admin_password)
                    )
                  
                    if csv_resp.status_code == 200:
                        csv_data = csv_resp.json()["csv"]
                        st.download_button(
                            label="📥 Download CSV with Feedback",
                            data=csv_data,
                            file_name="grades.csv",
                            mime="text/csv",
                            type="primary"
                        )
                else:
                    st.info("No submissions yet.")
            else:
                st.error("Session expired. Please login again.")
                st.session_state.admin_logged_in = False
                st.rerun()
              
        except Exception as e:
            st.error(f"Error loading dashboard: {e}")import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="☕ Prof. Haikel Hichri Java Lab", layout="wide")

API_URL = "https://java-grader-backend.fly.dev"  # Update with your actual Fly.io URL

st.title("☕ Prof. Haikel Hichri Java Lab")

# Sidebar navigation
page = st.sidebar.radio("Navigation", ["Submit Lab", "Admin Dashboard"])

# ========== SUBMIT LAB PAGE ==========
if page == "Submit Lab":
    st.header("Submit Your Lab")
  
    student_id = st.text_input("Student ID", placeholder="e.g., s001")
  
    # Auto-lookup student name
    student_name = ""
    if student_id:
        try:
            resp = requests.post(f"{API_URL}/lookup_student", json={"student_id": student_id})
            if resp.status_code == 200:
                student_name = resp.json()["name"]
                st.success(f"✅ Welcome, **{student_name}**!")
            else:
                st.error("❌ Student ID not found. Please check with your instructor.")
        except Exception as e:
            st.error(f"Connection error: {e}")
    ####################################################################################
    lab_id = st.selectbox("Select Lab", ["lab07", "lab06", "lab05", "lab04", "lab03", "lab02", "lab01"])
    # 2. Select Problem (only show for Lab 06 or others with multiple problems)
    problem_id = "none"
    if lab_id == "lab06" or lab_id == "lab07":  # Assuming lab07 also has multiple problems
        problem_id = st.selectbox("Select Problem", ["p1", "p2", "p3", "p4"])
    else:
        # For older labs that don't have sub-problems
        problem_id = "none"
    # Track lab/problem selection and reset uploader key when selection changes
    current_selection = f"{lab_id}_{problem_id}"
    if st.session_state.get("last_selection") != current_selection:
        st.session_state["last_selection"] = current_selection
        st.session_state["uploader_key"] = st.session_state.get("uploader_key", 0) + 1

    # File uploader for multiple .java files (key forces reset when lab/problem changes)
    uploaded_files = st.file_uploader(
        """
        YOU MUST UPLOAD ALL REQUIRED .JAVA FILES FOR YOUR LAB PROBLEM.
        YOU MUST ALSO UPLOAD YOUR FINAL SOLUTION ON MOODLE TO GET FULL CREDIT.
        Upload your .java files of the Campus Fleet Management System
        """,
        type=["java"],
        accept_multiple_files=True,
        help="For labs with multiple classes, upload all required .java files",
        key=f"file_uploader_{st.session_state.get('uploader_key', 0)}"
    )
    #######################################################################################
    if st.button("Submit", type="primary"):
        if not student_id:
            st.error("Please enter your Student ID")
        elif not uploaded_files:
            st.error("Please upload at least one .java file")
        else:
            # Combine all files with FILE markers
            code_parts = []
            for uploaded_file in uploaded_files:
                file_content = uploaded_file.read().decode("utf-8")
                code_parts.append(f"// FILE: {uploaded_file.name}\n{file_content}")
          
            combined_code = "\n\n".join(code_parts)
          
            # Send to backend
            with st.spinner("Grading your submission..."):
                try:
                    # Combine them for the backend: "lab06_p1" or just "lab05"
                    final_lab_id = f"{lab_id}_{problem_id}" if problem_id != "none" else lab_id
                    payload = {
                        "student_id": student_id,
                        "lab_id": final_lab_id,
                        "code": combined_code
                    }
                    resp = requests.post(f"{API_URL}/grade", json=payload, timeout=30)
                  
                    if resp.status_code == 200:
                        result = resp.json()
                        st.success(f"✅ Graded! Score: **{result['score']}/{result['max_score']}**")
                        st.text_area("Feedback", result["feedback"], height=400)
                    else:
                        st.error(f"Error {resp.status_code}: {resp.json().get('detail', 'Unknown error')}")
                except Exception as e:
                    st.error(f"Submission failed: {e}")


# ========== VIEW MY GRADES PAGE ==========
elif page == "View My Grades":
    st.header("My Submissions")
  
    student_id = st.text_input("Enter your Student ID", placeholder="e.g., s001")
  
    if st.button("Load My Grades"):
        if not student_id:
            st.error("Please enter your Student ID")
        else:
            try:
                resp = requests.get(f"{API_URL}/student/{student_id}/submissions")
                if resp.status_code == 200:
                    data = resp.json()
                    if data["submissions"]:
                        df = pd.DataFrame(data["submissions"])
                        st.dataframe(df, use_container_width=True)
                    else:
                        st.info("No submissions yet.")
                else:
                    st.error(f"Error: {resp.json().get('detail', 'Unknown error')}")
            except Exception as e:
                st.error(f"Failed to load grades: {e}")

# ========== ADMIN DASHBOARD PAGE ==========
elif page == "Admin Dashboard":
    st.header("🔒 Admin Dashboard")
  
    # Initialize session state for login
    if "admin_logged_in" not in st.session_state:
        st.session_state.admin_logged_in = False
        st.session_state.admin_username = ""
        st.session_state.admin_password = ""
  
    # Login form
    if not st.session_state.admin_logged_in:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
      
        if st.button("Login"):
            try:
                resp = requests.get(
                    f"{API_URL}/admin/all_submissions",
                    auth=(username, password)
                )
                if resp.status_code == 200:
                    st.session_state.admin_logged_in = True
                    st.session_state.admin_username = username
                    st.session_state.admin_password = password
                    st.rerun()
                else:
                    st.error("❌ Invalid credentials")
            except Exception as e:
                st.error(f"Login failed: {e}")
  
    # Show dashboard if logged in
    else:
        col1, col2 = st.columns([6, 1])
        with col1:
            st.success(f"✅ Logged in as {st.session_state.admin_username}")
        with col2:
            if st.button("Logout"):
                st.session_state.admin_logged_in = False
                st.rerun()
      
        try:
            # Fetch all submissions
            resp = requests.get(
                f"{API_URL}/admin/all_submissions",
                auth=(st.session_state.admin_username, st.session_state.admin_password)
            )
          
            if resp.status_code == 200:
                data = resp.json()
                st.info(f"Total submissions: {data['total']}")
              
                if data["submissions"]:
                    df = pd.DataFrame(data["submissions"])
                    st.dataframe(df, use_container_width=True)
                  
                    # Fetch CSV for download
                    csv_resp = requests.get(
                        f"{API_URL}/admin/export_csv",
                        auth=(st.session_state.admin_username, st.session_state.admin_password)
                    )
                  
                    if csv_resp.status_code == 200:
                        csv_data = csv_resp.json()["csv"]
                        st.download_button(
                            label="📥 Download CSV with Feedback",
                            data=csv_data,
                            file_name="grades.csv",
                            mime="text/csv",
                            type="primary"
                        )
                else:
                    st.info("No submissions yet.")
            else:
                st.error("Session expired. Please login again.")
                st.session_state.admin_logged_in = False
                st.rerun()
              
        except Exception as e:
            st.error(f"Error loading dashboard: {e}")
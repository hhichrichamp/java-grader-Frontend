import streamlit as st
import requests
import pandas as pd

# Backend API URL (replace with your Fly.io URL after deployment)
API_URL = "https://java-grader-backend.fly.dev"  # Update this!

st.set_page_config(page_title="Prof. Haikel Hichri Java Lab", page_icon="☕", layout="wide")

# Title
st.title("☕ Prof. Haikel Hichri Java Lab")
st.markdown("**OOP with Java - Lab Submission & Grading System**")
st.markdown("---")

# Sidebar navigation
page = st.sidebar.radio("Navigation", ["Submit Lab", "View My Grades", "Admin Dashboard"])

# ============================================
# PAGE 1: Submit Lab
# ============================================
if page == "Submit Lab":
    st.header("📝 Submit Your Lab")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        student_id = st.text_input("Student ID", placeholder="e.g., s001")
        
        # Auto-lookup student name
        student_name = ""
        if student_id:
            try:
                resp = requests.post(f"{API_URL}/lookup_student", json={"student_id": student_id}, timeout=5)
                if resp.status_code == 200:
                    data = resp.json()
                    student_name = data.get("name", "")
                    st.success(f"✅ Welcome, **{student_name}**!")
                else:
                    st.error("❌ Student ID not found. Please check your ID.")
            except Exception as e:
                st.warning(f"⚠️ Could not verify student ID: {e}")
        
        lab_id = st.selectbox("Select Lab", [f"lab{i:02d}" for i in range(1, 16)])
    
    with col2:
        st.markdown("### Paste your Java code below:")
        code = st.text_area(
            "Java Code", 
            height=400, 
            placeholder="public class Lab01 {\n    // Your code here\n}",
            help="Paste all your Java code here (all classes in one box)"
        )
    
    if st.button("🚀 Submit for Grading", type="primary"):
        if not student_id or not code.strip():
            st.error("⚠️ Please provide your Student ID and code.")
        elif not student_name:
            st.error("⚠️ Invalid Student ID. You must be registered in the class.")
        else:
            with st.spinner("⏳ Compiling and grading your code..."):
                try:
                    payload = {
                        "student_id": student_id,
                        "lab_id": lab_id,
                        "code": code
                    }
                    resp = requests.post(f"{API_URL}/grade", json=payload, timeout=30)
                    
                    if resp.status_code == 200:
                        result = resp.json()
                        score = result.get("score", 0)
                        max_score = result.get("max_score", 20)
                        feedback = result.get("feedback", "")
                        
                        # Display score
                        st.success(f"### 🎯 Your Score: **{score} / {max_score}**")
                        
                        # Display feedback
                        st.markdown("### 📋 Detailed Feedback:")
                        st.code(feedback, language="text")
                        
                        if score == max_score:
                            st.balloons()
                            st.success("🎉 Perfect score! Well done!")
                        elif score > 0:
                            st.info("💡 Review the failed test cases and try again!")
                        else:
                            st.warning("⚠️ No points earned. Check the feedback and fix your code.")
                    
                    elif resp.status_code == 403:
                        st.error("🚫 Access denied. Your Student ID is not authorized.")
                    else:
                        st.error(f"❌ Error {resp.status_code}: {resp.text}")
                
                except requests.exceptions.Timeout:
                    st.error("⏱️ Request timed out. The server may be busy. Please try again.")
                except Exception as e:
                    st.error(f"❌ Connection error: {e}")

# ============================================
# PAGE 2: View My Grades
# ============================================
elif page == "View My Grades":
    st.header("📊 View My Submissions & Grades")
    
    student_id = st.text_input("Enter Your Student ID", placeholder="e.g., s001")
    
    if st.button("🔍 Load My Grades"):
        if not student_id:
            st.error("⚠️ Please enter your Student ID.")
        else:
            try:
                resp = requests.get(f"{API_URL}/student/{student_id}/submissions", timeout=10)
                
                if resp.status_code == 200:
                    data = resp.json()
                    submissions = data.get("submissions", [])
                    
                    if not submissions:
                        st.info("📭 No submissions found for this student.")
                    else:
                        st.success(f"✅ Found {len(submissions)} submission(s)")
                        
                        for sub in submissions:
                            with st.expander(f"**{sub['lab_id'].upper()}** - Score: {sub['score']}/{sub['max_score']} - {sub['timestamp'][:10]}"):
                                st.markdown(f"**Student:** {sub['student_name']}")
                                st.markdown(f"**Score:** {sub['score']} / {sub['max_score']}")
                                st.markdown(f"**Submitted:** {sub['timestamp']}")
                                st.markdown("**Feedback:**")
                                st.code(sub['feedback'], language="text")
                
                elif resp.status_code == 403:
                    st.error("🚫 Student ID not authorized.")
                else:
                    st.error(f"❌ Error {resp.status_code}: {resp.text}")
            
            except Exception as e:
                st.error(f"❌ Connection error: {e}")

# ============================================
# PAGE 3: Admin Dashboard
# ============================================
elif page == "Admin Dashboard":
    st.header("🔐 Admin Dashboard")
    
    st.markdown("**Login required to view all submissions**")
    
    col1, col2 = st.columns(2)
    with col1:
        admin_user = st.text_input("Username", type="default")
    with col2:
        admin_pass = st.text_input("Password", type="password")
    
    if st.button("🔓 Login & View All Grades"):
        if not admin_user or not admin_pass:
            st.error("⚠️ Please enter both username and password.")
        else:
            try:
                resp = requests.get(
                    f"{API_URL}/admin/all_submissions",
                    auth=(admin_user, admin_pass),
                    timeout=10
                )
                
                if resp.status_code == 200:
                    data = resp.json()
                    submissions = data.get("submissions", [])
                    
                    st.success(f"✅ Loaded {data.get('total', 0)} submission(s)")
                    
                    if submissions:
                        df = pd.DataFrame(submissions)
                        st.dataframe(df, use_container_width=True)
                        
                        # Export CSV button
                        st.markdown("---")
                        if st.button("📥 Export as CSV"):
                            csv_resp = requests.get(
                                f"{API_URL}/admin/export_csv",
                                auth=(admin_user, admin_pass),
                                timeout=10
                            )
                            if csv_resp.status_code == 200:
                                csv_data = csv_resp.json().get("csv", "")
                                st.download_button(
                                    label="⬇️ Download CSV",
                                    data=csv_data,
                                    file_name="grades_export.csv",
                                    mime="text/csv"
                                )
                    else:
                        st.info("📭 No submissions yet.")
                
                elif resp.status_code == 401:
                    st.error("🚫 Invalid username or password.")
                else:
                    st.error(f"❌ Error {resp.status_code}: {resp.text}")
            
            except Exception as e:
                st.error(f"❌ Connection error: {e}")

# Footer
st.markdown("---")
st.markdown("*Developed for OOP with Java Course | Prof. Haikel Hichri*")

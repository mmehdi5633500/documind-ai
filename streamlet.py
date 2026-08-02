import streamlit as st
import requests

# ================================
# CONFIG
# ================================

API_URL = "https://documind-ai-production-35e0.up.railway.app"

st.set_page_config(page_title="DocuMind AI", page_icon="🧠", layout="wide")

# ================================
# SESSION STATE — Login info yaad rakhne ke liye
# ================================

if "token" not in st.session_state:
    st.session_state.token = None

if "messages" not in st.session_state:
    st.session_state.messages = []


# ================================
# SIDEBAR — Login/Signup
# ================================

st.sidebar.title("🧠 DocuMind AI")

if st.session_state.token is None:
    st.sidebar.subheader("Login")

    tab1, tab2 = st.sidebar.tabs(["Login", "Signup"])

    with tab1:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_pass")

        if st.button("Login"):
            response = requests.post(
                f"{API_URL}/auth/login", data={"username": email, "password": password}
            )
            if response.status_code == 200:
                st.session_state.token = response.json()["access_token"]
                st.rerun()
            else:
                st.error("Invalid email or password")

    with tab2:
        name = st.text_input("Name", key="signup_name")
        signup_email = st.text_input("Email", key="signup_email")
        signup_password = st.text_input("Password", type="password", key="signup_pass")

        if st.button("Signup"):
            response = requests.post(
                f"{API_URL}/auth/signup",
                json={"name": name, "email": signup_email, "password": signup_password},
            )
            if response.status_code == 201:
                st.success("Account created! Please login.")
            else:
                st.error("Signup failed")

else:
    st.sidebar.success("Logged in ✅")
    if st.sidebar.button("Logout"):
        st.session_state.token = None
        st.session_state.messages = []
        st.rerun()


# ================================
# MAIN AREA — Sirf Logged In Users Ke Liye
# ================================

if st.session_state.token:

    headers = {"Authorization": f"Bearer {st.session_state.token}"}

    st.title("🧠 DocuMind AI")
    st.write("Chat with your documents using AI")

    # ---------- Document Upload ----------
    st.subheader("📄 Upload Document")

    uploaded_file = st.file_uploader("Choose a file", type=["pdf", "txt"])

    if uploaded_file is not None:
        if st.button("Upload"):
            files = {"file": (uploaded_file.name, uploaded_file, "text/plain")}
            response = requests.post(
                f"{API_URL}/documents/upload", headers=headers, files=files
            )
            if response.status_code == 201:
                doc_id = response.json()["id"]
                st.success(f"Uploaded! Document ID: {doc_id}")

                # Auto process karo
                process_response = requests.post(
                    f"{API_URL}/chat/process/{doc_id}", headers=headers
                )
                if process_response.status_code == 200:
                    st.success("Document processed! Ready to chat.")
            else:
                st.error("Upload failed")

    # ---------- Get Documents List ----------
    st.subheader("📚 Your Documents")

    docs_response = requests.get(f"{API_URL}/documents/", headers=headers)

    if docs_response.status_code == 200:
        documents = docs_response.json()

        if documents:
            doc_options = {
                f"{doc['title']} (ID: {doc['id']})": doc["id"] for doc in documents
            }
            selected_doc_label = st.selectbox(
                "Select a document to chat with", list(doc_options.keys())
            )
            selected_doc_id = doc_options[selected_doc_label]

            # ---------- Chat Interface ----------
            st.subheader("💬 Chat")

            # Purani messages dikhao
            for msg in st.session_state.messages:
                with st.chat_message(msg["role"]):
                    st.write(msg["content"])

            # Naya sawaal
            question = st.chat_input("Ask something about the document...")

            if question:
                st.session_state.messages.append({"role": "user", "content": question})
                with st.chat_message("user"):
                    st.write(question)

                with st.spinner("Thinking..."):
                    chat_response = requests.post(
                        f"{API_URL}/chat/ask",
                        headers=headers,
                        json={"document_id": selected_doc_id, "message": question},
                    )

                if chat_response.status_code == 200:
                    answer = chat_response.json()["content"]
                    st.session_state.messages.append(
                        {"role": "assistant", "content": answer}
                    )
                    with st.chat_message("assistant"):
                        st.write(answer)
                else:
                    st.error("Failed to get response")
        else:
            st.info("No documents yet. Upload one above!")

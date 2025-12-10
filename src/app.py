import uuid  # <--- Thêm thư viện tạo ID ngẫu nhiên

import streamlit as st

from main import app

st.set_page_config(page_title="AI Researcher Agent", page_icon="🕵️")
st.title(" AI Researcher Agent (Có bộ nhớ)")

# === QUẢN LÝ SESSION (PHIÊN LÀM VIỆC) ===
# Tạo một thread_id duy nhất cho phiên chat này nếu chưa có
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())
    st.session_state.messages = []  # Lưu lịch sử chat hiển thị lên web

thread_id = st.session_state.thread_id
st.sidebar.write(f"ID Phiên: `{thread_id}`")  # Hiển thị ID để debug chơi

# Sidebar nhập liệu
with st.sidebar:
    st.header("Cấu hình")
    # Nút xóa bộ nhớ (Reset ID mới)
    if st.button("🗑️ Xóa bộ nhớ / Chat mới"):
        st.session_state.thread_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.rerun()

# === GIAO DIỆN CHAT ===
# Hiển thị các tin nhắn cũ
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Ô nhập liệu chat (Thay cho cái form cũ)
if prompt := st.chat_input("Nhập chủ đề nghiên cứu (VD: AI Agent là gì?)..."):
    # 1. Hiện câu hỏi người dùng
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Cấu hình chạy Agent với Thread ID
    config = {"configurable": {"thread_id": thread_id}}

    # 3. Chạy Agent
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        # Biến inputs bây giờ chỉ cần update task mới
        inputs = {"task": prompt, "count": 0}

        # Thử chạy và bắt lỗi

        try:
            # Truyền thêm config vào app.stream
            for output in app.stream(inputs, config=config):  # type: ignore
                for key, value in output.items():
                    if key == "search":
                        msg = f"🔎 *Đang tìm kiếm lần {value.get('count')}...*"
                        message_placeholder.markdown(msg)
                    elif key == "critique":
                        decision = value.get("draft", "")
                        if "NOTFULL" in decision:
                            message_placeholder.markdown(
                                "🤔 *Thông tin chưa đủ, tìm tiếp...*"
                            )
                    elif key == "write":
                        full_response = value.get("draft", "")
                        # Lưu kết quả vào biến tạm để hiển thị sau cùng

            # Hiển thị kết quả cuối cùng
            message_placeholder.markdown(full_response)

            # Lưu vào lịch sử chat của Streamlit
            st.session_state.messages.append(
                {"role": "assistant", "content": full_response}
            )

        except Exception as e:
            st.error(f"Lỗi: {e}")

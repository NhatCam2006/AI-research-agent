import streamlit as st

# Đảm bảo import đúng biến 'app' từ main.py
from main import app

st.set_page_config(page_title="AI Researcher Agent", page_icon="🕵️")

st.title("🕵️ AI Researcher Agent")

# Sidebar
with st.sidebar:
    st.header("Cấu hình")
    topic = st.text_input("Chủ đề:", "AI Agent năm 2025")
    # Dùng form để tránh reload lung tung
    with st.form(key="my_form"):
        submit_button = st.form_submit_button(label="🚀 Bắt đầu nghiên cứu")

# Logic chính
if submit_button and topic:
    st.info(f"Đang bắt đầu nghiên cứu về: {topic}...")

    # Tạo một khung để chứa nội dung log
    log_container = st.container()

    inputs = {"task": topic}
    final_result = ""

    try:
        # Chạy vòng lặp
        for output in app.stream(inputs):  # type: ignore
            for key, value in output.items():
                # In ra log trực tiếp để thấy nó chạy
                with log_container:
                    if key == "search":
                        # Lấy số lần count, nếu không có thì mặc định là 1
                        count = value.get("count", 1)
                        st.markdown(f"🔎 **Researcher:** Đang tìm kiếm lần {count}...")

                    elif key == "critique":
                        decision = value.get("draft", "")
                        if "NOTFULL" in decision:
                            st.warning(
                                f"🤔 **Reviewer:** Thấy thiếu thông tin ({decision})..."
                            )
                        else:
                            st.success("✅ **Reviewer:** Duyệt! Đủ thông tin.")
                            st.markdown("✍️ **Writer:** Đang viết bài tổng hợp...")

                    elif key == "write":
                        final_result = value.get("draft", "")

        # Hiển thị kết quả cuối cùng
        if final_result:
            st.divider()
            st.subheader("📝 Báo cáo kết quả")
            st.markdown(final_result)

            st.download_button(
                label="📥 Tải báo cáo", data=final_result, file_name="baocao.md"
            )
        else:
            st.error("Không nhận được kết quả cuối cùng.")

    except Exception as e:
        # In lỗi ra màn hình để biết đường sửa
        st.error(f"Lỗi chi tiết: {e}")

# 🕵️ AI Researcher Agent (LangGraph + Gemini)

Một AI Agent thông minh có khả năng tự động nghiên cứu, đánh giá thông tin và tổng hợp báo cáo. Sử dụng kiến trúc **Vòng lặp (Human-in-the-loop workflow)** thay vì chuỗi tuyến tính.

## 🚀 Tính năng
- **Tự động tìm kiếm:** Sử dụng Tavily API để lấy dữ liệu thực tế.
- **Cơ chế Phê bình (Self-Reflection):** Tự đánh giá xem thông tin đã đủ chưa.
- **Vòng lặp thông minh:** Nếu thiếu thông tin, tự động quay lại tìm kiếm tiếp.
- **LLM Power:** Sử dụng Google Gemini Flash cho tốc độ xử lý nhanh.

## 🛠️ Tech Stack
![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)
![LangGraph](https://img.shields.io/badge/LangGraph-Agent-orange)
![Gemini](https://img.shields.io/badge/Google-Gemini-4285F4?logo=google&logoColor=white)

## ⚙️ Cài đặt
1. Clone repo
2. Cài đặt thư viện: `pip install -r requirements.txt`
3. Tạo file `.env` và điền API Key.
4. Chạy: `python main.py`
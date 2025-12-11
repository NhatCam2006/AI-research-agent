from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from main import app as graph_app  # Import cái graph của bạn


# 1. Định nghĩa khuôn mẫu dữ liệu đầu vào (Schema)
# Đây là cách làm chuẩn của các dự án lớn: Khai báo rõ input gồm những gì
class ChatRequest(BaseModel):
    messages: str
    thread_id: str  # Bắt buộc người dùng phải gửi thread_id


# 2. Khởi tạo Server
app = FastAPI(title="Pro AI Agent API")


# 3. Tự viết API Endpoint (Thay vì dùng add_routes)
@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """
    API này nhận messages và thread_id, sau đó gọi LangGraph thủ công.
    """
    print(
        f"📥 Nhận yêu cầu: Messages='{request.messages}' | ThreadID='{request.thread_id}'"
    )

    try:
        # Tự tay cấu hình config (Không sợ LangServe làm mất nữa)
        config = {"configurable": {"thread_id": request.thread_id}}

        # Tự tay gọi Graph
        # input: chỉ lấy messages từ request
        inputs = {"messages": request.messages}

        # Gọi hàm ainvoke (bất đồng bộ)
        result = await graph_app.ainvoke(inputs, config=config)  # type: ignore

        # Trả về kết quả sạch đẹp
        return {
            "status": "success",
            "draft": result.get("draft"),
            "full_state": result,  # Trả về cả cục nếu muốn debug
        }

    except Exception as e:
        print(f"❌ LỖI: {str(e)}")
        import traceback

        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=8000)

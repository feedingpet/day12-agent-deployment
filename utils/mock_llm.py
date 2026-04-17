"""
Mock LLM — đã được nâng cấp để gọi API ModernBERT.
"""
import time
import random
import os
import requests

MOCK_RESPONSES = {
    "default": [
        "Đây là câu trả lời từ AI agent (mock). Trong production, đây sẽ là response từ OpenAI/Anthropic.",
        "Agent đang hoạt động tốt! (mock response) Hỏi thêm câu hỏi đi nhé.",
        "Tôi là AI agent được deploy lên cloud. Câu hỏi của bạn đã được nhận.",
    ],
    "docker": ["Container là cách đóng gói app để chạy ở mọi nơi. Build once, run anywhere!"],
    "deploy": ["Deployment là quá trình đưa code từ máy bạn lên server để người khác dùng được."],
    "health": ["Agent đang hoạt động bình thường. All systems operational."],
}

def ask(question: str, delay: float = 0.1) -> str:
    """
    Gọi HuggingFace Inference API tới model ModernBERT (answerdotai/ModernBERT-base),
    hoặc fallback về mock response nếu không cấu hình HF_TOKEN.
    """
    hf_token = os.getenv("HF_API_KEY") or os.getenv("HF_TOKEN")
    if hf_token:
        # ModernBERT thường dùng cho Masked Language Modeling hoặc Feature Extraction.
        # Nhưng để demo trên API inference, nếu chỉ gửi text thường có thể gặp lỗi nếu gọi qua endpoints Mask.
        # Ở đây ta sẽ thử gửi query để "fill-mask"
        API_URL = "https://api-inference.huggingface.co/models/answerdotai/ModernBERT-base"
        headers = {"Authorization": f"Bearer {hf_token}"}
        
        # Đảm bảo có [MASK] để ModernBERT dự đoán kết quả
        query = question
        if "[MASK]" not in query:
            query += " [MASK]"
            
        payload = {"inputs": query}
        try:
            response = requests.post(API_URL, headers=headers, json=payload, timeout=10)
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0 and 'sequence' in result[0]:
                    predicted_token = result[0].get('token_str', '')
                    return f"ModernBERT API response: {result[0]['sequence']} (Predicted mask: '{predicted_token}')"
                return f"ModernBERT API returned data: {str(result)}"
            else:
                # Nếu API lỗi, log lại status
                return f"ModernBERT API error: HTTP {response.status_code} - {response.text}"
        except Exception as e:
            return f"Lỗi gọi ModernBERT API: {str(e)}"

    # Nếu không có Token HuggingFace, Fallback sử dụng mock
    time.sleep(delay + random.uniform(0, 0.05))  
    question_lower = question.lower()
    for keyword, responses in MOCK_RESPONSES.items():
        if keyword in question_lower:
            return random.choice(responses)
    return random.choice(MOCK_RESPONSES["default"])

def ask_stream(question: str):
    response = ask(question)
    words = response.split()
    for word in words:
        time.sleep(0.05)
        yield word + " "

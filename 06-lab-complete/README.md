# Production AI Agent - ModernBERT Integration

Dự án AI Agent hoàn chỉnh cho môi trường Production (đáp ứng tiêu chuẩn Lab 06 Complete - Day 12). Ứng dụng này đã được đóng gói sẵn với Docker theo chuẩn **Multi-stage build**, áp dụng các best practices như bảo mật API Key, Rate Limiting, Cost Guard, Stateless Session (Redis) và cấu hình ứng dụng dễ dàng thông qua File Môi trường `(12-Factor App)`. Đặc biệt, mô hình đã được thay đổi linh hoạt sang gọi inference Model **answerdotai/ModernBERT-base** qua HuggingFace API.

---

## 📁 Cấu Trúc Dự Án (Full Source Code)

Dự án tuân thủ cấu trúc quy chuẩn, chia nhỏ các thành phần (modularity) như sau:

```text
06-lab-complete/
├── app/
│   ├── main.py              # Main application (Entry point)
│   ├── config.py            # Configuration variables
│   ├── auth.py              # Authentication security check
│   ├── rate_limiter.py      # Rate limiting defense (Sliding Window logic)
│   └── cost_guard.py        # Cost protection limiting logic
├── utils/
│   └── mock_llm.py          # LLM Service (Gọi Inference ModernBERT API)
├── Dockerfile               # Multi-stage build cho container nhỏ nhẹ
├── docker-compose.yml       # Full stack bao gồm Agent + Redis DB + LB
├── requirements.txt         # Dependencies (FastAPI, Redis, Requests, PyJWT...)
├── .env.example             # Environment template chuẩn
├── .dockerignore            # Docker ignore file
├── railway.toml             # Config khi Deploy lên nền tảng Railway
├── render.yaml              # Config khi Deploy lên nền tảng Render
└── README.md                # Tệp này (Setup instructions)
```

---

## 🛠 Yêu Cầu Cài Đặt (Prerequisites)
- `Python 3.11+`
- `Docker` & `Docker Compose`
- (Tuỳ chọn) Một API token miễn phí từ [Hugging Face](https://huggingface.co/settings/tokens) để test ModernBERT model.

---

## 🚀 Setup & Launch (Hướng dẫn chạy App)

### 1. Chuẩn bị File môi trường `.env.local`
Sao chép `.env.example` thành file riêng của bạn:
```bash
cp .env.example .env.local
```

Sau đó mở `.env.local` lên để điền các key quan trọng:
```env
# (QUAN TRỌNG) Token này lấy từ Hugging Face
HF_TOKEN=hf_xxxx_dia_chi_token_cua_ban_xyz

# (QUAN TRỌNG) Mật khẩu tự đặt để bảo vệ API chống gọi lén
AGENT_API_KEY=my-super-secret-key-123
```

### 2. Khởi chạy bằng Docker Compose
Câu lệnh dưới đây sẽ build container siêu nhẹ và khởi chạy app kèm theo Redis DB Cache:
```bash
docker compose up --build -d
```
_Note: Web Server của bạn hiện tại sẽ Public ra Port `8000`. Cùng với đó Redis sẽ trực ở Port `6379`._

### 3. Test Liveness & Readiness hệ thống
Kiểm tra xem hệ thống đã sẵn sàng chưa (Health Check 200 OK):
```bash
curl http://localhost:8000/health
curl http://localhost:8000/ready
```

---

## 💻 Test API ModernBERT Inference (Cách gửi đi request thật)

Vì chúng ta sử dụng Text Classifier/Mask Builder nên model là `ModernBERT-base`.
Để thử nghiệm, bạn gửi lên câu hỏi và chừa lại thẻ `<Mask>`, AI Agent sẽ tự động điền thẻ đó giùm bạn.

```bash
# Ở Terminal/Git Bash:
curl -X POST http://localhost:8000/ask \
  -H "X-API-Key: my-super-secret-key-123" \
  -H "Content-Type: application/json" \
  -d '{"question": "Hi ModernBERT, The capital city of Vietnam is [MASK]."}'
```

```powershell
# Ở PowerShell (Windows):
Invoke-RestMethod -Uri "http://localhost:8000/ask" `
  -Method Post `
  -Headers @{
    "X-API-Key" = "my-super-secret-key-123"
    "Content-Type" = "application/json"
  } `
  -Body '{"question": "Thủ đô của Việt Nam là [MASK]."}'
```

🎉 **Kết Quả Mong Chờ:**
```json
{
  "question": "Thủ đô của Việt Nam là [MASK].",
  "answer": "ModernBERT API response: Thủ đô của Việt Nam là Hà Nội. (Predicted mask: 'Hà Nội')",
  "model": "answerdotai/ModernBERT-base",
  "timestamp": "2026-04-17T15:20:00Z"
}
```

---

## 🌐 Mẹo Deploy lên Cloud Dễ Dàng

### Option 1: Railway (Khuyên dùng)
```bash
npm i -g @railway/cli
railway login
railway init
railway variables set HF_TOKEN=hf_xxxxxx...
railway variables set AGENT_API_KEY=super-secret-key
railway up
```

### Option 2: Render
1. Push toàn bộ source code này lên Github
2. Truy cập web Render Dashboard chọn `New` > `Blueprint`
3. Lựa chọn Repository git
4. Cấu hình biến môi trường (`HF_TOKEN` và `AGENT_API_KEY`) trên website
5. Nhấn tạo. Done!

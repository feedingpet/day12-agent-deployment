#  Delivery Checklist — Day 12 Lab Submission

> **Student Name:** Nguyễn Ngọc Cường  
> **Student ID:** 2A202600186 
> **Date:** 17/4/2026

---

##  Submission Requirements

Submit a **GitHub repository** containing:

### 1. Mission Answers (40 points)

Create a file `MISSION_ANSWERS.md` with your answers to all exercises:

```markdown
# Day 12 Lab - Mission Answers

## Part 1: Localhost vs Production

### Exercise 1.1: Anti-patterns found
1. API key hardcode trong code
2. Không có health check endpoint
3. Debug mode bật cứng
4. Không xử lý SIGTERM gracefully
5. Config không đến từ environment

### Exercise 1.3: Comparison table
| Feature | Develop | Production | Why Important? |
|---------|---------|------------|----------------|
| Config | Hardcode trong code | Đọc từ env vars |Dễ dàng thay đổi thông số (DB URL, Timeout) mà không cần build lại code.|
| Secrets | `api_key = "sk-abc123"` | `os.getenv("OPENAI_API_KEY")` |Tránh lộ khóa bảo mật trên GitHub và tuân thủ nguyên tắc an toàn dữ liệu.|
| Port | Cố định `8000` | Từ `PORT` env var |Các dịch vụ Cloud (Railway, Render) cấp port ngẫu nhiên; fix cứng sẽ khiến App không chạy được.|
| Health check | Không có | `GET /health` |Giúp hệ thống quản trị (Docker, K8s) biết ứng dụng còn sống hay đã "treo" để tự động khởi động lại.|
| Shutdown | Tắt đột ngột | Graceful — hoàn thành request hiện tại |Tránh mất mát dữ liệu hoặc gây lỗi cho khách hàng khi đang thực hiện dở một tác vụ (như thanh toán).|
| Logging | `print()` | Structured JSON logging |Giúp các công cụ quản lý log (ELK, Datadog) dễ dàng phân tích, tìm kiếm và cảnh báo khi có lỗi.|
## Part 2: Docker

### Exercise 2.1: Dockerfile questions
1. Base image: Nó chứa hệ điều hành tối giản (như Alpine, Ubuntu) hoặc một môi trường chạy mã nguồn đã cài sẵn (như Python, Node.js, Java)
2. Working directory: Thiết lập thư mục mặc định cho bất kỳ lệnh nào tiếp theo (như RUN, CMD, ENTRYPOINT, COPY).
3. Tại sao COPY requirements.txt trước?: tận dụng Cache, giúp Build Image nhanh hơn gấp nhiều lần
4. CMD vs ENTRYPOINT khác nhau thế nào?: CMD là lệnh mặc định (dễ thay thế), ENTRYPOINT là lệnh cố định (thường dùng cho các ứng dụng thực thi trực tiếp).

### Exercise 2.3: Image size comparison
- Develop: 1.66 GB
- Production: 236 MB
- Difference: 98.22%

## Part 3: Cloud Deployment

### Exercise 3.1: Railway deployment
- URL: https://railway.com/project/afe1a4aa-ef3d-4ec7-a7d0-56ea98b9910c
- Screenshot: [Link to screenshot in repo]

## Part 4: API Security

### Exercise 4.1-4.3: Test results
Exercise 4.1:
API key được check ở đâu?: verify_api_key(api_key: str = Security(api_key_header))
Điều gì xảy ra nếu sai key?: verify_api_key(api_key: str = Security(api_key_header))
Làm sao rotate key?: Thay đổi giá trị của biến môi trường AGENT_API_KEY
Exercise 4.2:
{
  "question": "Hôm nay là thứ mấy",
  "answer": "Đây là câu trả lời từ AI agent (mock). Trong production, đây sẽ là response từ OpenAI/Anthropic."
}
Exercise 4.3:
Algorithm nào được dùng? (Token bucket? Sliding window?): Sliding Window
Limit là bao nhiêu requests/minute?: Đối với User thông thường: Giới hạn là 10 requests mỗi phút (tương đương max_requests=10, window_seconds=60). Đối với Admin: Giới hạn cao hơn, là 100 requests mỗi phút (tương đương max_requests=100, window_seconds=60).
Làm sao bypass limit cho admin?: sửa code theo hướng bỏ qua bước kiểm tra đối với Admin
def check_rate_limit(user_id: str, is_admin: bool):
    if is_admin:
        return  # Không làm gì cả, cho đi qua luôn -> Đây là Bypass
    rate_limiter_user.check(user_id)
{
  "detail": {
    "error": "Rate limit exceeded",
    "limit": 10,
    "window_seconds": 60,
    "retry_after_seconds": 59
  }
}
### Exercise 4.4: Cost guard implementation
1. Cấu trúc lưu trữ (Key Design)
month_key = datetime.now().strftime("%Y-%m")
key = f"budget:{user_id}:{month_key}"
Ý nghĩa: Tạo ra một "ngăn chứa" riêng biệt cho từng người dùng theo từng tháng (ví dụ: budget:user123:2026-04).
Lợi ích: Tự động tách biệt dữ liệu giữa các tháng. Khi sang tháng mới, một key mới sẽ được tạo ra và ngân sách của người dùng được tính lại từ đầu (reset).
2. Kiểm tra ngân sách (The Check)
current = float(r.get(key) or 0)
if current + estimated_cost > 10:
    return False
Lấy dữ liệu: Truy xuất số tiền đã chi tiêu hiện tại từ Redis. Nếu chưa có dữ liệu (tháng mới), mặc định là 0.
So sánh: Cộng chi phí dự kiến (estimated_cost) vào tổng cũ. Nếu vượt quá ngưỡng 10 (đơn vị có thể là USD hoặc số lượt request), hàm sẽ trả về False để chặn hành động của người dùng.
3. Cập nhật và Gia hạn (Update & Expiration)
r.incrbyfloat(key, estimated_cost)
r.expire(key, 32 * 24 * 3600)  # 32 days
incrbyfloat: Đây là một lệnh Atomic (nguyên tử) trong Redis. Nó giúp tăng giá trị của key lên một khoảng đúng bằng estimated_cost. Việc dùng lệnh này đảm bảo tính chính xác ngay cả khi có nhiều yêu cầu gửi đến cùng một lúc (tránh lỗi Race Condition).
expire: Thiết lập thời gian sống cho key là 32 ngày. Sau thời gian này, dữ liệu tháng cũ sẽ tự động bị xóa để giải phóng bộ nhớ cho Redis.

## Part 5: Scaling & Reliability

### Exercise 5.1-5.5: Implementation notes
Exercise 5.1 
Giải pháp:

Stateless design — Không lưu state trong memory
Health checks — Platform biết khi nào restart
Graceful shutdown — Hoàn thành requests trước khi tắt
Load balancing — Phân tán traffic

Kết quả output sau khi chạy `python test_stateless.py`:
```text
============================================================
Stateless Scaling Demo
============================================================

Session ID: 5e18a900-a279-4b9c-aa4e-73e5662ae65d

Request 1: [instance-73eb1f]
  Q: What is Docker?
  A: Container là cách đóng gói app để chạy ở mọi nơi. Build once, run anywhere!...

Request 2: [instance-d3a294]
  Q: Why do we need containers?
  A: Đây là câu trả lời từ AI agent (mock). Trong production, đây sẽ là response từ O...

Request 3: [instance-83c7c9]
  Q: What is Kubernetes?
  A: Agent đang hoạt động tốt! (mock response) Hỏi thêm câu hỏi đi nhé....

Request 4: [instance-73eb1f]
  Q: How does load balancing work?
  A: Agent đang hoạt động tốt! (mock response) Hỏi thêm câu hỏi đi nhé....

Request 5: [instance-d3a294]
  Q: What is Redis used for?
  A: Agent đang hoạt động tốt! (mock response) Hỏi thêm câu hỏi đi nhé....

------------------------------------------------------------
Total requests: 5
Instances used: {'instance-73eb1f', 'instance-83c7c9', 'instance-d3a294'}
✅ All requests served despite different instances!

--- Conversation History ---
Total messages: 10
  [user]: What is Docker?...
  [assistant]: Container là cách đóng gói app để chạy ở mọi nơi. Build once...
  [user]: Why do we need containers?...
  [assistant]: Đây là câu trả lời từ AI agent (mock). Trong production, đây...
  [user]: What is Kubernetes?...
  [assistant]: Agent đang hoạt động tốt! (mock response) Hỏi thêm câu hỏi đ...
  [user]: How does load balancing work?...
  [assistant]: Agent đang hoạt động tốt! (mock response) Hỏi thêm câu hỏi đ...
  [user]: What is Redis used for?...
  [assistant]: Agent đang hoạt động tốt! (mock response) Hỏi thêm câu hỏi đ...

✅ Session history preserved across all instances via Redis!
```

---

### 2. Full Source Code - Lab 06 Complete (60 points)

Your final production-ready agent with all files:

```
your-repo/
├── app/
│   ├── main.py              # Main application
│   ├── config.py            # Configuration
│   ├── auth.py              # Authentication
│   ├── rate_limiter.py      # Rate limiting
│   └── cost_guard.py        # Cost protection
├── utils/
│   └── mock_llm.py          # Mock LLM (provided)
├── Dockerfile               # Multi-stage build
├── docker-compose.yml       # Full stack
├── requirements.txt         # Dependencies
├── .env.example             # Environment template
├── .dockerignore            # Docker ignore
├── railway.toml             # Railway config (or render.yaml)
└── README.md                # Setup instructions
```

**Requirements:**
-  All code runs without errors
-  Multi-stage Dockerfile (image < 500 MB)
-  API key authentication
-  Rate limiting (10 req/min)
-  Cost guard ($10/month)
-  Health + readiness checks
-  Graceful shutdown
-  Stateless design (Redis)
-  No hardcoded secrets

---

### 3. Service Domain Link

Create a file `DEPLOYMENT.md` with your deployed service information:

```markdown
# Deployment Information

## Public URL
https://your-agent.railway.app

## Platform
Railway / Render / Cloud Run

## Test Commands

### Health Check
```bash
curl https://your-agent.railway.app/health
# Expected: {"status": "ok"}
```

### API Test (with authentication)
```bash
curl -X POST https://your-agent.railway.app/ask \
  -H "X-API-Key: YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test", "question": "Hello"}'
```

## Environment Variables Set
- PORT
- REDIS_URL
- AGENT_API_KEY
- LOG_LEVEL

## Screenshots
- [Deployment dashboard](screenshots/dashboard.png)
- [Service running](screenshots/running.png)
- [Test results](screenshots/test.png)
```

##  Pre-Submission Checklist

- [ ] Repository is public (or instructor has access)
- [ ] `MISSION_ANSWERS.md` completed with all exercises
- [ ] `DEPLOYMENT.md` has working public URL
- [ ] All source code in `app/` directory
- [ ] `README.md` has clear setup instructions
- [ ] No `.env` file committed (only `.env.example`)
- [ ] No hardcoded secrets in code
- [ ] Public URL is accessible and working
- [ ] Screenshots included in `screenshots/` folder
- [ ] Repository has clear commit history

---

##  Self-Test

Before submitting, verify your deployment:

```bash
# 1. Health check
curl https://your-app.railway.app/health

# 2. Authentication required
curl https://your-app.railway.app/ask
# Should return 401

# 3. With API key works
curl -H "X-API-Key: YOUR_KEY" https://your-app.railway.app/ask \
  -X POST -d '{"user_id":"test","question":"Hello"}'
# Should return 200

# 4. Rate limiting
for i in {1..15}; do 
  curl -H "X-API-Key: YOUR_KEY" https://your-app.railway.app/ask \
    -X POST -d '{"user_id":"test","question":"test"}'; 
done
# Should eventually return 429
```

---

##  Submission

**Submit your GitHub repository URL:**

```
https://github.com/your-username/day12-agent-deployment
```

**Deadline:** 17/4/2026

---

##  Quick Tips

1.  Test your public URL from a different device
2.  Make sure repository is public or instructor has access
3.  Include screenshots of working deployment
4.  Write clear commit messages
5.  Test all commands in DEPLOYMENT.md work
6.  No secrets in code or commit history

---

##  Need Help?

- Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- Review [CODE_LAB.md](CODE_LAB.md)
- Ask in office hours
- Post in discussion forum

---

**Good luck! **

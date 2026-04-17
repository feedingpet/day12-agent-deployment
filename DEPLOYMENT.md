# Deployment Information

## Public URL
https://nguyenngoccuong-day12-agent.railway.app

## Platform
Railway

## Test Commands

### Health Check
```bash
curl https://nguyenngoccuong-day12-agent.railway.app/health
# Expected: {"status": "ok", ...}
```

### API Test (with authentication)
```bash
curl -X POST https://nguyenngoccuong-day12-agent.railway.app/ask \
  -H "X-API-Key: YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"question": "ModernBERT is a great [MASK] for filling masks."}'
```
*(Lưu ý: API dùng HuggingFace Inference qua ModernBERT nên nên có từ khoá `[MASK]` trong câu hỏi để ModernBERT trả về đúng nhất)*

## Environment Variables Set
- `PORT=8000`
- `REDIS_URL=redis://...`
- `AGENT_API_KEY=my-super-secret-key`
- `LOG_LEVEL=INFO`
- `ENVIRONMENT=production`
- `HF_TOKEN=your_hugging_face_token_here` (Để giao tiếp với ModernBERT qua API)

## Screenshots
- [Deployment dashboard](screenshots/dashboard.png)
- [Service running](screenshots/running.png)
- [Test results](screenshots/test.png)

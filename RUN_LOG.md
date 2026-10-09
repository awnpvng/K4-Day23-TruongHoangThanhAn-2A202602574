# Run log

Nhật ký các lần chạy `python research.py "<topic>"` — để biết đang ở đâu, không cần dò lại background output.
Cập nhật thủ công sau mỗi lần chạy xong (thành công hay thất bại). Không phải file nộp bài, chỉ để theo dõi tiến độ.

## Trạng thái hiện tại theo 5 chủ đề

| # | Chủ đề | Trạng thái | Validator |
|---|---|---|---|
| 1 | survey about world model | ✅ Xong, đạt chuẩn | `OK: 12 sources, all citations resolve` |
| 2 | survey about reinforcement learning for LLM reasoning | ✅ Xong, đạt chuẩn | `OK: 14 sources, all citations resolve` |
| 3 | survey about LLM agents and tool use | ⏳ đang chạy | — |
| 4 | survey about video and multimodal generation | ⬜ Chưa chạy | — |
| 5 | survey about efficient inference and small language models | ⬜ Chưa chạy | — |

## Lịch sử các lần chạy

| # | Thời điểm (giờ phiên) | Chủ đề | Model | Kết quả | Ghi chú |
|---|---|---|---|---|---|
| 1 | run 1 | world model | openai/gpt-4o-mini (OpenRouter) | ✅ thành công nhưng lỗi chất lượng | Lead tự viết `# References` giả trong thân báo cáo; 1 URL arxiv sai domain (`arxiv.science`). Validator cũ không bắt được vì chỉ tách theo `## References` đúng nghĩa. |
| 2 | run 2 | world model | openai/gpt-4o-mini (OpenRouter) | ✅ sạch | Sau khi sửa `agents.py` (cấm mọi heading References trong thân, bắt copy URL nguyên văn) và siết `check_citations.py` (bắt heading References giả + `source` không hợp lệ). `OK: 12 sources, all citations resolve`, 3 họ nguồn, `subagent_calls=5`. |
| 3 | run 1 | RL cho LLM reasoning | openai/gpt-4o-mini (OpenRouter) | ✅ thành công nhưng lỗi chất lượng | Nguồn `[8]` có `"source": "alphaXiv"` (không thuộc 4 giá trị hợp lệ `arxiv/hf-daily/hf-search/web`) và trùng bài với `[7]`. |
| 4 | run 2 | RL cho LLM reasoning | openai/gpt-4o-mini (OpenRouter) | ❌ lỗi hạ tầng | `402 This request would exceed your available credits given your current in-flight requests` — do nhiều subagent gọi model song song, vượt in-flight budget của tier miễn phí OpenRouter. Đợi 125s theo `Retry-After` rồi thử lại. |
| 5 | run 3 | RL cho LLM reasoning | openai/gpt-4o-mini (OpenRouter) | ❌ lỗi hạ tầng | `402 requires more credits` — tài khoản OpenRouter hết credit thật sự (không phải rate limit tạm thời). Đổi sang Gemini. |
| 6 | run 4 | RL cho LLM reasoning | google_genai:gemini-2.5-flash | ❌ bị treo ~26 phút, đã kill | Gemini free tier chỉ 15 RPM, nhiều subagent gọi song song liên tục 429 → agent kẹt trong retry nội bộ của SDK, không ra kết quả. Đã `kill` process + xoá container Docker. |
| 7 | run 5 | RL cho LLM reasoning | google_genai:gemini-3.5-flash-lite (key mới, limit 10 RPM) | ⚠️ thành công nhưng lỗi chất lượng, 40.6 phút (2436s) | Thêm trần RPM phía client (`InMemoryRateLimiter`, mặc định 8 RPM, chỉnh qua `LAB_MAX_RPM`) dùng chung cho lead+mọi subagent. Validator `OK: 19 sources`, nhưng `source_families` chỉ còn `["arxiv", "hf-search"]` (2/4) — lead có giao thêm researcher bù nguồn (note `05-arxiv-web-supplement.md`) nhưng KHÔNG thực sự trích dẫn fact từ family đó vào thân báo cáo, nên `finalize_citations.py` âm thầm loại bỏ (chỉ giữ nguồn được cite). Chưa đạt RUBRIC 2.2 (cần >=3 họ nguồn ĐƯỢC CITE, không phải chỉ có mặt trong sources.json). |
| 8 | run 6 | RL cho LLM reasoning | google_genai:gemini-3.5-flash-lite | ✅ sạch, 30.3 phút (1820s) | Sửa `agents.py` bước 5: bắt lead liệt kê sources.json theo family TRƯỚC khi viết thân báo cáo và chủ động lên kế hoạch cite >=3 family ngay từ đầu. Kết quả: `OK: 14 sources`, `subagent_calls=4`, 3 họ nguồn (`hf-daily`, `hf-search`, `web`) — đạt RUBRIC 2.1/2.2. |
| 9 | run 1 | LLM agents and tool use | google_genai:gemini-3.5-flash-lite | ⏳ đang chạy | Chủ đề 3, dùng bản prompt đã sửa ổn định (bắt cite đa dạng nguồn từ đầu). |

## Bước tiếp theo

- [ ] Theo dõi kết quả chủ đề 3 (`survey about LLM agents and tool use`).
- [ ] Chạy chủ đề 4, 5 — luôn kiểm `meta.json["source_families"]` sau mỗi lần chạy (validator không tự kiểm RUBRIC 2.2).
- [ ] Rà soát cả 5 báo cáo + `python self_check.py` cuối cùng.

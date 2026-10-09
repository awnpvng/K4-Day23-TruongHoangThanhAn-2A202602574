# Run log

Nhật ký các lần chạy `python research.py "<topic>"` — để biết đang ở đâu, không cần dò lại background output.
Cập nhật thủ công sau mỗi lần chạy xong (thành công hay thất bại). Không phải file nộp bài, chỉ để theo dõi tiến độ.

## Trạng thái hiện tại theo 5 chủ đề

| # | Chủ đề | Trạng thái | Validator |
|---|---|---|---|
| 1 | survey about world model | ✅ Xong, đạt chuẩn | `OK: 12 sources, all citations resolve` |
| 2 | survey about reinforcement learning for LLM reasoning | ✅ Xong, đạt chuẩn | `OK: 14 sources, all citations resolve` |
| 3 | survey about LLM agents and tool use | ✅ Xong, đạt chuẩn | `OK: 12 sources, all citations resolve` |
| 4 | survey about video and multimodal generation | ✅ Xong, đạt chuẩn | `OK: 11 sources, all citations resolve` |
| 5 | survey about efficient inference and small language models | ✅ Xong, đạt chuẩn | `OK: 12 sources, all citations resolve` |

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
| 9 | run 1 | LLM agents and tool use | google_genai:gemini-3.5-flash-lite | ⚠️ sạch validator, 18.25 phút (1095s), nhưng chỉ 2/4 họ nguồn | `OK: 13 sources`, `subagent_calls=4`, nhưng `source_families: ["hf-search", "web"]` — thiếu arxiv/hf-daily dù prompt đã bắt lên kế hoạch đa dạng nguồn (hành vi nondeterministic của LLM, đúng như GUIDE cảnh báo). **Người dùng quyết định chấp nhận như hiện tại**, không chạy lại, để tiết kiệm thời gian. |
| 10 | run 1 | video and multimodal generation | google_genai:gemini-3.5-flash-lite | ⏸️ Dừng theo yêu cầu người dùng ở phút 15 (2 notes xong), không lỗi | `LAB_MAX_RPM` nâng từ 8 lên **15**. Chưa thấy 429 trước khi dừng. Chưa có file nào trong `reports/`. |
| 11 | run 2 | video and multimodal generation | - | ❌ lỗi hạ tầng, không gọi tới model | `cannot start the sandbox container: ... docker API ...` — Docker Desktop daemon đã tắt (có thể do khởi động lại máy hoặc dừng thủ công). Đã khởi động lại Docker Desktop, daemon sẵn sàng sau ~10s. |
| 12 | run 3 | video and multimodal generation | google_genai:gemini-3.5-flash-lite | ⚠️ "thành công" (exit 0) nhưng báo cáo HỎNG, chỉ 177.5s | `n_sources=12`, 3 họ nguồn (arxiv/hf-search/web) — tốt! Nhưng validator fail: 10 dòng References có URL KHÔNG khớp với `sources.json` theo đúng số thứ tự (ví dụ ref[2] trỏ URL mà sources.json nói là của n=7). `finalize_citations.py` ghi report.md+sources.json ĐỒNG THỜI trong 1 lần chạy nên luôn khớp nhau tại thời điểm đó — suy ra agent đã sửa `sources.json` hoặc phần References bằng tay SAU lần chạy finalizer cuối, làm 2 file lệch pha, nhưng `research.py` cũ không tự kiểm tra lại nên vẫn lưu ra `reports/` dù hỏng. **Đã vá lỗ hổng**: thêm bước gọi `check_citations.check()` ngay trong `save_outputs()` (research.py) — nếu báo cáo tải về không hợp lệ thì KHÔNG ghi gì cả, báo `FAILED` và thoát mã 1, thay vì âm thầm lưu báo cáo hỏng. Đồng thời siết prompt lead: cấm tuyệt đối sửa tay `sources.json`/References sau khi finalizer chạy, bắt buộc validator là lệnh cuối cùng trước khi coi là xong. |
| 13 | run 4 | video and multimodal generation | google_genai:gemini-3.5-flash-lite | ✅ sạch, 147.5s | `OK: 11 sources`, `subagent_calls=4`, 3 họ nguồn (arxiv/hf-search/web) — chốt chặn mới trong `save_outputs()` xác nhận hợp lệ trước khi lưu. |
| 14 | run 1 | efficient inference and small LM | google_genai:gemini-3.5-flash-lite | ✅ sạch, 208s | `OK: 12 sources`, `subagent_calls=4`, 3 họ nguồn (arxiv/hf-search/web). |
| 15 | run 2 | LLM agents and tool use | google_genai:gemini-3.5-flash-lite | ✅ sạch, 164.7s | `OK: 12 sources`, `subagent_calls=4`, 3 họ nguồn (arxiv/hf-search/web) — đạt chuẩn. |

## Rà soát nội dung (sau khi self_check pass)

Đọc toàn bộ 5 báo cáo, phát hiện lỗi chất lượng thật: **chủ đề "world model" và "video and multimodal generation" có TOÀN BỘ bullet trong `## TL;DR` không có citation `[n]` nào** — vi phạm `REPORT_TEMPLATE.md` ("each bullet with a citation [n]"). `check_citations.py` không bắt được vì đây là yêu cầu chất lượng, không phải lỗi tính nhất quán trích dẫn. Báo cáo world model cũng sơ sài hơn 4 báo cáo còn lại (ít số liệu/tên cụ thể).

Đã sửa:
- `agents.py`: bắt buộc mọi bullet TL;DR phải có `[n]`, yêu cầu nội dung cụ thể (tên method/số liệu) thay vì mô tả chung chung.
- `research.py` `save_outputs()`: thêm kiểm tra TL;DR-citation ngay trên host — báo cáo thiếu citation ở TL;DR sẽ bị từ chối lưu (`FAILED`) thay vì lọt qua.

| # | Thời điểm | Chủ đề | Model | Kết quả | Ghi chú |
|---|---|---|---|---|---|
| 16 | run 3 | world model | google_genai:gemini-3.5-flash-lite | ✅ sạch, 211.2s | `OK: 8 sources`, 3 họ nguồn, TL;DR có citation đầy đủ (DreamerV3, DIAMOND, JEPA/LeWAM...) — nội dung cụ thể hơn hẳn bản cũ. |
| 17 | run 1 | video and multimodal generation (lần 2, sau sửa TL;DR) | google_genai:gemini-3.5-flash-lite | ✅ sạch, 172.8s | `OK: 15 sources`, 3 họ nguồn, TL;DR có citation đầy đủ (Sora, Wan2.1, HunyuanVideo, Tora...). |

## 🎉 Trạng thái cuối cùng: `python self_check.py` → READY to submit

Cả 5/5 báo cáo: validator OK, ≥3 họ nguồn thực sự được cite, `subagent_calls≥3`, TL;DR có citation đầy đủ, git/secrets sạch.

## Bước tiếp theo

- [ ] Mở vài citation (URL thật) trong các báo cáo để đối chiếu nội dung — xác suất cao các nguồn arxiv/hf-search là thật (đã kiểm chứng định dạng + nhất quán), nhưng khuyến khích tự verify thêm trước khi nộp vì RUBRIC 4.2 giảng viên sẽ tự kiểm mẫu.
- [ ] Kiểm `git status` trước khi commit, đảm bảo không dính `.env`/khóa.
- [ ] Commit + push lên GitHub public, nộp link repo.

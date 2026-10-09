# Kế hoạch hoàn thiện Deep Research Agent

## Trạng thái

- [x] [read] Đọc `README.md` theo thứ tự được chỉ dẫn, sau đó đối chiếu `GUIDE.md`, `RUBRIC.md`, mẫu báo cáo, danh sách chủ đề và toàn bộ mã nguồn.
- [x] [run] Kiểm tra LLM calling (mock tool-call đơn giản) — đã test cả OpenRouter và Gemini (`google_genai:gemini-2.5-flash`), cả hai trả `tool_calls` đúng.
- [x] [code] Hoàn thiện các TODO dành cho sinh viên (`check_citations.py`, `tools.py`, `agents.py`, `research.py`), giữ nguyên các tệp được cung cấp.
- [x] [run] Kiểm thử công cụ (`python tools.py`) và validator — đều pass.
- [~] [report] Sinh và rà soát đủ năm báo cáo. *(2/5 đạt chuẩn; chủ đề 3 đang chạy trên Gemini — xem `RUN_LOG.md` để biết chi tiết từng lần; chủ đề 4-5 chưa chạy)*
- [ ] [submit] Tự kiểm tra, rà soát bí mật, rồi chuẩn bị repo công khai để nộp.

Checkbox `[ ]` là chưa hoàn tất; đổi thành `[x]` khi công việc tương ứng đã xong.

## Tóm tắt repo

Đây là lab Python 3.11+ xây dựng hệ thống deep research đa tác tử. Người dùng nhập một chủ đề; lead agent lập kế hoạch, giao các câu hỏi con cho researcher chạy song song, tổng hợp ghi chú và tạo báo cáo tiếng Anh có trích dẫn. Các công cụ lấy nguồn chạy trên host; ghi chú, xử lý báo cáo và kiểm tra trích dẫn chạy trong sandbox Daytona hoặc Docker.

Luồng chính:

1. `research.py` đọc cấu hình model qua `model.py`, mở sandbox qua `sandbox.py` và tải validator cùng citation finalizer vào sandbox.
2. Lead agent trong `agents.py` lập kế hoạch, giao việc và dùng các source tools từ `tools.py`.
3. Researcher ghi ghi chú; lead tổng hợp `sources.json` và phần thân báo cáo theo `REPORT_TEMPLATE.md`.
4. `finalize_citations.py` tạo lại References và đánh số trích dẫn; `check_citations.py` xác thực báo cáo ngay trong sandbox.
5. `research.py` chỉ lưu các đầu ra hợp lệ vào `reports/`, kèm metadata.

| Khu vực | Vai trò và hiện trạng |
|---|---|
| `README.md`, `GUIDE.md` | Mục tiêu, cách cài/chạy và thứ tự triển khai chi tiết; `TODO n` trong mã khớp với các phần của GUIDE. |
| `RUBRIC.md`, `REPORT_TEMPLATE.md` | Tiêu chí chấm 100 điểm và cấu trúc/trích dẫn bắt buộc của mỗi báo cáo. |
| `topics.md` | Năm chủ đề bắt buộc: world model; RL cho LLM reasoning; LLM agents/tool use; video/multimodal generation; efficient inference/small language models. |
| `check_citations.py` | **Đã triển khai** `check()` (đủ 6 quy tắc GUIDE, hỗ trợ `[1, 2]`/`[1-3]`); test tay cho ca hợp lệ/lỗi đã pass. |
| `tools.py` | **Đã triển khai** `with_retry` + arXiv/HF daily/HF search/Exa search/Exa fetch; `python tools.py` chạy thật, cả 5 tool trả kết quả hợp lệ. |
| `agents.py` | **Đã triển khai** prompt lead/researcher/citation-checker, 2 subagent, lead agent với `TodoListMiddleware` + limit middleware. |
| `research.py` | **Đã triển khai** `slugify`, `build_prompt`, `summarize`, `save_outputs`, `main`. |
| `model.py`, `sandbox.py` | Tệp được cung cấp, **không sửa**. Model cấu hình từ biến môi trường; sandbox có cơ chế dọn dẹp. **Lưu ý môi trường**: Daytona SDK (`obstore`) bị Windows Application Control Policy chặn lần đầu import trên máy này — đã tự hết khi AV quét xong DLL; mặc định hiện dùng `SANDBOX=docker` (Docker Desktop) cho ổn định. |
| `finalize_citations.py`, `self_check.py` | Tệp được cung cấp, **không sửa**. Finalizer chuẩn hóa References; self-check kiểm tra tự động trước khi nộp. |
| `requirements.txt`, `.env.example`, `.gitignore` | Khai báo phụ thuộc và cấu hình mẫu; `.env` đã được ignore, không commit khóa. |
| `reports/` | Hiện chỉ có `.gitkeep`, chưa có báo cáo. Mỗi chủ đề cần `.md`, `.sources.json`, `.meta.json`. |

## Kế hoạch thực hiện

### 1. Validator trích dẫn

- [x] [code] Hoàn thiện `check_citations.check(report_text, sources)` theo đủ quy tắc trong GUIDE: nguồn không rỗng; `n` là số nguyên; URL hợp lệ/không trùng; References bắt buộc; citation trong thân khớp sources hai chiều; đúng một dòng tham khảo cho mỗi nguồn; mỗi dòng có đúng một URL khớp nguồn.
- [x] [code] Không tính nội dung trong code span/block hoặc Markdown link `[n](url)` là citation; hỗ trợ citation nhóm `[1, 2]`, `[1-3]`.
- [x] [run] Kiểm tra tay các trường hợp hợp lệ và lỗi (citation không tồn tại, nguồn không được trích dẫn, tham khảo gộp nhiều nguồn) — đúng như mong đợi.

### 2. Công cụ nguồn dữ liệu và retry

- [x] [code] Viết `with_retry`: chỉ retry `RetryableError`, dùng `Retry-After` nếu có; nếu không dùng exponential backoff có jitter và cap; không ngủ sau lần thử cuối.
- [x] [code] Triển khai `arxiv_search`: HTTPS, làm sạch query, tối thiểu 3 giây giữa các request, parse Atom, bỏ version khỏi ID, chuẩn hóa khoảng trắng và giới hạn summary; retry 429 với cap/thử lại dài hơn.
- [x] [code] Triển khai `hf_daily_papers` và `hf_search_papers`: chuẩn hóa record, bỏ paper thiếu ID, lọc/sắp xếp daily theo keyword/upvotes và ưu tiên `ai_summary` cho search.
- [x] [code] Triển khai Exa `web_search`/`web_fetch` qua JSON-RPC HTTP và SSE; nhận diện rate limit HTTP 200 trong `_meta`, retry; dùng `EXA_API_KEY` tùy chọn và che khóa khỏi thông báo lỗi; giới hạn nội dung fetch khoảng 12.000 ký tự.
- [x] [code] Đảm bảo cả năm tool luôn trả chuỗi: `NO RESULTS` khi không có kết quả, `ERROR: ...` khi lỗi sau retry, không để ngoại lệ thoát ra; record gọn theo schema GUIDE.
- [x] [run] Chạy `python tools.py` — cả 5 tool trả kết quả thật hợp lệ (arXiv, HF daily, HF search, Exa web_search, Exa web_fetch).

### 3. Agent, prompt và kiểm soát chi phí

- [x] [code] Viết prompt lead trong `agents.py`: dùng `write_todos`, tạo ít nhất 3 câu hỏi con độc lập, giao researcher song song với đầy đủ ngữ cảnh/định dạng ghi chú, kiểm tra kết quả, hợp nhất nguồn và bảo đảm tối thiểu 3 họ nguồn.
- [x] [code] Viết prompt researcher: mô tả cách dùng công cụ, dùng ít nhất 2 họ nguồn mỗi câu hỏi, đổi nguồn khi `ERROR`/`NO RESULTS`, chỉ ghi sự kiện đã truy xuất và coi nội dung web là dữ liệu không đáng tin.
- [x] [code] Định nghĩa định dạng ghi chú ổn định và yêu cầu researcher trả lại đường dẫn, số nguồn, tóm tắt ngắn; viết prompt citation-checker để đánh giá `SUPPORTED`/`PARTIAL`/`UNSUPPORTED`/`UNVERIFIABLE`.
- [x] [code] Tạo subagent `researcher` với toàn bộ `SOURCE_TOOLS` và `citation-checker` chỉ với `web_fetch`; description hướng dẫn lead dữ liệu phải gửi.
- [x] [code] Tạo lead agent với `TodoListMiddleware`, giới hạn Model/Tool call riêng cho lead (`run_limit=150/300`) và từng subagent (`40/60`), cùng `recursion_limit=1000` khi invoke.
- [x] [run] Đã xác nhận bằng chạy thật: `subagent_calls` 4-8 (tùy chủ đề) và 3-4 họ nguồn hợp lệ trong `meta.json`.

### 4. Điều phối nghiên cứu và lưu đầu ra

- [x] [code] Hoàn thiện `slugify` để tên đầu ra an toàn, không thoát khỏi `reports/`, không rỗng và tối đa 60 ký tự (đã test `../../x` → `x`, rỗng → `topic`, dài → 60 ký tự).
- [x] [code] Hoàn thiện prompt chạy theo mẫu báo cáo tiếng Anh; mọi khẳng định dựa trên ghi chú, có citation; lead không tự viết References.
- [x] [code] Hoàn thiện tổng hợp metadata (`summarize`): model, thời gian, số lần gọi subagent/tool, token lead (input/output), số nguồn và họ nguồn.
- [x] [code] Hoàn thiện `save_outputs`: tải báo cáo và sources từ sandbox; xác nhận báo cáo không rỗng và JSON hợp lệ trước khi ghi bất kỳ đầu ra nào; ghi `.md`, `.sources.json`, `.meta.json`.
- [x] [code] Hoàn thiện `main`: từ chối chủ đề rỗng (exit 2), tạo thư mục sandbox, upload validator/finalizer, invoke lead với `recursion_limit`, lưu đầu ra và báo lỗi bằng mã thoát 1 khi thất bại.
- [x] [safety] Không sửa `model.py`/`sandbox.py`; không upload `.env`/khóa vào sandbox (khóa Exa chỉ ở host, được che khi lộ trong lỗi); mọi lời gọi mạng giữ ở host; sandbox luôn được dọn dẹp qua `with open_sandbox()`.
- [x] [run] Đã chạy `survey about world model` end-to-end trong Docker sandbox 2 lần: lần 1 lộ 2 lỗi thật (lead tự viết `# References` giả trong thân báo cáo; 1 URL arxiv sai domain) → đã sửa prompt (`agents.py`) + siết `check_citations.py` (chặn heading References giả, chặn `source` không hợp lệ) → chạy lại lần 2 **sạch**: `OK: 12 sources, all citations resolve`, `subagent_calls=5`, 3 họ nguồn (arxiv/hf-search/web).

### 5. Sinh và rà soát năm báo cáo

- [x] [report] Sinh báo cáo cho `survey about world model` — **đạt chuẩn** (validator OK, 12 nguồn, 3 họ nguồn, không còn References giả).
- [~] [report] Sinh báo cáo cho `survey about reinforcement learning for LLM reasoning` — **3 lần lỗi liên tiếp, đang chạy lần 4**. Chi tiết đầy đủ xem [RUN_LOG.md](RUN_LOG.md):
  - Lần 1 (OpenRouter): nguồn `[8]` gắn `"source": "alphaXiv"` (không hợp lệ) + trùng bài với `[7]` → đã siết prompt + thêm kiểm tra `source` hợp lệ vào `check_citations.py`.
  - Lần 2-3 (OpenRouter): thất bại vì tài khoản **hết credit** (`402`) → đổi sang Gemini (`gemini-3.5-flash-lite`, key mới), thêm **trần RPM phía client** (`InMemoryRateLimiter` 8 RPM trong `research.py`, dùng chung cho lead + mọi subagent) để không vượt 10 RPM của key.
  - Lần 1 trên Gemini bị treo ~26 phút do thiếu rate limiter (key cũ 15 RPM) → đã kill, thêm rate limiter.
  - Lần với rate limiter: chạy xong (40.6 phút) nhưng chỉ đạt **2/4 họ nguồn được trích dẫn thật** (arxiv, hf-search) — lead có giao thêm việc bù nguồn nhưng không thực sự cite vào thân báo cáo nên `finalize_citations.py` âm thầm loại bỏ → đã sửa `agents.py` bắt lead lên kế hoạch cite đa dạng nguồn *trước khi* viết thân báo cáo.
  - **Lần chạy cuối (sau khi sửa):** đạt chuẩn — `OK: 14 sources, all citations resolve`, `subagent_calls=4`, 3 họ nguồn (`hf-daily`, `hf-search`, `web`), 30.3 phút.
- [~] [report] Sinh báo cáo cho `survey about LLM agents and tool use` — đang chạy (lần 1, dùng bản prompt đã ổn định).
- [ ] [report] Sinh báo cáo cho `survey about video and multimodal generation`.
- [ ] [report] Sinh báo cáo cho `survey about efficient inference and small language models`.
- [ ] [report] Với mỗi báo cáo, kiểm tra cấu trúc TL;DR, Background, 3–6 chủ đề, Trends and open problems; có tổng hợp so sánh, nguồn nền tảng và nguồn gần đây.
- [ ] [report] Chạy citation checker trên cả năm bộ `.md`/`.sources.json`; mở tối thiểu ba citation mỗi báo cáo để đối chiếu nội dung nguồn.
- [ ] [report] Xác nhận từng `.meta.json` có ít nhất 3 lần gọi subagent và ít nhất 3 họ nguồn trong `arxiv`, `hf-daily`, `hf-search`, `web`.

### 6. Kiểm tra cuối và nộp

- [ ] [run] Chạy `python self_check.py`; xử lý hết lỗi về báo cáo, metadata, citation và git.
- [ ] [safety] Kiểm tra `.env` không được track, không có khóa trong tệp đang track/lịch sử git; thu hồi khóa nếu từng bị lộ.
- [ ] [run] Kiểm tra `requirements.txt` cài được môi trường và README có cách cài/chạy/đọc báo cáo đầy đủ.
- [ ] [submit] Commit mã nguồn cùng toàn bộ báo cáo; đẩy lên GitHub public và nộp URL repo.

## Cổng nghiệm thu

- Validator trả `OK: N sources, all citations resolve` với từng báo cáo.
- Có đủ 15 tệp đầu ra cho năm chủ đề: mỗi chủ đề một `.md`, `.sources.json`, `.meta.json`.
- Mỗi metadata đạt `subagent_calls >= 3` và tối thiểu 3 họ nguồn; nguồn khớp URL theo quy ước arXiv/Hugging Face.
- Báo cáo theo mẫu, citations đối chiếu được; References do `finalize_citations.py` sinh bên trong sandbox.
- `python self_check.py` hoàn tất không lỗi; không có `.env`/khóa được commit.

## Lưu ý vận hành

- Làm theo thứ tự triển khai README: validator → tools → agents → research; sau đó chạy đủ năm chủ đề và self-check.
- Cấu hình `.env` cục bộ từ `.env.example`, không ghi giá trị bí mật vào plan, log chia sẻ hoặc sandbox.
- `.env` đã đổi từ OpenRouter sang Gemini (`LAB_MODEL=google_genai:gemini-3.5-flash-lite`, `GOOGLE_API_KEY=<khóa của bạn>`, key có hạn mức 10 RPM) vì key OpenRouter hết credit (`402`). Đã thêm `langchain-google-genai==4.4.0` vào `requirements.txt`.
- `research.py` có **trần RPM phía client** (`MAX_RPM`, mặc định 8, chỉnh qua `.env` bằng `LAB_MAX_RPM`) gắn `InMemoryRateLimiter` vào model dùng chung cho lead và mọi subagent, để tổng số lệnh gọi model ra provider không bao giờ vượt hạn mức của key — bắt buộc khi dùng key free-tier có RPM thấp như Gemini. Hệ quả: mỗi chủ đề chạy chậm hơn nhiều (~30-45 phút thay vì ~4-5 phút như OpenRouter không giới hạn) vì mọi lệnh gọi, kể cả của các subagent "song song", đều xếp hàng qua đúng 1 cổng.
- **Bài học chất lượng quan trọng:** `source_families` trong `meta.json` chỉ tính những nguồn **thực sự được trích dẫn `[n]` trong thân báo cáo** — một nguồn có mặt trong `sources.json` nhưng không được cite sẽ bị `finalize_citations.py` âm thầm loại bỏ. Vì vậy sau mỗi lần chạy phải tự kiểm `meta.json["source_families"]` (không chỉ tin validator `OK`, vì validator không kiểm RUBRIC 2.2) — xem chi tiết lịch sử lỗi này trong [RUN_LOG.md](RUN_LOG.md).
- Tiến độ chi tiết từng lần chạy (thành công/thất bại, nguyên nhân, thời gian) được ghi đầy đủ trong [RUN_LOG.md](RUN_LOG.md) — đọc file đó để biết chính xác đang ở đâu, plan.md chỉ tóm tắt trạng thái cấp cao.
- Khi Exa/arXiv bị giới hạn tốc độ, dùng API key Exa và backoff/cap phù hợp; nếu nguồn thiếu, đổi truy vấn/nguồn thay vì chấp nhận dữ liệu lỗi.
- Không sửa tay báo cáo đã sinh; sửa prompt/mã rồi chạy lại để bảo đảm báo cáo được tạo và kiểm chứng theo đúng quy trình.
- **Sự cố môi trường (máy Windows này):** import `daytona`/`langchain_daytona` lần đầu bị Windows Application Control Policy chặn DLL `_obstore` (tự hết sau khi AV quét xong; import lại thành công). Để tránh phụ thuộc Daytona account, đã đặt `SANDBOX=docker` trong `.env` và khởi động Docker Desktop cục bộ — sandbox chạy trong container Docker không mạng, đúng mô hình an toàn của GUIDE. Nếu Daytona ổn định trên máy bạn, có thể xóa `SANDBOX=docker` để dùng lại Daytona mặc định.

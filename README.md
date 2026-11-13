# Bộ cài context QC Eskimo cho Cline (Ollama) trên máy khác

Bộ này dành cho máy **đã có sẵn `pg4-ai-workflow`**.

## Vì sao Cline ở máy kia "không hiểu context"

1. **Cline không đọc `~/.claude/CLAUDE.md`.** File đó chỉ Claude Code nạp. Mỗi task, Cline chỉ tự nạp:
   - rule global: `Documents\Cline\Rules\*.md`
   - workflow global (gọi bằng `/tên-file.md`): `Documents\Cline\Workflows\*.md`
   - rule của workspace: `.clinerules/` trong thư mục project đang mở

   Các rule QC hiện chỉ nằm trong `~/.claude/CLAUDE.md`, nên task Cline mới nào cũng không thấy chúng.
2. **Ollama chạy local mặc định chỉ có context nhỏ** (vài nghìn token). Riêng system prompt của Cline đã lớn hơn mức đó,
   nên Ollama cắt bớt đầu prompt, và phần bị cắt thường chính là rule. Cần tăng context window (xem bước 3).

## Cài đặt

1. Chép cả thư mục này sang máy kia, mở PowerShell trong thư mục đó rồi chạy:

   ```powershell
   powershell -ExecutionPolicy Bypass -File .\setup-new-machine.ps1 -OllamaCtx 32768
   ```

   Script tự tìm `pg4-ai-workflow` ở `D:\`, `C:\`, `E:\` và thư mục user. Nếu để chỗ khác thì chỉ rõ đường dẫn:

   ```powershell
   ... -File .\setup-new-machine.ps1 -Pg4 E:\src\pg4-ai-workflow -E2E E:\src\eskimo-e2e -OllamaCtx 32768
   ```

   Script sẽ:
   - giải nén `eskimo-e2e.zip` nếu máy chưa có, rồi chạy `npm ci` và cài Chromium; tạo `.env` từ `.env.example`;
   - tạo `Documents\Cline\Rules\eskimo-qc.md` chứa rule QC (9 bước, hard rules, lệnh `plane`), với **đường dẫn thật của máy đó**;
   - tạo `Documents\Cline\Workflows\qa-auto.md`. Đây chỉ là **file trỏ**, bảo Cline đọc `pg4-ai-workflow\claude\commands\qa-auto.md`,
     nên khi team cập nhật qa-auto thì Cline dùng ngay bản mới, không cần chạy lại script;
   - ghi cùng khối rule đó vào `~/.claude/CLAUDE.md`, để Claude Code trên máy đó cũng dùng được;
   - nếu có `-OllamaCtx`: đặt biến môi trường user `OLLAMA_CONTEXT_LENGTH`.

2. Làm tiếp các dòng **TODO** mà script in ra ở cuối: `plane auth login`, điền `.env`, khởi động lại Ollama.

3. **Trong Cline:**
   - Settings → API Provider **Ollama** → đặt **Context Window** bằng đúng số đã truyền cho `-OllamaCtx`, ví dụ 32768. Nếu Cline có tuỳ chọn **Use compact prompt** cho model local, nên bật lên.
   - Bấm biểu tượng cái cân dưới ô chat, kiểm tra `eskimo-qc.md` đang **bật**.
   - Mở **task mới** (task cũ vẫn giữ context cũ), rồi gõ: `/qa-auto.md ESKIMO-<n> --url <url stage>`.

## Gợi ý về model

- Context càng lớn thì càng tốn RAM/VRAM. 32k là mức tối thiểu hợp lý với Cline; nếu máy chịu được thì dùng 64k.
- Model nhỏ (dưới khoảng 14B) thường không theo nổi quy trình nhiều bước. Nếu vẫn bị lạc bước, hãy chọn model lớn hơn
  hoặc dùng Ollama cloud, rồi nhắc ở đầu task: "đọc rule eskimo-qc và làm theo từng bước".

## Lưu ý

- Muốn sửa rule: sửa `personal-claude-md.template.md` rồi chạy lại script. Đừng sửa trực tiếp file đã sinh ra, vì lần chạy sau sẽ ghi đè.
- Khi team cập nhật `qa-auto.md` trong `pg4-ai-workflow`: **không cần làm gì**, Cline đọc trực tiếp file đó.
  Chỉ phải chạy lại script khi **đổi chỗ** thư mục `pg4-ai-workflow` hoặc `eskimo-e2e`.
- Bộ cài **không** chép `.env`, token, `settings.json`, memory, evidence/reports.

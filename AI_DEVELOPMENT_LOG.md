# 🤖 AI 協同開發過程摘要 (AI Development Log)

本文件完整記錄與 Google DeepMind / Antigravity AI 助理結對編程（Pair Programming）共同開發「單人 TRPG 故事生成與 AI 裁判」專題的完整歷程。

---

## 📅 開發進程與四個核心迭代階段

### 階段一：需求分析、技術選型與架構原型確立
- **使用者需求**：
  - 開發單人 TRPG 網頁應用程式，具備角色屬性面板（HP、地點、背包）、劇情對話區、每輪提供 3 個動態風格按鈕與自由文字輸入。
  - 評估 Streamlit 與 Gradio，需以單一檔案 `app.py` 交付。
  - 支援 OpenAI API 格式，透過 System Prompt 要求模型輸出嚴格 JSON 結構。
- **AI 決策與實作**：
  - **框架評估**：選擇 **Streamlit**。因其原生的 `st.session_state` 能無縫管理 RPG 的複雜狀態機，且 `st.columns` 能輕鬆依照 AI 回傳的陣列渲染動態按鈕。
  - **提示詞工程（Prompt Engineering）**：
    - 設定 AI 擔任「幽默嚴謹的地下城主（DM）」，內建 d20 檢定思維。
    - 嚴格約定 JSON 輸出結構：`story`、`hp_change`、`items_obtained`、`location`、`options`（限定常規、策略、搞怪三風格）。
  - **防禦性 JSON 解析**：設計 `parse_dm_response` 函式，自動過濾 Markdown 程式碼區塊（\`\`\`json）與頭尾雜訊。

---

### 階段二：支援本地模型（Local LLM - Ollama / LM Studio）
- **使用者需求**：
  - 希望不綁定雲端付費 API，改用玩家自己電腦裡的「本地模型」。
- **AI 決策與實作**：
  - 增加 **模型來源選擇器**：支援 `🦙 Ollama (11434)`、`🧪 LM Studio (1234)`、`☁️ OpenAI` 與自訂端點。
  - **一鍵自動探索（Auto-Discovery）**：新增 `fetch_available_models` 函式，打本地 API 自動抓取玩家本機已下載的模型清單（如 `qwen2.5:7b`、`llama3.2:3b`），省去手動打字。
  - **API 參數向下相容**：針對部分本地模型未完全支援 `response_format={"type": "json_object"}` 的情況，加入自動降級（Graceful Degradation）機制。

---

### 階段三：環境解耦與依賴修復（解決 `ModuleNotFoundError`）
- **發生問題**：
  - 使用者執行時跳出 `ModuleNotFoundError: 找不到名為「openai」的模組`。
- **AI 偵測與解法**：
  - AI 檢查環境後發現使用者的 Python 雖未安裝 `openai`，但已內建 `requests` 套件。
  - **架構升級**：將底層連線全面重構成標準的 `requests` HTTP POST 呼叫，直接與本地或遠端端點溝通。
  - **成果**：使用者**完全不需要額外 pip 安裝 openai 套件**，重新整理即可直接執行。

---

### 階段四：連線容錯強化與狀態防禦（解決「下一步無按鈕」問題）
- **發生問題**：
  - 使用者回報「現在介面中決定下一步完全沒東西」，並附上截圖。
- **AI 根因分析**：
  1. 使用者電腦後台當時尚未啟動 Ollama 服務（端口 `11434` 拒絕連線）。
  2. 舊程式碼在 `call_dm_agent` 捕獲錯誤後，緊接著執行了 `st.rerun()`，導致 `st.error` 訊息被立即刷掉。
  3. 由於 AI 未能產生內容，`current_options` 保持為空，介面便呈現完全空白。
- **AI 全面重構與三層防禦**：
  1. **側邊欄即時連線燈號**：加入 `check_connection` 函式，即時顯示 `🟢 本地服務連線正常` 或 `🔴 未連線`，並給出啟動提示。
  2. **保底選項（Fallback Options）**：若連線中斷或回傳異常，強制提供 3 個常備行動按鈕，確保玩家操作介面永不卡死。
  3. **持久化錯誤面板**：錯誤訊息存入 `session_state`，並提供「🔄 重新連線嘗試」按鈕。
  4. **🎭 離線模擬模式（Mock Mode）**：內建免模型離線演示功能，即使尚未啟動 Ollama 也能完整體驗遊戲的所有功能。

---

## 🏆 協同開發成果總結

- **程式碼體積**：單一檔案約 450 行，乾淨簡潔、中文註解完整。
- **核心架構**：低耦合（僅依賴 Streamlit 與 Requests）、高容錯（三層異常攔截）、高彈性（本機離線與雲端雙模支援）。
- **人機協作效率**：在數個回合的對話中，迅速完成「原型搭建 ➔ 本地化遷移 ➔ 依賴修復 ➔ 容錯強化」的高強度敏捷迭代。

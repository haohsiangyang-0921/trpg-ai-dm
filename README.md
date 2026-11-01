# 🎲 TRPG 故事生成與 AI 裁判 (支援本地模型 & OpenAI)

這是一個以 Python + Streamlit 開發的單人 TRPG 冒險遊戲。由 AI 擔任地下城主（DM），負責劇情引導、檢定判定、血量管理、掉落物品判定，並在每回合動態生成 3 種風格迥異的行動建議（常規、策略、搞笑）。

支援直接使用您電腦上的 **本地模型**（如 Ollama、LM Studio），完全**免費、不限次數且無需上傳數據至雲端**。

---

## 💻 本地模型支援教學

### 方式一：使用 Ollama（最推薦）
1. 若尚未安裝 Ollama，請至 [ollama.com](https://ollama.com) 下載安裝。
2. 在電腦命令提示字元（CMD）或 PowerShell 中下載並執行推薦的模型（任選其一）：
   ```bash
   # 推薦一：Qwen 2.5（中文語感與 TRPG 劇情生成表現極佳，推薦 7b 或 14b）
   ollama run qwen2.5:7b

   # 推薦二：Llama 3.2（輕量高速，推薦 3b）
   ollama run llama3.2:3b
   ```
3. 啟動本程式後，左側側邊欄選擇 **「🦙 本地模型 (Ollama)」**，點擊 **「🔍 偵測本地模型清單」** 即可自動讀取已下載的模型！

---

### 方式二：使用 LM Studio
1. 開啟 LM Studio 並載入您下載的模型。
2. 點擊左側的 **「Local Server」**（或開發者模式圖示）。
3. 點擊 **「Start Server」**，確認連接埠為 `http://localhost:1234`。
4. 本程式左側側邊欄選擇 **「🧪 本地模型 (LM Studio)」** 即可開始遊玩。

---

## 🚀 快速啟動遊戲

1. **安裝相依套件**：
   ```bash
   pip install streamlit openai
   ```

2. **啟動應用程式**：
   ```bash
   cd "c:\Users\yangh\OneDrive\Desktop\trpg-ai-dm"
   streamlit run app.py
   ```
3. 瀏覽器開啟 `http://localhost:8501`，即可在左側切換本地模型開始冒險！

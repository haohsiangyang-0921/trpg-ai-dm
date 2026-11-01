import os
from PIL import Image, ImageDraw, ImageFont

def create_report_pdf():
    # A4 尺寸 at 150 DPI: 1240 x 1754
    width, height = 1240, 1754
    font_path = "C:/Windows/Fonts/msjh.ttc"
    
    # 載入不同字級字型
    title_font = ImageFont.truetype(font_path, 34)
    subtitle_font = ImageFont.truetype(font_path, 18)
    h2_font = ImageFont.truetype(font_path, 22)
    h3_font = ImageFont.truetype(font_path, 18)
    body_font = ImageFont.truetype(font_path, 15)
    small_font = ImageFont.truetype(font_path, 13)
    code_font = ImageFont.truetype(font_path, 14)

    pages = []

    # ==========================================
    # PAGE 1
    # ==========================================
    p1 = Image.new("RGB", (width, height), "#ffffff")
    d1 = ImageDraw.Draw(p1)

    # 頂部裝飾條
    d1.rectangle([(0, 0), (width, 16)], fill="#2b579a")

    # 標題區
    d1.text((70, 50), "🎲 單人 TRPG 故事生成與 AI 裁判系統", font=title_font, fill="#1a365d")
    d1.text((70, 100), "基於 Streamlit 與本地開源大模型（Local LLM）之智能文字冒險應用 ｜ 專題報告", font=subtitle_font, fill="#4a5568")

    # 分隔線
    d1.line([(70, 135), (width - 70, 135)], fill="#cbd5e0", width=2)

    # Meta Box
    d1.rounded_rectangle([(70, 150), (width - 70, 205)], radius=8, fill="#f7fafc", outline="#e2e8f0", width=1)
    d1.text((90, 168), "專案負責人：haohsiangyang-0921", font=small_font, fill="#4a5568")
    d1.text((450, 168), "技術棧：Python, Streamlit, Requests, Ollama", font=small_font, fill="#4a5568")
    d1.text((920, 168), "專案日期：2026 年 11 月", font=small_font, fill="#4a5568")

    # Section 1: 一、做什麼 (What & Why)
    y = 230
    d1.rectangle([(70, y), (78, y + 26)], fill="#3182ce")
    d1.text((90, y), "一、做什麼（What & Why）：專題背景與核心機制", font=h2_font, fill="#2b579a")
    y += 40

    intro_text = (
        "傳統桌上角色扮演遊戲（TRPG）以高自由度著稱，但面臨「湊人開團難、資深地下城主（DM）難尋、"
        "規則繁瑣門檻高」等困境。本專題旨在打造一個輕量、單人隨開即玩的 TRPG 智能冒險系統，"
        "讓 AI 擔任嚴謹且風趣的裁判，帶來零社交負擔的沉浸式冒險體驗。"
    )
    d1.text((70, y), intro_text[:62], font=body_font, fill="#2d3748")
    y += 26
    d1.text((70, y), intro_text[62:], font=body_font, fill="#2d3748")
    y += 40

    # 核心特色卡片
    d1.rounded_rectangle([(70, y), (width - 70, y + 175)], radius=8, fill="#ebf8ff", outline="#bee3f8", width=1)
    d1.text((95, y + 15), "🌟 三大核心特色與產品突破：", font=h3_font, fill="#2b6cb0")
    
    features = [
        "1. AI 數值與命運裁判：內建 d20 檢定邏輯，即時結算傷害扣血（HP）、探索補給、裝備掉落與地點轉換。",
        "2. 動態三風格建議行動：每輪即時生成「🅰️ 常規穩健」、「🅱️ 策略洞察」、「🅲 搞笑奇策」三種按鈕與自由打字框。",
        "3. 隱私優先與本地運行：支援 Ollama / LM Studio 本機端點，完全免費離線運行，保護個資並避免 API 費用。"
    ]
    fy = y + 50
    for f in features:
        d1.text((95, fy), f, font=body_font, fill="#2d3748")
        fy += 38

    y += 205

    # Section 2: 二、給誰用 (Target Audience)
    d1.rectangle([(70, y), (78, y + 26)], fill="#3182ce")
    d1.text((90, y), "二、給誰用（Target Audience）：目標客群與應用場景", font=h2_font, fill="#2b579a")
    y += 40

    # 表格繪製
    table_x = 70
    col_w = [260, 400, 440]
    table_w = sum(col_w)
    row_h = 52

    # 表頭
    d1.rectangle([(table_x, y), (table_x + table_w, y + 40)], fill="#edf2f7")
    d1.text((table_x + 15, y + 10), "目標族群", font=h3_font, fill="#1a202c")
    d1.text((table_x + col_w[0] + 15, y + 10), "核心痛點與使用場景", font=h3_font, fill="#1a202c")
    d1.text((table_x + col_w[0] + col_w[1] + 15, y + 10), "本產品帶來的價值", font=h3_font, fill="#1a202c")
    d1.rectangle([(table_x, y), (table_x + table_w, y + 40)], outline="#cbd5e0", width=1)
    y += 40

    rows = [
        ("TRPG 初學者／愛好者", "找不到同好湊團、規則龐大複雜難以上手", "零社交門檻，單人隨時開團，由 AI 循序引導。"),
        ("桌遊 DM 與小說創作者", "備團時靈感枯竭、NPC 與遭遇情境單調", "作為靈感發想器，利用三風格選項激發腦力震盪。"),
        ("開源 AI 與本地模型愛好者", "不願承擔商業 API 費用、重視數據隱私安全", "本機離線運算（Qwen2.5 / Llama3.2），無數據洩漏。"),
        ("日常文字休閒玩家", "通勤或碎片時間想體驗微型冒險故事", "每局 5-10 分鐘輕快節奏，直覺按鈕點擊即玩。")
    ]

    for i, (col1, col2, col3) in enumerate(rows):
        bg = "#ffffff" if i % 2 == 0 else "#f7fafc"
        d1.rectangle([(table_x, y), (table_x + table_w, y + row_h)], fill=bg, outline="#cbd5e0", width=1)
        d1.text((table_x + 15, y + 15), col1, font=body_font, fill="#2d3748")
        d1.text((table_x + col_w[0] + 15, y + 15), col2, font=small_font, fill="#4a5568")
        d1.text((table_x + col_w[0] + col_w[1] + 15, y + 15), col3, font=small_font, fill="#22543d")
        y += row_h

    # 頁尾
    d1.line([(70, height - 70), (width - 70, height - 70)], fill="#e2e8f0", width=1)
    d1.text((width // 2 - 40, height - 50), "第 1 頁 / 共 2 頁", font=small_font, fill="#a0aec0")
    pages.append(p1)

    # ==========================================
    # PAGE 2
    # ==========================================
    p2 = Image.new("RGB", (width, height), "#ffffff")
    d2 = ImageDraw.Draw(p2)

    # 頂部裝飾條
    d2.rectangle([(0, 0), (width, 16)], fill="#2b579a")

    y = 50
    # Section 3: 三、怎麼做 (How)
    d2.rectangle([(70, y), (78, y + 26)], fill="#3182ce")
    d2.text((90, y), "三、怎麼做（Architecture & Implementation）：技術實作與架構", font=h2_font, fill="#2b579a")
    y += 40

    arch_points = [
        ("1. 極簡依賴與無 SDK 通訊層：", "捨棄臃腫的第三方 SDK，直接採用原生 Requests 模組發送 OpenAI 相容 REST API 請求，完全杜絕 ModuleNotFoundError。"),
        ("2. 前端狀態機（Streamlit Session State）：", "精準維護血量、背包物品、當前地點、對話歷程與選項陣列，達成高內聚低耦合的單檔案設計架構。"),
        ("3. 提示詞契約與結構化輸出（JSON Schema）：", "約束 AI 以標準 JSON 格式回傳 story、hp_change、items_obtained 與三風格 options，輔以正則容錯抽取。"),
        ("4. 三層容錯防禦體系（Fault Tolerance）：", "側邊欄即時監控燈號（🟢/🔴）、操作面板保底按鈕、以及無需啟動任何模型的「🎭 離線模擬演示模式」。")
    ]
    for title, desc in arch_points:
        d2.text((70, y), title, font=h3_font, fill="#1a365d")
        y += 24
        d2.text((90, y), desc, font=small_font, fill="#4a5568")
        y += 32

    y += 15

    # Section 4: 四、怎麼測 (Testing & QA)
    d2.rectangle([(70, y), (78, y + 26)], fill="#3182ce")
    d2.text((90, y), "四、怎麼測（Testing & QA）：驗證策略與成果", font=h2_font, fill="#2b579a")
    y += 40

    col_w4 = [220, 260, 480, 140]
    table_w4 = sum(col_w4)
    row_h4 = 46

    # 表頭
    d2.rectangle([(table_x, y), (table_x + table_w4, y + 36)], fill="#edf2f7")
    d2.text((table_x + 10, y + 8), "測試維度", font=h3_font, fill="#1a202c")
    d2.text((table_x + col_w4[0] + 10, y + 8), "測試項目", font=h3_font, fill="#1a202c")
    d2.text((table_x + col_w4[0] + col_w4[1] + 10, y + 8), "測試步驟與驗證情境", font=h3_font, fill="#1a202c")
    d2.text((table_x + col_w4[0] + col_w4[1] + col_w4[2] + 10, y + 8), "驗證結果", font=h3_font, fill="#1a202c")
    d2.rectangle([(table_x, y), (table_x + table_w4, y + 36)], outline="#cbd5e0", width=1)
    y += 36

    tests = [
        ("模型輸出相容性", "Qwen 2.5 / Llama 3.2", "連續 20 回合各類行動，測試 JSON 抽取與 Markdown 剝除成功率", "100% 通過"),
        ("斷線防護測試", "Ollama 未開機 / 端口佔用", "關閉本地服務點擊行動，驗證燈號轉紅、錯誤留存與保底按鈕", "穩定不崩潰"),
        ("數值邏輯驗證", "HP 變動 / 死亡機制", "模擬扣血至 0，驗證進度條歸零、彈出陣亡墓碑與重置按鈕", "邏輯正確"),
        ("環境解耦測試", "無 openai 套件環境", "在純 Streamlit + Requests 乾淨環境下啟動與執行所有流程", "零相依報錯")
    ]

    for i, (c1, c2, c3, c4) in enumerate(tests):
        bg = "#ffffff" if i % 2 == 0 else "#f7fafc"
        d2.rectangle([(table_x, y), (table_x + table_w4, y + row_h4)], fill=bg, outline="#cbd5e0", width=1)
        d2.text((table_x + 10, y + 13), c1, font=body_font, fill="#2d3748")
        d2.text((table_x + col_w4[0] + 10, y + 13), c2, font=small_font, fill="#4a5568")
        d2.text((table_x + col_w4[0] + col_w4[1] + 10, y + 13), c3, font=small_font, fill="#4a5568")
        d2.text((table_x + col_w4[0] + col_w4[1] + col_w4[2] + 15, y + 13), c4, font=body_font, fill="#2b6cb0")
        y += row_h4

    y += 35

    # Section 5: 五、下一步 (Next Steps)
    d2.rectangle([(70, y), (78, y + 26)], fill="#3182ce")
    d2.text((90, y), "五、下一步（Next Steps & Roadmap）：未來擴充計畫", font=h2_font, fill="#2b579a")
    y += 40

    roadmap = [
        ("1. 3D 物理投骰視覺化：", "整合 WebGL / Three.js 物理引擎，在重大判定（如大成功 / 大失敗）時呈現華麗 3D 擲骰動畫。"),
        ("2. 多角色隊友系統（Multi-Agent）：", "引入個性迥異的 AI 冒險夥伴（法師、戰士、盜賊），在對話中互相吐槽並協同戰鬥。"),
        ("3. 語音朗讀與音效氛圍（TTS & BGM）：", "整合本地語音合成模型（TTS）朗讀 DM 旁白，並隨冒險情境自動切換地下城環境音。"),
        ("4. 冒險回憶錄匯出：", "通關後一鍵排版生成精美冒險小說回憶錄，支援 Markdown 與 PDF 格式匯出收藏。")
    ]
    for r_title, r_desc in roadmap:
        d2.text((70, y), r_title, font=h3_font, fill="#2b579a")
        y += 24
        d2.text((90, y), r_desc, font=small_font, fill="#4a5568")
        y += 30

    # 頁尾
    d2.line([(70, height - 70), (width - 70, height - 70)], fill="#e2e8f0", width=1)
    d2.text((70, height - 50), "專案 GitHub: https://github.com/haohsiangyang-0921/trpg-ai-dm", font=small_font, fill="#718096")
    d2.text((width - 180, height - 50), "第 2 頁 / 共 2 頁", font=small_font, fill="#a0aec0")
    pages.append(p2)

    # 輸出 PDF
    out_pdf_path = "c:/Users/yangh/OneDrive/Desktop/trpg-ai-dm/TRPG_AI_DM_專題報告.pdf"
    pages[0].save(out_pdf_path, save_all=True, append_images=pages[1:], resolution=150.0)
    print(f"PDF 報告生成成功：{out_pdf_path}")

if __name__ == "__main__":
    create_report_pdf()

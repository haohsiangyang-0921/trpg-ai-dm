import os
from PIL import Image, ImageDraw, ImageFont

def create_slides_pdf():
    # 16:9 簡報尺寸: 1600 x 900
    width, height = 1600, 900
    font_path = "C:/Windows/Fonts/msjh.ttc"
    
    title_font = ImageFont.truetype(font_path, 40)
    h2_font = ImageFont.truetype(font_path, 32)
    h3_font = ImageFont.truetype(font_path, 22)
    body_font = ImageFont.truetype(font_path, 18)
    sub_font = ImageFont.truetype(font_path, 15)
    tag_font = ImageFont.truetype(font_path, 14)

    slides = []

    def draw_base_slide(timing_tag, slide_num):
        img = Image.new("RGB", (width, height), "#0f172a")
        d = ImageDraw.Draw(img)
        # 背景漸層感網格/卡片
        d.rounded_rectangle([(40, 30), (width - 40, height - 40)], radius=16, fill="#1e293b", outline="#334155", width=2)
        # 時間標籤
        d.rounded_rectangle([(70, 55), (320, 95)], radius=10, fill="#0f172a", outline="#38bdf8", width=1)
        d.text((85, 65), timing_tag, font=tag_font, fill="#38bdf8")
        # 頁碼
        d.text((width - 150, 65), f"Slide {slide_num} / 5", font=tag_font, fill="#64748b")
        d.text((70, height - 75), "單人 TRPG 故事生成與 AI 裁判 ｜ 90 秒展示", font=sub_font, fill="#64748b")
        d.text((width - 450, height - 75), "GitHub: haohsiangyang-0921/trpg-ai-dm", font=sub_font, fill="#38bdf8")
        return img, d

    # ----------------------------------------
    # Slide 1: 00~15s 痛點開場
    # ----------------------------------------
    s1, d1 = draw_base_slide("⏱️ 00 ~ 15 秒 ｜ 痛點與開場", 1)
    d1.text((70, 130), "🎲 單人 TRPG 故事生成與 AI 裁判", font=title_font, fill="#f8fafc")
    d1.text((70, 195), "想體驗高自由度的跑團冒險，卻總是湊不到人、找不到地下城主（DM）？", font=h3_font, fill="#94a3b8")

    cards1 = [
        ("👥 揪團開團極難", "3-5 人很難湊齊時間\n常常因為一人缺席就流團"),
        ("📖 規則繁瑣龐大", "厚厚數百頁的規則手冊\n新手光看就望而卻步"),
        ("🧙‍♂️ 專業 DM 稀缺", "需要經驗豐富的主持人\n帶領劇情、兼顧公平判定")
    ]
    cx = 70
    cw = 450
    for title, desc in cards1:
        d1.rounded_rectangle([(cx, 270), (cx + cw, 520)], radius=12, fill="#0f172a", outline="#334155", width=1)
        d1.text((cx + 25, 305), title, font=h3_font, fill="#38bdf8")
        lines = desc.split("\n")
        d1.text((cx + 25, 375), lines[0], font=body_font, fill="#cbd5e0")
        d1.text((cx + 25, 420), lines[1], font=body_font, fill="#94a3b8")
        cx += cw + 45

    d1.rounded_rectangle([(70, 580), (width - 70, 680)], radius=12, fill="#1e3a5f", outline="#38bdf8", width=1)
    d1.text((95, 615), "💡 我們的解答：讓 AI 化身專屬地下城主，打造單人隨開即玩、零社交壓力的沉浸式冒險！", font=h3_font, fill="#ffffff")
    slides.append(s1)

    # ----------------------------------------
    # Slide 2: 15~40s 核心突破
    # ----------------------------------------
    s2, d2 = draw_base_slide("⏱️ 15 ~ 40 秒 ｜ 核心功能與特色", 2)
    d2.text((70, 130), "✨ 三大產品突破與特色", font=title_font, fill="#f8fafc")
    d2.text((70, 195), "將傳統龐雜的跑團體驗，轉化為直覺流暢的智能文字冒險介面：", font=h3_font, fill="#94a3b8")

    cards2 = [
        ("🎲 1. 真正 AI 裁判與檢定", "心中自帶 d20 檢定邏輯！\n即時計算受到傷害（扣除 HP）、\n獲得戰利品與切換地點，\n絕非單純敷衍的聊天機器人。"),
        ("🎯 2. 動態三風格建議行動", "每輪即時生成 3 個風格按鈕：\n🅰️ 常規穩健 ｜ 🅱️ 策略洞察\n🅲 搞笑奇策（出人意料反饋）\n點擊即行動，亦可自由打字！"),
        ("💻 3. 本機離線運行 (Local LLM)", "深度原生適配 Ollama！\n支援 Qwen2.5 / Llama3.2，\n完全免費、零 API 成本、\n遊戲數據絕不上傳，隱私無虞。")
    ]
    cx = 70
    cw = 450
    for title, desc in cards2:
        d2.rounded_rectangle([(cx, 260), (cx + cw, 640)], radius=12, fill="#0f172a", outline="#334155", width=1)
        d2.text((cx + 25, 295), title, font=h3_font, fill="#38bdf8")
        lines = desc.split("\n")
        ly = 365
        for l in lines:
            d2.text((cx + 25, ly), l, font=body_font, fill="#cbd5e0")
            ly += 45
        cx += cw + 45
    slides.append(s2)

    # ----------------------------------------
    # Slide 3: 40~65s 技術架構
    # ----------------------------------------
    s3, d3 = draw_base_slide("⏱️ 40 ~ 65 秒 ｜ 技術架構與容錯", 3)
    d3.text((70, 130), "⚙️ 極簡架構與三層容錯防禦", font=title_font, fill="#f8fafc")
    d3.text((70, 195), "從依賴解耦到狀態容錯，打造永不卡死的健壯單檔案系統（Single-File）：", font=h3_font, fill="#94a3b8")

    # 左側架構卡片
    d3.rounded_rectangle([(70, 260), (750, 680)], radius=12, fill="#0f172a", outline="#334155", width=1)
    d3.text((95, 290), "🏗️ 極簡單檔案架構 (app.py)", font=h3_font, fill="#38bdf8")
    arch_txt = [
        "• 前端與狀態機：Streamlit session_state 維護 HP、背包與對話流",
        "• 通訊層解耦：捨棄第三方 SDK，直接採用 Requests 呼叫 REST API",
        "• 零 ModuleNotFoundError：玩家環境不需額外安裝 openai 套件",
        "• 嚴格 JSON 契約：約束標準輸出，並實作正則容錯提取算法"
    ]
    ay = 360
    for a in arch_txt:
        d3.text((95, ay), a, font=body_font, fill="#cbd5e0")
        ay += 65

    # 右側容錯防禦
    d3.rounded_rectangle([(810, 260), (width - 70, 680)], radius=12, fill="#0f172a", outline="#334155", width=1)
    d3.text((835, 290), "🛡️ 三層容錯防禦體系 (Fault-Tolerant)", font=h3_font, fill="#10b981")
    ft_txt = [
        "• 側邊欄連線燈號：即時心跳監測 Ollama 本地端點 (🟢/🔴 狀態燈)",
        "• 操作按鈕防卡死：連線中斷時提供保底建議選項，介面絕不留白",
        "• 錯誤提示面板：錯誤留存 session_state，提供一鍵重新連線按鈕",
        "• 🎭 離線模擬模式：無需啟動任何 AI 模型亦能流暢體驗完整遊戲"
    ]
    fy = 360
    for f in ft_txt:
        d3.text((835, fy), f, font=body_font, fill="#cbd5e0")
        fy += 65
    slides.append(s3)

    # ----------------------------------------
    # Slide 4: 65~80s Live Demo
    # ----------------------------------------
    s4, d4 = draw_base_slide("⏱️ 65 ~ 80 秒 ｜ 實機展示 (Live Demo)", 4)
    d4.text((70, 130), "🎮 實機互動體驗演示", font=title_font, fill="#f8fafc")
    d4.text((70, 195), "從進入迷霧森林、遭遇毒藤判定受傷，到出人意料的搞怪反饋：", font=h3_font, fill="#94a3b8")

    # 模擬主畫面 Box
    d4.rounded_rectangle([(70, 260), (width - 70, 680)], radius=12, fill="#020617", outline="#334155", width=2)
    # 頂部狀態列
    d4.text((95, 285), "📍 當前地點：迷霧森林深處古老祭壇", font=body_font, fill="#94a3b8")
    d4.text((620, 285), "❤️ 生命值：17 / 20 (🩸 受到傷害: -3 HP)", font=body_font, fill="#ef4444")
    d4.text((1150, 285), "🎒 獲得物品：神秘的哥布林短刀", font=body_font, fill="#f59e0b")
    d4.line([(95, 330), (width - 95, 330)], fill="#1e293b", width=1)

    # 對話
    d4.text((95, 355), "🧙‍♂️ AI 裁判（DM）：", font=h3_font, fill="#38bdf8")
    dm_speech = (
        "你擲出了 14 點檢定成功！你俐落地揮劍斬斷了撲面而來的毒藤，但手臂仍被倒鉤劃破了一道血口（生命 -3 HP）。\n"
        "藤蔓底部掉出一把刻有古怪符文的「哥布林短刀」！就在此時，陰暗樹叢深處傳來粗重的低吼聲..."
    )
    d4.text((95, 400), dm_speech.split("\n")[0], font=body_font, fill="#e2e8f0")
    d4.text((95, 440), dm_speech.split("\n")[1], font=body_font, fill="#e2e8f0")

    # 選項按鈕
    d4.text((95, 510), "🎯 請決定您的下一步行動：", font=sub_font, fill="#94a3b8")
    btn_w = 440
    bx = 95
    demo_btns = [
        ("🅰️ 常規行動", "拔出鐵劍擺出防禦姿態"),
        ("🅱️ 策略行動", "點燃火把擲向樹叢照亮敵人"),
        ("🅲 搞笑奇策", "舉起短刀大唱哥布林戰歌試圖裝熟")
    ]
    for btag, btext in demo_btns:
        border_col = "#f59e0b" if "搞笑" in btag else "#334155"
        d4.rounded_rectangle([(bx, 545), (bx + btn_w, 640)], radius=8, fill="#1e293b", outline=border_col, width=2)
        d4.text((bx + 20, 560), btag, font=sub_font, fill="#38bdf8" if "常規" in btag else ("#10b981" if "策略" in btag else "#f59e0b"))
        d4.text((bx + 20, 595), btext, font=body_font, fill="#f8fafc")
        bx += btn_w + 25
    slides.append(s4)

    # ----------------------------------------
    # Slide 5: 80~90s 下一步與結語
    # ----------------------------------------
    s5, d5 = draw_base_slide("⏱️ 80 ~ 90 秒 ｜ 未來展望與結語", 5)
    d5.text((70, 130), "🚀 未來展望與總結", font=title_font, fill="#f8fafc")
    d5.text((70, 195), "讓 AI 成為每個人口袋裡隨身攜帶的地下城主，未來升級藍圖：", font=h3_font, fill="#94a3b8")

    cards5 = [
        ("🎲 3D 物理投骰視覺", "結合 Three.js WebGL 引擎，\n在關鍵檢定呈現真實 3D 物理\n滾動與暴擊大成功（Natural 20）特效！"),
        ("👥 Multi-Agent AI 隊友", "引入法師、狂戰士等 AI 隊友，\n冒險途中具備各自不同性格，\n在對話中互相交流並協同作戰！"),
        ("🎙️ 語音朗讀與動態氛圍", "整合本地語音模型（TTS），\n以沉浸口吻朗讀 DM 旁白，\n並隨冒險情境自適應播放地牢配樂！")
    ]
    cx = 70
    cw = 450
    for title, desc in cards5:
        d5.rounded_rectangle([(cx, 260), (cx + cw, 530)], radius=12, fill="#0f172a", outline="#334155", width=1)
        d5.text((cx + 25, 295), title, font=h3_font, fill="#38bdf8")
        lines = desc.split("\n")
        ly = 365
        for l in lines:
            d5.text((cx + 25, ly), l, font=body_font, fill="#cbd5e0")
            ly += 45
        cx += cw + 45

    d5.rounded_rectangle([(70, 570), (width - 70, 680)], radius=12, fill="#1e3a5f", outline="#38bdf8", width=1)
    d5.text((95, 605), "🎉 感謝各位聆聽！開源專案已上線 GitHub，歡迎體驗跑團！", font=h3_font, fill="#ffffff")
    d5.text((95, 640), "GitHub Repo: https://github.com/haohsiangyang-0921/trpg-ai-dm", font=body_font, fill="#38bdf8")
    slides.append(s5)

    # 輸出 PDF
    out_pdf_path = "c:/Users/yangh/OneDrive/Desktop/trpg-ai-dm/TRPG_AI_DM_90秒展示簡報.pdf"
    slides[0].save(out_pdf_path, save_all=True, append_images=slides[1:], resolution=150.0)
    print(f"簡報 PDF 生成成功：{out_pdf_path}")

if __name__ == "__main__":
    create_slides_pdf()

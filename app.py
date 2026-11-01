import os
import json
import re
import requests
import streamlit as st

# ==========================================
# 頁面配置
# ==========================================
st.set_page_config(
    page_title="TRPG 故事生成與 AI 裁判",
    page_icon="🎲",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自訂 CSS 美化 UI 標籤與按鈕樣式
st.markdown("""
<style>
    .badge-hp-loss {
        background-color: #ff4d4f;
        color: white;
        padding: 3px 9px;
        border-radius: 12px;
        font-size: 0.85em;
        font-weight: bold;
    }
    .badge-hp-gain {
        background-color: #52c41a;
        color: white;
        padding: 3px 9px;
        border-radius: 12px;
        font-size: 0.85em;
        font-weight: bold;
    }
    .badge-item {
        background-color: #faad14;
        color: #222;
        padding: 3px 9px;
        border-radius: 12px;
        font-size: 0.85em;
        font-weight: bold;
    }
    .stButton button {
        height: auto;
        min-height: 3.5rem;
        white-space: normal;
        word-wrap: break-word;
        font-size: 0.95rem;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 遊戲預設狀態常數
# ==========================================
DEFAULT_MAX_HP = 20
DEFAULT_HP = 20
DEFAULT_LOCATION = "灰燼鎮外的迷霧森林入口"
DEFAULT_INVENTORY = ["生鏽鐵劍", "旅行乾糧 x2", "簡易火把"]

SYSTEM_PROMPT = """你是一位專業、幽默且規則嚴謹的 TRPG 地下城主（Dungeon Master, DM）。
玩家正在進行一場單人文字角色扮演冒險。

【職責與判斷準則】
1. 根據玩家的行動進行合理判定（心中進行 d20 檢定：難度 DC、大成功、大失敗、普通成功或失敗）。
2. 提供生動、沉浸感強的繁體中文場景描寫與幽默風趣的口吻，並明確描述行動的後果。
3. 若玩家遭遇陷阱、戰鬥失誤或受到傷害，請在 hp_change 中扣除血量（負整數，例如 -3）；若得到治療或充分休息，請恢復血量（正整數，例如 +2）。一般無危險的行動扣 0。
4. 若玩家搜索、開寶箱或繳獲戰利品，請在 items_obtained 陣列中列出獲得的物品名稱（若無則為空陣列 []）。
5. 若玩家移動到了新場景或深入某處，請更新 location；若未移動請保持原地點。
6. 【核心特色】每次回應的最後，必須提供 3 個截然不同風格的下一步行動建議選項：
   - 選項 1：認真／常規行動（正統穩健的做法）
   - 選項 2：認真／策略行動（善用環境、智謀、潛行或法術等深入策略）
   - 選項 3：有趣／幽默／意想不到的行動（大膽無厘頭、破格搞笑或令人啼笑皆非的點子）

【輸出格式要求】
請嚴格輸出符合以下結構的合法純 JSON 物件，請勿附加任何額外開頭或結尾文字：
{
  "story": "生動的劇情描述與判定結果（含行動後果與當前情勢）",
  "hp_change": 0,
  "items_obtained": [],
  "location": "當前或新地點",
  "options": [
    "選項 A（常規行動）",
    "選項 B（策略行動）",
    "選項 C（有趣/意想不到行動）"
  ]
}
"""

# ==========================================
# 離線模擬 DM (當本地模型尚未啟動時的備用演示)
# ==========================================
def mock_dm_reply(user_action: str) -> dict:
    """離線演示回應，讓使用者在尚未啟動 Ollama 時也能體驗完整流程"""
    return {
        "story": f"【離線模擬裁判】你選擇了：「{user_action}」。你小心翼翼地向前邁進，四周迷霧散開，隱約看見前方有一座傾頹的石質祭壇，上面泛著微弱的藍光。隱約有某種生物正在暗處窺伺著你！",
        "hp_change": 0,
        "items_obtained": ["神秘的藍色鵝卵石"],
        "location": "迷霧森林深處的古老祭壇",
        "options": [
            "拔出鐵劍，警戒並走向祭壇查看藍光來源",
            "躲在巨石後方屏住呼吸，暗中觀察窺伺者是誰",
            "大聲對著暗處喊：「是誰在那裡？我這裡有好吃的旅行乾糧！」"
        ]
    }

# ==========================================
# 輔助函式：JSON 安全解析
# ==========================================
def parse_dm_response(raw_text: str) -> dict:
    text = raw_text.strip()
    
    # 移除 markdown 程式碼區塊 ```json ... ```
    if "```" in text:
        block_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text, re.IGNORECASE)
        if block_match:
            text = block_match.group(1).strip()

    try:
        return json.loads(text)
    except Exception:
        pass

    # 搜尋第一個 { 到最後一個 }
    try:
        start_idx = text.find("{")
        end_idx = text.rfind("}")
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            json_candidate = text[start_idx:end_idx + 1]
            return json.loads(json_candidate)
    except Exception:
        pass
    
    return {
        "story": raw_text,
        "hp_change": 0,
        "items_obtained": [],
        "location": st.session_state.get("location", DEFAULT_LOCATION),
        "options": [
            "仔細觀察四周的動靜與環境細節",
            "拔出武器，做好應對突發戰鬥的準備",
            "對著虛空大喊：「DM，擲骰結果到底是幾點？！」"
        ]
    }

# ==========================================
# 輔助函式：檢查端點連線狀態
# ==========================================
def check_connection(base_url: str) -> bool:
    try:
        url = base_url.split("/v1")[0].rstrip("/")
        # 先試根目錄或 tags
        r = requests.get(url, timeout=1.0)
        return r.status_code in [200, 404, 403]
    except Exception:
        return False

# ==========================================
# 輔助函式：取得可用模型清單
# ==========================================
def fetch_available_models(base_url: str, api_key: str):
    url = base_url.rstrip("/")
    models_url = f"{url}/models" if url.endswith("/v1") else f"{url}/v1/models"
    headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
        
    try:
        resp = requests.get(models_url, headers=headers, timeout=2.0)
        if resp.status_code == 200:
            data = resp.json()
            if "data" in data and isinstance(data["data"], list):
                return [m["id"] for m in data["data"] if "id" in m]
    except Exception:
        pass

    # Ollama 原生 tags 端點
    if "11434" in base_url:
        try:
            native_url = base_url.split("/v1")[0].rstrip("/") + "/api/tags"
            resp = requests.get(native_url, timeout=2.0)
            if resp.status_code == 200:
                data = resp.json()
                if "models" in data and isinstance(data["models"], list):
                    return [m["name"] for m in data["models"] if "name" in m]
        except Exception:
            pass

    return []

# ==========================================
# 輔助函式：通用 HTTP API 呼叫
# ==========================================
def chat_completion(base_url: str, api_key: str, model: str, messages: list, temperature: float = 0.7):
    url = base_url.rstrip("/")
    endpoint = f"{url}/chat/completions" if url.endswith("/v1") else f"{url}/v1/chat/completions"
        
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "response_format": {"type": "json_object"}
    }

    try:
        resp = requests.post(endpoint, headers=headers, json=payload, timeout=90)
        # 若因為 response_format 不被該模型支援而回傳 400，降級重試
        if resp.status_code == 400 and "response_format" in resp.text:
            payload.pop("response_format", None)
            resp = requests.post(endpoint, headers=headers, json=payload, timeout=90)
            
        if resp.status_code != 200:
            raise RuntimeError(f"HTTP {resp.status_code}: {resp.text}")

        data = resp.json()
        return data["choices"][0]["message"]["content"]
    except requests.exceptions.ConnectionError:
        raise ConnectionError(
            f"無法連接到服務端點：{endpoint}。\n"
            f"請確認 Ollama 服務是否已啟動（在終端機輸入：ollama run {model}）"
        )
    except Exception as e:
        raise e

# ==========================================
# 初始化 Session State
# ==========================================
def init_game_state(reset: bool = False):
    if reset or "messages" not in st.session_state:
        st.session_state.messages = []
        st.session_state.hp = DEFAULT_HP
        st.session_state.max_hp = DEFAULT_MAX_HP
        st.session_state.location = DEFAULT_LOCATION
        st.session_state.inventory = list(DEFAULT_INVENTORY)
        st.session_state.current_options = []
        st.session_state.game_over = False
        st.session_state.game_started = False
        st.session_state.last_error = None

init_game_state()

# ==========================================
# 側邊欄：角色狀態與模型設定
# ==========================================
with st.sidebar:
    st.title("🛡️ 冒險者面板")
    
    # 1. 生命值 (HP)
    hp_percent = max(0.0, min(1.0, st.session_state.hp / st.session_state.max_hp))
    st.subheader(f"❤️ 生命值: {st.session_state.hp} / {st.session_state.max_hp}")
    st.progress(hp_percent)
    
    if st.session_state.hp <= 0:
        st.error("💀 冒險者已經陣亡！")
    elif st.session_state.hp <= 5:
        st.warning("⚠️ 傷勢嚴重，處於瀕死邊緣！")

    st.markdown("---")

    # 2. 當前地點
    st.subheader("📍 當前地點")
    st.info(st.session_state.location)

    st.markdown("---")

    # 3. 裝備與道具背包
    st.subheader("🎒 道具背包")
    if st.session_state.inventory:
        for item in st.session_state.inventory:
            st.markdown(f"- 📦 {item}")
    else:
        st.caption("背包空空如也...")

    st.markdown("---")

    # 4. AI 模型來源設定
    st.subheader("🤖 AI 模型設定")
    
    provider = st.radio(
        "選擇模型來源",
        ["🦙 本地模型 (Ollama)", "🧪 本地模型 (LM Studio)", "☁️ 雲端 (OpenAI)", "🎭 離線模擬 (免模型直接體驗)"],
        index=0
    )

    if provider == "🦙 本地模型 (Ollama)":
        default_base_url = "http://localhost:11434/v1"
        default_api_key = "ollama"
        default_model = "llama3.2"
    elif provider == "🧪 本地模型 (LM Studio)":
        default_base_url = "http://localhost:1234/v1"
        default_api_key = "lm-studio"
        default_model = "local-model"
    elif provider == "☁️ 雲端 (OpenAI)":
        default_base_url = "https://api.openai.com/v1"
        default_api_key = os.environ.get("OPENAI_API_KEY", "")
        default_model = "gpt-4o-mini"
    else:
        default_base_url = "http://localhost:11434/v1"
        default_api_key = "mock"
        default_model = "mock-agent"

    active_base_url = st.text_input("Base URL", value=default_base_url)
    
    # 即時連線狀態檢查
    if "本地" in provider:
        active_api_key = default_api_key
        is_alive = check_connection(active_base_url)
        if is_alive:
            st.success("🟢 本地服務連線正常！")
        else:
            st.error("🔴 未連線至本地服務！")
            st.caption("👉 請在電腦啟動 Ollama 應用程式，或於終端機執行：`ollama run llama3.2`")
    elif "雲端" in provider:
        active_api_key = st.text_input("API Key", value=default_api_key, type="password")
    else:
        active_api_key = "mock"
        st.info("🎭 離線演示模式：無需啟動任何 AI 模型即可測試全部 UI 功能！")

    # 偵測本地模型清單按鈕
    if "本地" in provider:
        if st.button("🔍 偵測本地模型清單", use_container_width=True):
            detected = fetch_available_models(active_base_url, active_api_key)
            if detected:
                st.success(f"找到 {len(detected)} 個已安裝模型！")
                st.session_state["local_models_list"] = detected
            else:
                st.warning("⚠️ 未偵測到模型，請確認服務已啟動。")

    cached_models = st.session_state.get("local_models_list", [])
    if cached_models and "本地" in provider:
        active_model = st.selectbox("選擇已安裝模型", cached_models)
    else:
        active_model = st.text_input("模型名稱 (Model Name)", value=default_model)

    st.markdown("---")

    # 5. 重置遊戲按鈕
    if st.button("🔄 開始新冒險 / 重置遊戲", use_container_width=True, type="secondary"):
        init_game_state(reset=True)
        st.rerun()

# ==========================================
# 核心互動邏輯：呼叫 AI DM
# ==========================================
def call_dm_agent(user_action: str):
    """將玩家行動發送給 AI DM 並更新遊戲狀態"""
    st.session_state.last_error = None
    
    # 記錄玩家訊息
    st.session_state.messages.append({"role": "user", "content": user_action})

    # 若使用離線演示
    if provider == "🎭 離線模擬 (免模型直接體驗)":
        dm_data = mock_dm_reply(user_action)
        apply_dm_result(dm_data)
        return

    # 構建對話歷史
    api_messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    status_summary = (
        f"[系統現況提示] 玩家當前血量: {st.session_state.hp}/{st.session_state.max_hp}，"
        f"當前地點: {st.session_state.location}，"
        f"背包物品: {', '.join(st.session_state.inventory) if st.session_state.inventory else '無'}。"
    )
    api_messages.append({"role": "system", "content": status_summary})

    for msg in st.session_state.messages:
        api_messages.append({"role": msg["role"], "content": msg["content"]})

    try:
        with st.spinner("🎲 AI 裁判正在擲骰判定命運並編織劇情..."):
            raw_response = chat_completion(
                base_url=active_base_url.strip(),
                api_key=active_api_key or "local-model",
                model=active_model.strip(),
                messages=api_messages,
                temperature=0.7
            )
            dm_data = parse_dm_response(raw_response)
            apply_dm_result(dm_data)
    except Exception as e:
        # 捕捉錯誤並存入 session_state，避免被 rerun 洗掉
        st.session_state.last_error = str(e)
        # 若最後一條是未得到回應的玩家訊息，暫時保留或提供重試機會

def apply_dm_result(dm_data: dict):
    hp_change = int(dm_data.get("hp_change", 0))
    new_hp = max(0, min(st.session_state.max_hp, st.session_state.hp + hp_change))
    st.session_state.hp = new_hp

    items_obtained = dm_data.get("items_obtained", [])
    if isinstance(items_obtained, list):
        for item in items_obtained:
            if item and item not in st.session_state.inventory:
                st.session_state.inventory.append(item)

    new_loc = dm_data.get("location")
    if new_loc:
        st.session_state.location = new_loc

    # 更新 3 個選項
    opts = dm_data.get("options", [])
    if not opts or len(opts) < 3:
        opts = [
            "仔細觀察四周的動靜與環境細節",
            "拔出武器，做好應對突發戰鬥的準備",
            "大膽採取出人意料的搞怪舉動"
        ]
    st.session_state.current_options = opts

    if st.session_state.hp <= 0:
        st.session_state.game_over = True

    st.session_state.messages.append({
        "role": "assistant",
        "content": dm_data.get("story", ""),
        "hp_change": hp_change,
        "items_obtained": items_obtained
    })

# ==========================================
# 主介面：劇情對話區
# ==========================================
st.title("🎲 TRPG 故事生成與 AI 裁判")
st.caption(f"目前引擎：`{provider}` ｜ 模型：`{active_model}`")

# 錯誤告警區（若上一輪連線失敗，直接在主要畫面醒目提示）
if st.session_state.last_error:
    st.error(f"### ⚠️ 連線 AI 裁判失敗！\n\n**詳細原因：**\n```\n{st.session_state.last_error}\n```")
    
    col_err1, col_err2 = st.columns([2, 1])
    with col_err1:
        st.info("💡 **排查指南：**\n1. 若使用 **Ollama**：請在 Windows 開啟 Ollama 或在終端機輸入：`ollama run llama3.2`\n2. 若您想先體驗遊戲畫面與選項功能，可在左側側邊欄選擇 **「🎭 離線模擬 (免模型直接體驗)」**。")
    with col_err2:
        if st.button("🔄 重新連線嘗試", type="primary", use_container_width=True):
            if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
                last_user_msg = st.session_state.messages.pop()["content"]
                call_dm_agent(last_user_msg)
                st.rerun()

# 若尚未開始冒險，顯示主題選擇與開場導引
if not st.session_state.game_started and len(st.session_state.messages) == 0:
    st.markdown("""
    ### ⚔️ 歡迎踏入冒險旅程！
    AI 裁判已就位。請選擇你的起始劇本，或自行輸入專屬背景：
    """)
    
    col1, col2, col3 = st.columns(3)
    start_action = None
    
    with col1:
        if st.button("🌲 經典奇幻：深入迷霧森林", use_container_width=True):
            start_action = "我是一位配備鐵劍的冒險者，站在灰燼鎮外的迷霧森林入口，準備踏上尋找失落神廟的旅程。"
    with col2:
        if st.button("🏰 地下迷宮：探索古老地牢", use_container_width=True):
            st.session_state.location = "古代地牢第一層入口"
            start_action = "我點燃火把，踏入散發著腐朽氣味的地下石造古牢，四周傳來滴水聲與不明生物的低吼。"
    with col3:
        if st.button("🍺 喧鬧酒館：打聽危險委託", use_container_width=True):
            st.session_state.location = "野豬與口哨酒館"
            start_action = "我推開嘈雜的酒館木門，找了個吧檯角落坐下，準備向酒保打聽最近高額賞金的委託。"

    custom_prologue = st.text_input("或者自訂開場行動／角色背景：", placeholder="例如：我是一名擅長隱形術的遊俠，潛入了哥布林盤據的廢棄礦坑...")
    if st.button("🚀 開始冒險", type="primary") and custom_prologue.strip():
        start_action = custom_prologue.strip()

    if start_action:
        st.session_state.game_started = True
        call_dm_agent(start_action)
        st.rerun()

else:
    # 渲染對話歷程
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            with st.chat_message("user", avatar="🛡️"):
                st.write(msg["content"])
        else:
            with st.chat_message("assistant", avatar="🧙‍♂️"):
                st.write(msg["content"])
                
                hp_c = msg.get("hp_change", 0)
                items = msg.get("items_obtained", [])
                
                tags = []
                if hp_c < 0:
                    tags.append(f'<span class="badge-hp-loss">🩸 受到傷害: {hp_c} HP</span>')
                elif hp_c > 0:
                    tags.append(f'<span class="badge-hp-gain">💚 恢復生命: +{hp_c} HP</span>')
                
                if items:
                    for it in items:
                        tags.append(f'<span class="badge-item">🎁 獲得: {it}</span>')
                
                if tags:
                    st.markdown(" ".join(tags), unsafe_allow_html=True)

    st.markdown("---")

    # ==========================================
    # 動態建議行動選項區 & 自訂輸入框
    # ==========================================
    if st.session_state.game_over:
        st.error("### 🪦 你的生命值歸零，冒險在此劃下句點...")
        st.caption("DM 微微合上筆記本，為你的英勇（或魯莽）嘆了一口氣。")
        if st.button("🔄 重新轉生，再次挑戰！", type="primary"):
            init_game_state(reset=True)
            st.rerun()
    else:
        st.write("#### 🎯 請決定您的下一步：")
        
        # 取得當前選項；若暫時無選項，提供保底引導選項
        opts = st.session_state.current_options
        if not opts:
            # 發生連線異常或開場等待時的保底備選方案
            opts = [
                "拔出武器，小心翼翼環顧四周",
                "點燃火把仔細檢查腳下的足跡與陷阱",
                "對著濃霧大喊一聲試探反應"
            ]

        col_a, col_b, col_c = st.columns(3)
        clicked_action = None

        with col_a:
            st.caption("🅰️ **認真／常規行動**")
            if st.button(opts[0], key="btn_opt_0", use_container_width=True):
                clicked_action = opts[0]
        with col_b:
            st.caption("🅱️ **策略／洞察行動**")
            if st.button(opts[1], key="btn_opt_1", use_container_width=True):
                clicked_action = opts[1]
        with col_c:
            st.caption("🅲 **有趣／奇策行動**")
            if st.button(opts[2], key="btn_opt_2", use_container_width=True):
                clicked_action = opts[2]

        # 自由輸入框
        typed_action = st.chat_input("或在此輸入自訂行動（例如：使用火把點燃蜘蛛網、嘗試跟地精商量...）")

        # 觸發玩家行動
        action_to_take = clicked_action or typed_action
        if action_to_take:
            call_dm_agent(action_to_take)
            st.rerun()

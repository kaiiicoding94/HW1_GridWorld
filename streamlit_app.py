import streamlit as st
import random

# ─── Page Config ──────────────────────────────────────────────
st.set_page_config(page_title="GridWorld — 策略評估與價值迭代", layout="centered")

# ─── Constants ────────────────────────────────────────────────
GAMMA = 0.9
THETA = 1e-6
STEP_REWARD = -1
GOAL_REWARD = 0
ACTIONS = ['up', 'down', 'left', 'right']
DELTAS = {'up': (-1, 0), 'down': (1, 0), 'left': (0, -1), 'right': (0, 1)}
ARROW_MAP = {'up': '↑', 'down': '↓', 'left': '←', 'right': '→'}


# ─── Algorithm Functions ─────────────────────────────────────
def next_state(r, c, action, n, obstacles):
    dr, dc = DELTAS[action]
    nr, nc = r + dr, c + dc
    if 0 <= nr < n and 0 <= nc < n and (nr, nc) not in obstacles:
        return nr, nc
    return r, c


def generate_random_policy(n, end, obstacles):
    pol = {}
    for r in range(n):
        for c in range(n):
            if (r, c) == end or (r, c) in obstacles:
                continue
            pol[(r, c)] = random.choice(ACTIONS)
    return pol


def policy_evaluation(n, end, obstacles, pol):
    V = {}
    for r in range(n):
        for c in range(n):
            if (r, c) in obstacles:
                continue
            V[(r, c)] = 0.0

    for _ in range(10000):
        delta = 0.0
        for r in range(n):
            for c in range(n):
                if (r, c) in obstacles or (r, c) == end:
                    continue
                action = pol.get((r, c))
                if action is None:
                    continue
                nr, nc = next_state(r, c, action, n, obstacles)
                reward = GOAL_REWARD if (nr, nc) == end else STEP_REWARD
                new_v = reward + GAMMA * V.get((nr, nc), 0.0)
                delta = max(delta, abs(new_v - V[(r, c)]))
                V[(r, c)] = new_v
        if delta < THETA:
            break
    return V


def value_iteration(n, end, obstacles):
    V = {}
    for r in range(n):
        for c in range(n):
            if (r, c) in obstacles:
                continue
            V[(r, c)] = 0.0

    for _ in range(10000):
        delta = 0.0
        for r in range(n):
            for c in range(n):
                if (r, c) in obstacles or (r, c) == end:
                    continue
                old_v = V[(r, c)]
                best_v = float('-inf')
                for action in ACTIONS:
                    nr, nc = next_state(r, c, action, n, obstacles)
                    reward = GOAL_REWARD if (nr, nc) == end else STEP_REWARD
                    v = reward + GAMMA * V.get((nr, nc), 0.0)
                    if v > best_v:
                        best_v = v
                V[(r, c)] = best_v
                delta = max(delta, abs(best_v - old_v))
        if delta < THETA:
            break

    pol = {}
    for r in range(n):
        for c in range(n):
            if (r, c) in obstacles or (r, c) == end:
                continue
            best_action, best_v = None, float('-inf')
            for action in ACTIONS:
                nr, nc = next_state(r, c, action, n, obstacles)
                reward = GOAL_REWARD if (nr, nc) == end else STEP_REWARD
                v = reward + GAMMA * V.get((nr, nc), 0.0)
                if v > best_v:
                    best_v = v
                    best_action = action
            pol[(r, c)] = best_action
    return V, pol


# ─── Custom CSS ───────────────────────────────────────────────
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
    }
    h1 {
        background: linear-gradient(90deg, #00d2ff, #7b2ff7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        font-size: 2.5rem !important;
    }
    .subtitle {
        text-align: center;
        color: #999;
        font-size: 0.95rem;
        margin-bottom: 20px;
    }
    .grid-table {
        margin: 0 auto;
        border-collapse: collapse;
    }
    .grid-table td {
        width: 72px;
        height: 72px;
        text-align: center;
        vertical-align: middle;
        border: 1px solid rgba(255,255,255,0.15);
        font-size: 0.8rem;
        color: #fff;
        background: rgba(255,255,255,0.04);
        transition: all 0.2s;
    }
    .grid-table td:hover {
        background: rgba(123,47,247,0.2) !important;
    }
    .cell-start {
        background: linear-gradient(135deg, #43a047, #66bb6a) !important;
    }
    .cell-end {
        background: linear-gradient(135deg, #e53935, #ef5350) !important;
    }
    .cell-obs {
        background: linear-gradient(135deg, #616161, #9e9e9e) !important;
    }
    .arrow {
        font-size: 1.5rem;
        line-height: 1;
    }
    .val {
        font-size: 0.68rem;
        font-weight: 600;
        opacity: 0.9;
    }
    .param-box {
        text-align: center;
        color: #888;
        font-size: 0.82rem;
        margin-top: 16px;
    }
    .param-box code {
        background: rgba(255,255,255,0.1);
        padding: 2px 8px;
        border-radius: 4px;
    }
    div[data-testid="stHorizontalBlock"] {
        justify-content: center;
    }
</style>
""", unsafe_allow_html=True)


# ─── Session State Initialization ─────────────────────────────
if 'grid_start' not in st.session_state:
    st.session_state.grid_start = None
if 'grid_end' not in st.session_state:
    st.session_state.grid_end = None
if 'grid_obstacles' not in st.session_state:
    st.session_state.grid_obstacles = set()
if 'grid_phase' not in st.session_state:
    st.session_state.grid_phase = 'start'
if 'grid_policy' not in st.session_state:
    st.session_state.grid_policy = None
if 'grid_values' not in st.session_state:
    st.session_state.grid_values = None
if 'grid_mode' not in st.session_state:
    st.session_state.grid_mode = None
if 'grid_n' not in st.session_state:
    st.session_state.grid_n = 7


# ─── Header ──────────────────────────────────────────────────
st.markdown("# GridWorld")
st.markdown('<p class="subtitle">策略評估 ＆ 價值迭代 視覺化</p>', unsafe_allow_html=True)


# ─── Controls ────────────────────────────────────────────────
col1, col2, col3, col4, col5 = st.columns([1.2, 1, 1, 1, 1])

with col1:
    new_n = st.selectbox("網格大小 n", [5, 6, 7, 8, 9], index=[5,6,7,8,9].index(st.session_state.grid_n), label_visibility="collapsed")
    if new_n != st.session_state.grid_n:
        st.session_state.grid_n = new_n
        st.session_state.grid_start = None
        st.session_state.grid_end = None
        st.session_state.grid_obstacles = set()
        st.session_state.grid_phase = 'start'
        st.session_state.grid_policy = None
        st.session_state.grid_values = None
        st.session_state.grid_mode = None
        st.rerun()

n = st.session_state.grid_n
max_obs = n - 2

with col2:
    if st.button("🎲 隨機策略", use_container_width=True):
        if st.session_state.grid_start and st.session_state.grid_end:
            pol = generate_random_policy(n, st.session_state.grid_end, st.session_state.grid_obstacles)
            st.session_state.grid_policy = pol
            st.session_state.grid_values = None
            st.session_state.grid_mode = 'random'
            st.rerun()

with col3:
    if st.button("📊 策略評估", use_container_width=True):
        if st.session_state.grid_policy:
            V = policy_evaluation(n, st.session_state.grid_end, st.session_state.grid_obstacles, st.session_state.grid_policy)
            st.session_state.grid_values = V
            st.session_state.grid_mode = 'eval'
            st.rerun()

with col4:
    if st.button("⚡ 價值迭代", use_container_width=True):
        if st.session_state.grid_start and st.session_state.grid_end:
            V, pol = value_iteration(n, st.session_state.grid_end, st.session_state.grid_obstacles)
            st.session_state.grid_values = V
            st.session_state.grid_policy = pol
            st.session_state.grid_mode = 'optimal'
            st.rerun()

with col5:
    if st.button("🔄 重置", use_container_width=True):
        st.session_state.grid_start = None
        st.session_state.grid_end = None
        st.session_state.grid_obstacles = set()
        st.session_state.grid_phase = 'start'
        st.session_state.grid_policy = None
        st.session_state.grid_values = None
        st.session_state.grid_mode = None
        st.rerun()


# ─── Instruction Message ─────────────────────────────────────
phase = st.session_state.grid_phase
if st.session_state.grid_mode == 'random':
    st.info("🎲 已生成隨機策略（箭頭顯示於各格子）")
elif st.session_state.grid_mode == 'eval':
    st.info("📊 策略評估完成，V(s) 已顯示")
elif st.session_state.grid_mode == 'optimal':
    st.success("⚡ 價值迭代完成，最佳策略與 V(s) 已顯示")
elif phase == 'start':
    st.warning("👆 請點擊下方格子設定 **起點**（綠色）")
elif phase == 'end':
    st.warning("👆 請點擊下方格子設定 **終點**（紅色）")
elif phase == 'obs':
    remaining = max_obs - len(st.session_state.grid_obstacles)
    st.warning(f"👆 請點擊設定 **障礙物**（灰色），還可設定 {remaining} 個")
elif phase == 'done':
    st.success("✅ 設定完成！請使用上方按鈕生成策略")


# ─── Status Tags ─────────────────────────────────────────────
c1, c2, c3 = st.columns(3)
with c1:
    if st.session_state.grid_start:
        st.markdown(f"🟢 起點：`{st.session_state.grid_start}`")
    else:
        st.markdown("🟢 起點：未設定")
with c2:
    if st.session_state.grid_end:
        st.markdown(f"🔴 終點：`{st.session_state.grid_end}`")
    else:
        st.markdown("🔴 終點：未設定")
with c3:
    st.markdown(f"🚧 障礙物：`{len(st.session_state.grid_obstacles)} / {max_obs}`")


# ─── Grid Display (HTML table) ────────────────────────────────
cur_policy = st.session_state.grid_policy
cur_values = st.session_state.grid_values

html = '<table class="grid-table">'
for r in range(n):
    html += '<tr>'
    for c in range(n):
        cell_class = ''
        content = ''
        if st.session_state.grid_start == (r, c):
            cell_class = 'cell-start'
            if cur_policy and (r, c) in cur_policy:
                content = f'<div class="arrow">{ARROW_MAP[cur_policy[(r,c)]]}</div>'
            else:
                content = '<div class="arrow">🟢</div>'
            if cur_values and (r, c) in cur_values:
                content += f'<div class="val">V={round(cur_values[(r,c)], 2)}</div>'
        elif st.session_state.grid_end == (r, c):
            cell_class = 'cell-end'
            content = '<div class="arrow">🔴</div>'
        elif (r, c) in st.session_state.grid_obstacles:
            cell_class = 'cell-obs'
            content = '<div class="arrow">🚧</div>'
        else:
            if cur_policy and (r, c) in cur_policy:
                content = f'<div class="arrow">{ARROW_MAP[cur_policy[(r,c)]]}</div>'
            if cur_values and (r, c) in cur_values:
                content += f'<div class="val">V={round(cur_values[(r,c)], 2)}</div>'
        html += f'<td class="{cell_class}">{content}</td>'
    html += '</tr>'
html += '</table>'

st.markdown(html, unsafe_allow_html=True)

# ─── Click Grid (buttons) ────────────────────────────────────
st.markdown("---")
st.markdown("##### 👇 點擊格子進行設定")

for r in range(n):
    cols = st.columns(n)
    for c in range(n):
        with cols[c]:
            label = f"({r},{c})"
            if st.session_state.grid_start == (r, c):
                label = "🟢"
            elif st.session_state.grid_end == (r, c):
                label = "🔴"
            elif (r, c) in st.session_state.grid_obstacles:
                label = "🚧"

            if st.button(label, key=f"btn_{r}_{c}", use_container_width=True):
                if phase == 'start':
                    st.session_state.grid_start = (r, c)
                    st.session_state.grid_phase = 'end'
                    st.session_state.grid_policy = None
                    st.session_state.grid_values = None
                    st.session_state.grid_mode = None
                    st.rerun()
                elif phase == 'end':
                    if (r, c) != st.session_state.grid_start:
                        st.session_state.grid_end = (r, c)
                        st.session_state.grid_phase = 'obs' if max_obs > 0 else 'done'
                        st.session_state.grid_policy = None
                        st.session_state.grid_values = None
                        st.session_state.grid_mode = None
                        st.rerun()
                elif phase == 'obs':
                    if (r, c) != st.session_state.grid_start and (r, c) != st.session_state.grid_end:
                        obs = st.session_state.grid_obstacles
                        if (r, c) in obs:
                            obs.discard((r, c))
                        elif len(obs) < max_obs:
                            obs.add((r, c))
                        if len(obs) >= max_obs:
                            st.session_state.grid_phase = 'done'
                        st.session_state.grid_policy = None
                        st.session_state.grid_values = None
                        st.session_state.grid_mode = None
                        st.rerun()


# ─── Parameters ──────────────────────────────────────────────
st.markdown(
    '<div class="param-box">參數：<code>γ = 0.9</code>　<code>step reward = −1</code>　<code>goal reward = 0</code>（terminal）</div>',
    unsafe_allow_html=True
)

# HW1: GridWorld 開發對話紀錄

**日期**：2026-03-24  
**專案**：GridWorld Flask 網頁應用程式

---

## 使用者需求

### HW1-1：網格地圖開發（60%）
- 開發 n×n 網格地圖（n = 5–9）
- 滑鼠點擊設定起點（綠色）、終點（紅色）、障礙物（灰色，n-2 個）

### HW1-2：策略顯示與價值評估（40%）
- 顯示隨機生成行動（↑↓←→ 箭頭）
- 使用策略評估推導 V(s)

### HW1-3：價值迭代推導最佳政策
- 實現價值迭代算法
- 顯示最佳策略與 V(s)

---

## 實作過程

### 1. 規劃階段

建立了實作計畫，包含以下架構：

- **後端**：`app.py`（Flask）
  - `GET /` — 主頁面
  - `POST /api/random_policy` — 隨機策略生成
  - `POST /api/policy_evaluation` — 策略評估
  - `POST /api/value_iteration` — 價值迭代
- **前端**：`templates/index.html`（HTML/CSS/JS 單頁應用）

**演算法參數**：

| 參數 | 值 |
|------|-----|
| 折扣因子 γ | 0.9 |
| 步驟獎勵 | -1 |
| 目標獎勵 | 0（終止狀態）|
| 收斂閾值 θ | 1e-6 |

---

### 2. 建立 Flask 後端 — `app.py`

建立了 `app.py`，包含：

- **`_next_state()`**：計算下一個狀態，撞牆或障礙物則留在原地
- **`/api/random_policy`**：為每個自由格子隨機分配一個動作
- **`/api/policy_evaluation`**：迭代策略評估（Bellman 更新），直到收斂
- **`/api/value_iteration`**：價值迭代（Bellman 最優更新），提取貪婪策略

---

### 3. 建立前端 — `templates/index.html`

建立了具有以下特色的單頁應用：

- **視覺設計**：漸層背景、glassmorphism 風格、動態 hover 效果
- **控制項**：網格大小選擇器（5–9）、四個功能按鈕
- **互動流程**：
  1. 第一次點擊 → 設定起點（綠色）
  2. 第二次點擊 → 設定終點（紅色）
  3. 後續點擊 → 設定障礙物（灰色，最多 n-2 個）
- **顯示**：箭頭（策略）+ V(s) 數值

---

### 4. 環境設定

由於系統未安裝 Python 和 Git，透過 `winget` 安裝了：

- **Python 3.12.10**
- **Flask 3.1.3**（及相關套件）
- **Git 2.53.0**

---

### 5. 驗證測試

使用瀏覽器進行了完整測試：

#### ✅ 網格設定
- 點擊設定起點 (0,0) → 綠色
- 點擊設定終點 (6,6) → 紅色
- 點擊設定 4 個障礙物 → 灰色

#### ✅ 隨機策略
- 所有自由格子顯示隨機箭頭（↑↓←→）

#### ✅ 策略評估
- 計算 V(s) 值並顯示於每個格子
- 隨機策略下大部分格子 V ≈ -10

#### ✅ 價值迭代
- 最佳策略箭頭正確指向目標方向，繞過障礙物
- V(s) 值從目標向外遞減（-1, -1.9, -2.71, ...）

---

### 6. 上傳至 GitHub

成功推送至：https://github.com/kaiiicoding94/HW1_-GridWorld

```
git init
git add app.py templates/
git commit -m "HW1: GridWorld Flask application - grid map, policy evaluation, value iteration"
git branch -M main
git remote add origin https://github.com/kaiiicoding94/HW1_-GridWorld.git
git push -u origin main
```

---

## 專案檔案結構

```
HW1_ GridWorld/
├── app.py                  # Flask 後端（路由 + RL 演算法）
└── templates/
    └── index.html          # 前端介面（HTML/CSS/JS）
```

---

## 如何執行

```bash
cd "c:\Users\Kai\Desktop\HW1_ GridWorld"
python app.py
# 瀏覽器開啟 http://127.0.0.1:5000
```

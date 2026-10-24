# aniGamerPlus 優化與安全審核

審核日期：2026-10-25。比較基準為提交 `6c5e7221bb36f8d13e71822dbdea6560fe397a80`。

本次針對 Python 下載流程、Dashboard API、片單與縮圖處理、網頁快取及發佈工作流程進行程式碼審核與離線回歸測試。以下記載已修復問題、可重現的效能證據和仍存在的限制。沒有使用實際帳戶下載影片，也未將本機設定或帳戶資料收錄到報告。

## 已修復問題

| 範圍 | 原有問題及影響 | 修復方式 |
| --- | --- | --- |
| 縮圖記憶體 | EXIF 方向處理與 RGB 轉換發生在縮放之前，大圖片會產生多份完整尺寸的像素緩衝區。Pillow 預設的圖片大小警告門檻也高於縮圖所需。 | `Dashboard/thumbnail_cache.py` 先檢查 3,200 萬像素上限，再縮放至最長邊 960 像素，最後處理方向及 RGB。保留調色盤圖片的濾鏡品質、原子發佈及產出解碼驗證。 |
| 片單抓取上限 | 上游 HTML 的最大頁數直接控制完整抓取迴圈，異常巨大頁碼可造成長時間請求與背景工作佔用。 | `Catalog.total_pages()` 拒絕超過 1,000 頁及異常巨大數字；呼叫端依既有錯誤處理保留前一份快取，不將截短結果當成完整片單。 |
| OP 時間衝突判定 | 同集有 n 份錄影時，所有候選區間兩兩比較，工作量為 O(n²)。 | `OpeningSkip.anime_skip_op()` 改以起點與終點的最大值減最小值判定，保持原本 3 秒容差，工作量降為 O(n)。 |
| HLS 分片及合併 | 每片建立作業系統執行緒；失敗可能留下尚在寫入的執行緒；HTTP 錯誤內容或 ffmpeg 部分輸出可能被當成正常結果。 | `Anime.py` 使用最多 5 個固定工作執行緒、同步進度計數、失敗取消及完整 join，拒絕失敗／空分片，檢查 ffmpeg 返回碼、錯誤訊息與產出檔案後才進入發佈。 |
| 影片發佈 | 搬移前先刪除舊影片，跨磁碟複製或磁碟滿可能造成資料遺失。 | 同卷原子替換；跨卷與強制複製先在目的端暫存、驗證大小與同步結果，再原子替換，成功後才清除來源。兩種下載模式共用此流程。 |
| HLS 外部輸入 | 以檔名字串片段取代完整 URI 驗證，可能將不支援的路徑或額外資源標籤帶入本機清單。 | 下載器與 Dashboard 限定可接受的分片檔名；下載器驗證金鑰與額外 URI 標籤，依整行 URI 本地化，避免取代到 query 內相似字串。 |
| 請求及索引生命週期 | 單次附加 HTTP header 修改共用字典；curl 指紋請求例外與 JSON 解碼不一致；短期 session 未明確關閉；影片索引直接覆寫且可並行逆序發佈。 | 複製 header、統一 JSON 解碼／錯誤處理、關閉已緩衝回應的 session，以鎖序列化片庫快照並透過原子寫入發佈。 |
| Dashboard 請求邊界 | 跨來源瀏覽器可觸發部分狀態修改；超量請求例外可能被表單／JSON 的廣泛捕捉吞掉；異常投放票券及舊中文密碼可能觸發例外。 | 檢查瀏覽器來源及狀態修改路由、讓請求大小例外繼續傳遞、嚴格驗證票券格式、以 UTF-8 bytes 進行密碼常數時間比較。 |
| 舊密碼相容流程 | 舊明文密碼驗證與重設同時發生時，遷移分支可能發出重設後的 token。 | 交易中重驗最新密碼；帳戶已移除或驗證失敗時拒絕登入。正式資料載入通常已先轉換為雜湊，這是相容／遷移分支修復，不代表一般雜湊帳戶可直接被接管。 |
| Dashboard 鎖與連線 | 動態鍵的鎖永久留在字典，且短期 curl session 缺少明確釋放。 | 鎖改用弱參考容器；活躍或等待的呼叫仍保有強參考，同一鍵的互斥性不變。請求結束即關閉 session。 |
| 網頁與 PWA | 設定資料尚未回來便渲染；觀看紀錄反覆解析及建立索引；失敗查詢重複佔用名額；離線快取包含個人化 HTML。 | 收到設定後才渲染，快取名稱與觀看索引並在資料改變時失效，限制失敗重試頻率；PWA 改用不含帳戶資料的離線頁，清除自身舊版本快取。 |
| Release workflow | 使用者輸入的版本字串直接插入 shell 程式。 | 改經環境變數傳遞，並在產生發佈檔名之前驗證版本格式。 |
| Docker 建置 | `COPY . .` 未排除本機帳戶資料、私鑰與稽核工具；未固定 Python 主版本會碰到自動登入套件不支援的新版本。 | 補齊 `.dockerignore`，固定使用與 CI 一致的 Python 3.11，關閉安裝非必要推薦套件。Docker 未在本機建置驗證。 |
| 前端依賴 | jQuery 3.4.0 包含已知 HTML 處理 XSS 問題。 | 升級相容的 jQuery 3.7.1，更新所有模板；監控頁讓 layui 共用已載入的新版 jQuery，不再下載第二份舊 jQuery。官方下載檔案通過 SHA-256 SRI 比對，並執行既有網頁回歸。 |

## 可重現的縮圖效能量測

量測程式：[tools/benchmark_thumbnail.py](../tools/benchmark_thumbnail.py)。在專案根目錄使用 PowerShell 執行：

```powershell
.\.venv\Scripts\python.exe tools\benchmark_thumbnail.py --baseline-ref 6c5e7221bb36f8d13e71822dbdea6560fe397a80 --runs 3 --width 6000 --height 4000
```

腳本從指定 Git 提交讀取舊縮圖模組，與目前工作目錄的模組分別執行。輸入為合成的 6000 × 4000、RGB、navy 純色 JPEG；圖片建立不計入子程序。每次編碼都使用全新的 Python 子程序，計時範圍包含圖片處理、WebP 編碼、解碼驗證及原子發佈，排除模組載入。檔案只寫入暫存目錄，結束後刪除。輸出 JSON 包含 Python、Pillow、作業系統、完整基準提交與每次樣本。

在 Windows、Python 3.11.9、Pillow 13.0.0 的一次三輪執行結果：

| 版本 | 三次耗時（秒） | 耗時中位數（秒） | 三次程序峰值 working set（MiB） | 記憶體中位數（MiB） |
| --- | --- | ---: | --- | ---: |
| 基準提交 | 0.586070、0.563475、0.893821 | 0.586070 | 302.293、302.121、302.176 | 302.176 |
| 本次修改 | 0.530359、0.320529、0.264345 | 0.320529 | 59.996、60.047、59.949 | 59.996 |

這個樣本的程序峰值 working set 中位數降低約 **80.1%**。兩版每次輸出均為 1,172 bytes。較早在 Pillow 12.3.0 使用相同輸入與方法的三輪量測，中位數為 303.223 → 61.168 MiB，耗時為 0.300266 → 0.235386 秒。

記憶體數字使用 Windows `GetProcessMemoryInfo().PeakWorkingSetSize`，包含 Python 與 Pillow 的程序開銷，不是只有像素緩衝區。此結果來自單一純色 JPEG，不能推估整體下載速度、全部圖片格式或多人使用時的伺服器吞吐量。耗時受 CPU 排程、同機工作與快取影響明顯，因此不將此單一樣本的時間差當成產品層級加速承諾。腳本在 Linux／macOS 改回報 `ru_maxrss`，不同作業系統的記憶體指標不應直接混比。

## OP 比對的操作次數證據

新增回歸測試 `tests/test_catalog_hardening.py::test_duplicate_opening_recordings_require_linear_comparisons` 使用 1,000 筆相同錄影，對時間戳減法計數。另將同一組資料交給基準提交的 `OpeningSkip.py` 及目前版本：

| 版本 | 時間戳相減次數 | 回傳區間 |
| --- | ---: | --- |
| 基準提交 | 2,001,000 | `(100, 190)` |
| 本次修改 | 1,002 | `(100, 190)` |

新測試同時檢查恰為 3 秒及略超過 3 秒的邊界，避免用效能改善換掉原本保守的衝突判定。測試命令：

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_catalog_hardening.py tests\test_opening_skip.py tests\test_dashboard_loading.py -q
```

## 下載流程獨立複審

分片效能回歸以 120 片、併發數 3 驗證執行緒建立數：由每片建立一條的 120 條改為共用 3 條，全部分片仍會下載與合併。這是執行緒建立成本降低，不代表網路下載速度提升 40 倍。

瀏覽器回歸另外使用 2,000 筆名稱資料，2,000 次查詢只解析一次 JSON；資料改變後可立即讀到新名稱。建立觀看索引後連續查詢 1,000 張卡片，不再重掃觀看紀錄；更名或刪除紀錄會使索引失效。這些測試比較實際解析／掃描次數，沒有使用易受硬體影響的固定毫秒門檻。

複審曾指出新的 worker `join()` 在 `segment_max_retry=-1` 時可能永遠等待：一片已失敗，但另一片仍在無限網路重試。後續已加上 `cancel_event`，每輪請求及取得回應後檢查取消，使用 `Event.wait(3)` 取代分片的不可取消重試等待。`test_sibling_failure_interrupts_unlimited_network_retries` 實際經過請求重試函式，以離線 Session 模擬兩片分別持續連線失敗與回傳 503，確認所有工作執行緒能結束。

取消訊號不會強制中止已開始的底層 HTTP 呼叫；仍須等待它回應或逾時，才可安全 join。如此避免上一輪尚在寫入的分片與下一輪重試互相覆寫。現有 HTTP timeout 是單次請求設定，不代表整個下載有固定總時限。

索引更新的鎖涵蓋讀取、建立及發佈快照，避免較舊快照最後覆蓋較新快照；原子檔案替換可避免讀者看到半份 JSON。這是單一程序內的序列化，沒有宣稱跨多程序寫入的協調。`Config.bahamut_request` 的 session 關閉適用於目前使用的完整緩衝回應；若新增 `stream=True` 的使用者，須另行設計串流回應與 session 的生命週期。

## HLS 相容性與安全邊界

目前分片模式支援動畫瘋既有的 AES-128、單一金鑰與獨立 MPEG-TS 分片，分片路徑必須符合 `media_b[A-Za-z0-9_.-]+\.ts`，可附 query；下載時保留遠端 query，交給 ffmpeg 的本機清單移除 query，保留金鑰的 IV。金鑰內容必須恰為 16 bytes。

這不是通用 HLS 實作。多金鑰輪替、`METHOD=NONE`、fMP4／`EXT-X-MAP`、絕對或子目錄分片 URI、同檔重複 URI 的 byte-range 清單不在此分片模式的支援範圍。遇到無法安全處理的清單會拒絕，不能承諾所有合法 HLS 格式均可下載。舊實作也未完整處理這些格式，不應為兼容未驗證格式而放寬路徑驗證。

本次圖片像素上限限制的是解碼記憶體，不是網路回應的位元組數。外部封面網址的來源限制、重新導向與回應長度尚未因此獲得完整保護；不應把圖片檢查描述成完整 SSRF 或網路資源耗盡防護。Dashboard 的瀏覽器來源檢查也不取代帳戶權限、網路存取限制與正確的反向代理設定。

ffmpeg 失敗或回報缺片時，不會以其部分輸出取代舊影片。最終發佈也已加入同卷原子替換與跨卷暫存複製；失敗注入測試涵蓋短拷貝、複製中斷、替換失敗與延遲磁碟滿。遠端掛載若沒有實作 `fsync`，會允許繼續發佈；檔案系統本身的原子性與耐久性仍由掛載服務決定，不能承諾所有外部儲存故障均無資料損失。

CSRF 檢查依照 ASGI 已解碼路徑與 `root_path` 邊界處理，覆蓋 `/agp` 等子路徑部署。反向代理應保留公開 Host，並正確設定可信代理的 HTTPS 協定資訊；不會任意信任外部傳入的 Forwarded 標頭。原生 Flutter／CLI 沒有瀏覽器來源標頭的請求保持原有登入權限行為。此修復未加入新的登入限流或 session 到期政策。

## 整合驗證與依賴風險

本機使用 Python 3.11、Pillow 13.0.0、實際 Chromium 與 ffmpeg 7.1。`tests/test_media_pipeline.py` 由 ffmpeg 建立合成的 AES-128 HLS，經過真實分片下載方法、解密合併、檔案發佈，最後再次用 ffmpeg 解碼驗證；網路層只提供暫存目錄的測試素材。

最終完整離線測試結果：**514 passed、1 skipped，163.84 秒**。唯一跳過為未安裝且已從儲存庫移除的可選 Anime1.me 插件；播放器、HLS 與縮圖的 ffmpeg 測試皆有執行。59 個警告來自 TestClient 的 httpx 相容層與既有逐請求 cookie 用法的淘汰提示。

第一輪曾有一項圖片測試在 Windows 暫存目錄收到 `OSError: No space left on device`；受影響的 19 項測試重跑通過，再完整重跑取得上述 514 項通過結果，沒有用跳過測試掩蓋失敗。`git diff --check`、修改的 JavaScript 語法檢查及 `pip check` 均通過。Release shell 以 Git Bash 驗證：3 組合法版本接受、4 組路徑／shell 注入／換行輸入拒絕；沒有執行實際發佈工作流程。

依賴安裝後 `pip check` 通過。使用 `pip-audit 2.10.1` 掃描目前工作區虛擬環境：更新前 8 個套件、69 筆通報（56 個不同 ID），更新後只剩 Requests 2.32.5 的同一問題，被資料源重複列為 2 筆。

剩餘問題為 [CVE-2026-25645 / GHSA-gc5v-m9x4-r6x2](https://github.com/advisories/GHSA-gc5v-m9x4-r6x2)：`requests.utils.extract_zipped_paths()` 使用可預測的暫存檔路徑，修復版為 Requests 2.33.0。專案原始碼沒有直接呼叫此函式；通報說明一般 Requests HTTP 使用不受影響。自動登入依賴 `selenium-recaptcha-solver==1.9.1` 宣告 `requests<2.33.0`，因此此次更新至相容的 2.32.5，保留這個已知限制，未透過忽略依賴或降級 solver 來製造掃描全綠結果。待上游放寬限制，應升級 Requests 並重新驗證自動登入。

Pillow、lxml、Selenium、urllib3、certifi 等已升級；原虛擬環境的建置／觀測工具 setuptools、opentelemetry-api 亦已更新，但不將這兩個非應用直接依賴新增至 requirements。此結果是本次環境快照，不代表所有舊安裝或未來上游版本均無漏洞。

```powershell
python -m pip install -r requirements.txt -r requirements-dev.txt
python -m pytest tests -q -ra --ignore=tests/test_real_server_e2e.py
python -m pip check
python -m pip_audit --progress-spinner off
```

最後一條需另行安裝 `pip-audit`；因上述剩餘通報會回傳非零退出碼。完整離線測試需要 Chromium 和 ffmpeg；本次的 ffmpeg 僅置於忽略的 `.agpwork/bin`，未修改系統 PATH 或將執行檔提交。未執行會觸發真實帳號下載的 `test_real_server_e2e.py`。本機沒有 Flutter SDK 或 Docker，未宣稱已完成 Flutter 原生建置、裝置播放、容器建置或真實動畫瘋登入／下載驗證。

Anime1.me 插件在既有提交中已刻意移除，僅修正過期 README 與對應測試的可選插件判斷，沒有恢復該插件。Playwright 改為只在瀏覽器 fixture 載入，避免未安裝瀏覽器依賴時連後端測試也全部跳過。

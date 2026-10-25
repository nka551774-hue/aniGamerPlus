# aniGamerPlus 優化與安全審核

審核日期：2026-10-25。比較基準為提交 `6c5e7221bb36f8d13e71822dbdea6560fe397a80`。

本次針對 Python 下載流程、Dashboard API、片單與縮圖處理、網頁快取及發佈工作流程進行程式碼審核與離線回歸測試。以下記載已修復問題、可重現的效能證據和仍存在的限制。沒有使用實際帳戶下載影片，也未將本機設定或帳戶資料收錄到報告。

前面各節保留第一輪審核的環境與結果；2026-10-25 接手後的新修改、Flutter 驗證與更新限制記於文末「第二輪接手審核」。

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

## 第二輪接手審核

日期：2026-10-25；本輪比較基準為 `5427d47aea0666f20e6448f32c92500dc989fc4e`。接手時已有尚未完成的 staged 修正與三份 deep regression 測試；首次執行為 **32 passed、19 failed**，因此先保留既有意圖，再逐項重現與完成。

### 專案結構與資料流

| 範圍 | 責任與本輪檢查邊界 |
| --- | --- |
| `aniGamerPlus.py`、`Anime.py` | CLI／排程／手動任務、SQLite 狀態、HLS 分片、ffmpeg 合併及檔案發佈。確認重試、同集並行與失敗清理沒有互相覆寫。 |
| `Config.py`、`Danmu.py` | 設定、限流／鎖、網路 Session、原子寫入與 ASS 產生。確認例外不會耗盡鎖、不會污染共用過濾設定或毀掉舊字幕。 |
| `Dashboard/Server.py` | FastAPI 權限與帳戶儲存、媒體 Range／快取、HLS 回源。以 TestClient、loopback HTTP 與失敗注入檢驗協定及儲存錯誤。 |
| `Catalog.py`、`OpeningSkip.py`、`Dashboard/thumbnail_cache.py` | 片單、片頭時間比對與縮圖；沿用第一輪優化，完整測試再次覆蓋。 |
| `Dashboard/templates`、`Dashboard/static` | 網頁播放、片庫與 PWA；完整 Chromium 測試覆蓋播放器及網頁行為。 |
| `flutter_app/lib/src/api`、`state` | 原生客戶端 API、帳戶、下載狀態與 isolate 影片快取；新增伺服器／帳戶切換與實際 loopback 續傳測試。 |
| `flutter_app/lib/src/pages`、`widgets`、`packages` | UI、播放器與原生平台橋接；執行既有 widget 測試與靜態分析，未宣稱實機原生外掛已驗證。 |
| `tests`、`flutter_app/test`、`.github/workflows` | 後端／網頁／Flutter 回歸與 CI；保留真實帳戶測試的獨立執行邊界，不讀取本機帳戶內容。 |

### 本輪修復與實際行為

| 問題 | 結果 |
| --- | --- |
| 同集兩個 Anime 實例共用暫存檔；失敗重試殘留上輪成功狀態與分類目錄 | 單程序以集數共用鎖，重試前清理狀態並從片庫根重新分類。8 個並行實例的測試觀察到下載區段最大並行數為 1。 |
| 下載結果依四捨五入後 5 MB 門檻判定，短影片可能被當失敗 | 以實際發佈成功旗標與非空檔案為準；舊外部 Anime-like 介面保留一致的 5 MB fallback。失敗合併不發送完成通知。 |
| SQLite commit／close 例外可能永久占用 gate | statement 成功後才 commit；cursor／connection 清理各自有 finally，最外層一定釋放 gate。 |
| 帳戶 JSON 損毀／無法讀取可能重建預設使用者；磁碟同步錯誤被忽略 | 僅首次檔案不存在才初始化；損毀、重複帳號及讀寫故障回 503 並保留原檔，保留未知頂層 metadata。ENOSPC／EIO 不再當作成功同步。 |
| 彈幕解析失敗先清空舊 ASS，線上關鍵字污染共用列表或被當作 regex | 完整生成後才原子發佈，複製設定列表，線上關鍵字做 literal escape；使用者自行設定的 regex 保持原意。 |
| If-Range 被忽略、ETag 沒引號、日期條件蓋過不匹配的 ETag、巨大 Range 整數回 500 | 檔案替換回 200 讓客戶端重抓；標準 ETag／弱比較／清單／wildcard 正確處理，If-None-Match 優先；不合理 Range 回 416。 |
| HLS 重導向後基底錯誤、相對路徑拼接錯誤、非零媒體序號遺失 | 依最終播放清單 URL 做標準 URL resolution，保留媒體序號與既有 IV，拒絕 HTTP(S) 以外的資源 scheme。 |
| 同時索取金鑰重複回源；短暫解析失敗被快取半小時 | 8 個同時金鑰請求實際只回源 1 次；失敗解析退避改為 30 秒，成功解析仍保留原 30 分鐘。金鑰必須為 16 bytes。 |
| 回源完整緩衝沒有位元組限制 | libcurl callback 在接收解壓後 bytes 時限制大小，超量立即中止。一般回應 16 MiB、playlist 2 MiB、key 16 bytes、segment 32 MiB；identity／gzip／chunked 均有 loopback 測試。 |
| Windows 非 ANSI 專案路徑讓 curl_cffi 載入 CA bundle 就失敗 | 只在必要時將公開 CA 憑證複製至程序私有暫存目錄，沿用原憑證內容及 TLS 驗證；程序結束清理，不複製帳戶資料。 |
| Flutter 換伺服器仍帶舊 token、舊請求回來污染新帳戶快取、晚到登入／登出互蓋 | 切換上下文時失效 pending 結果與 memo；以登入請求序號保留最新登入；切換伺服器同時清除持久化 token 與帳戶觀看狀態。 |
| Flutter 416 直接視為完成，206 偏移／總長度未驗證 | 驗證 Content-Range 與實際長度後才發佈；續傳記錄來源 URL 與 validator，送 If-Range。收到完整 200 重新下載，舊格式沒有 validator 的 Dart 前景部分檔安全地從頭重抓。iOS URLSession 續傳格式未修改。 |
| 影片快取探測可能整集下載一次、上游錯誤範圍進入快取 | 1-byte probe 不符就取消，後續 Range 帶 If-Range 並驗證 offset／total／長度；錯誤資料不留在快取。 |

金鑰請求 8 → 1 與同集互斥是操作次數／正確性的證據；本輪沒有隔離其他專案建置進行產品吞吐量測，因此不新增整體效能百分比。前面的縮圖量測屬第一輪歷史結果。

### 本輪驗證與限制

Python 3.11 完整離線套件已通過 **565 passed、1 skipped，205.69 秒**，唯一跳過仍為已移除的可選 Anime1.me 插件。之後新增 3 個針對小型成功影片、同集 8 執行緒互斥與 Unicode CA 的測試；`test_core_deep_regressions.py` 單獨 **18 passed**。複審另外發現 curl_cffi 會忽略 callback 回傳的普通短長度（含 0），已改用 `CURL_WRITEFUNC_ERROR`；新測試讓 loopback 上游逐塊傳送 64 MiB，確認超量後 5 秒內斷線且未傳完整份，串流套件 **20 passed，9.11 秒**。這是完整套件及後續增量驗證，沒有把次數相加當成單次結果。真實 ffmpeg 合成 HLS、解密與 Chromium 網頁測試均有執行。`pip check` 與 `git diff --check` 通過。

主代理複審後，以所有最終程式與新增測試再次完整執行：**569 passed、1 skipped、61 warnings，143.98 秒**。唯一跳過仍是可選 Anime1.me 插件；警告為既有相依套件淘汰提示。此結果涵蓋最後的 libcurl 中止修復與新增回歸。

Flutter 使用本輪準備的 **Flutter 3.47.8 / Dart 3.13.7**。SDK 釘選的 matcher、meta、test_api、vector_math 四個間接依賴隨 `pub get` 更新；沒有全面升級應用依賴。Unicode 路徑在此 SDK 的分析伺服器觸發 LSP 長度解析錯誤，以 Windows `subst` 將整個儲存庫映射到暫時 ASCII 磁碟路徑後驗證同一批檔案，保留 `../tests/fixtures` 相對位置。

最終 `flutter analyze --no-fatal-infos` 回報 **No issues found**；`flutter test` 完整 **376 passed，58 秒**；停用更新器的 AAB 組態另 **2 passed**。首次映射僅包含 flutter_app，造成外層測試素材不可見，修正為整個儲存庫後完整重跑通過；沒有移除測試或放寬斷言。新增下載測試的清理也已等待工作完成再刪除暫存目錄。

```powershell
$env:PATH = (Join-Path $PWD '.agpwork\bin') + ';' + $env:PATH
.\.venv\Scripts\python.exe -m pytest tests -q -ra --ignore=tests/test_real_server_e2e.py
.\.venv\Scripts\python.exe -m pytest tests/test_core_deep_regressions.py -q
# 以下於 flutter_app/，使用 Flutter SDK 執行
flutter analyze --no-fatal-infos
flutter test
flutter test --dart-define=APP_UPDATER=false test/app_updater_build_test.dart
```

仍未執行真實動畫瘋帳號登入／下載、Android/iOS release build、實體裝置播放或 Docker 建置；上面的離線測試不等於這些環境已驗證。第一輪記載的 Requests 相依上限仍存在，本輪沒有為消除通報而強行放寬 solver 約束。HLS proxy 的 URI 相容修正不代表全面 SSRF 防護，也沒有新增跨程序檔案互斥保證。

Windows CA 路徑相容處理仍需要系統暫存目錄可由目前 ANSI code page 表示；若使用者名稱與 TEMP 本身也不可表示，會保留錯誤而不關閉 TLS 驗證，需將 TEMP 設至可表示且可寫的目錄。憑證副本於本程序中快取，更新信任憑證後應重新啟動程式。

## 第三輪下載與播放交叉檢查

日期：2026-10-25；基準提交 `25e372f`。本輪沿下載重試、HLS 時間線、帳戶切換及原生客戶端續傳流程檢查，未讀取實際帳戶檔、執行真實服務下載或修改相依套件。

| 可重現問題 | 修復與回歸證據 |
| --- | --- |
| 本地 EVENT HLS 將來源 `MEDIA-SEQUENCE:42` 重寫成 0，沒有顯式 IV 時會改變 AES 解密序號 | 保留來源序號，播放清單識別碼同時納入序號與金鑰行；既有零起點與顯式 IV 行為保持。 |
| 本地與回源代理解析器把多金鑰、未加密切換、MAP／BYTERANGE／DISCONTINUITY 當作可忽略標記，輸出語意不同的清單；非有限／負數時長可進入狀態 | 兩個解析器共用支援範圍檢查，明確拒絕無法保留的時間線及資源格式；拒絕 NaN、Infinity 及非正數時長。17 個新案例先全數失敗，修復後與既有 HLS／stream 測試共 75 項通過。 |
| 分片下載失敗後重試仍留有舊 `.ts`／`.part`；新金鑰到達時，HLS 的就緒掃描會把舊密文當成新分片 | 在發佈新清單／金鑰前，清除下載器命名契約範圍內的舊分片與部分檔案；保留其他檔案。失敗案例觀察到換鑰前兩個舊檔都存在，修復後均不存在；下載及真實 ffmpeg HLS 套件 34 項通過。 |
| 晚到的登出回應雖未覆蓋 API client 新 token，AppState 仍清空磁碟 token | AppState 在 Discord 清理、登出回應及本機清理後檢查上下文，保留已切換的伺服器或新登入。回歸以延遲的登出回應驗證記憶體與持久化 token 均保留。 |
| API client 已拒絕舊片庫回應，但 AppState 的例外分支仍用舊快取覆蓋新片庫；登出等待檔案路徑後可能刪到新帳戶觀看檔 | 在片庫請求的 await 邊界與錯誤處理、觀看檔刪除前確認上下文。兩個延遲回歸先分別重現新片庫變空與新檔遭刪，修復後通過。另保留舊觀看 API 回應被 client 擋住的正向控制，未重寫已正確的 client 行為。 |
| 切換來源／重抓時，先儲存新 validator 再截斷舊部分檔；當機後可能以新 validator 續接舊 bytes | 開始新的完整內容前先完成部分檔截斷，再發佈新來源與 validator。回歸在身分資料發佈通知時讀取磁碟，從原先仍有 `[1,2,3]` 改為空檔。 |
| 206 回應明確換了 ETag 仍可接到舊部分檔；416 只比長度而未確認檔案身分；影片快取同樣未核對回應 validator | 下載與 isolate 快取拒絕明確不符的 ETag／Last-Modified；416 完成判斷要求長度與原 validator 同時相符。測試覆蓋錯誤／缺少／正確 validator，並確認被拒絕的快取資料仍需重新回源。 |

此輪強化正確性與故障恢復，沒有新增整體下載速度或記憶體改善百分比。HLS 仍限定既有的單一 AES-128 金鑰與獨立 TS 模式；不支援格式會回報不可用，並未實作通用多金鑰或 fMP4 播放。清除重試殘留不等於多程序鎖，也不會撤回已送出的網路分片。Flutter 的 Range 改動適用 Dart 前景下載及影片快取；iOS URLSession 原生背景下載仍需裝置驗證。

第三輪最終完整離線驗證：Python **587 passed、1 skipped、61 warnings，154.54 秒**；唯一跳過仍為已移除的可選 Anime1.me 插件，警告仍來自既有相依套件淘汰提示。真實 ffmpeg 合成 HLS、解密、檔案發佈與 Chromium 網頁測試均有執行。Flutter 3.47.8 / Dart 3.13.7 完整 **386 passed，49 秒**；`flutter analyze --no-fatal-infos` 回報 **No issues found，40.4 秒**。這是納入複審兩項帳戶狀態修復及三項回歸後的完整重跑；未變更 Python，因此保留先前完整結果。`APP_UPDATER=false` 組態於追加帳戶修復前另 **2 passed**。`pip check` 和 `git diff --check` 通過。

Flutter 驗證沿用整個儲存庫的暫時 ASCII 磁碟映射，避免 Unicode SDK 分析問題且保留外層測試素材位置；驗證後移除映射。本輪仍未執行真實動畫瘋登入／下載、Android/iOS release build、實體裝置播放或 Docker 建置。驗證命令與第二輪相同；新的離線回歸已納入完整套件。

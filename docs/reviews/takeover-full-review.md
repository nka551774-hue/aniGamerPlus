# aniGamerPlus 接手審查與收尾紀錄

基準提交：`356c851dc26d8da9813d997f817e1e5b45bf5cee`。

本輪原本以全庫逐檔審查為目標；依使用者最後「直接先收尾」指示，於
2026-10-26 凍結範圍、完成已修改路徑的驗證並提交。這份紀錄不把搜尋、測試通過或
素材格式檢查冒充成第一方原始碼的逐行閱讀；凍結時仍未逐檔深讀的清單保留在
`docs/reviews/round4-file-review.md`。

## 已完成範圍

- Python 核心下載、設定遷移、使用者資料、登入、目錄、日誌與 Dashboard API 的主要
  資料流及錯誤路徑。
- Flutter 的伺服器／帳號 context、下載事件、投放、Discord presence、縮圖、電視遙控、
  影片匯出、格式化與共用封面元件。
- GitHub Actions、nightly 發佈腳本、PyInstaller 打包內容，以及 README 與本機 Codex
  環境設定。
- Flutter packages 與各平台原生整合 63 個檔案的靜態閱讀；Dashboard 前端重新分派批次
  實際完成 7/23 個檔案後即依收尾指示停止。
- 166 個 vendor／二進位／生成或 IDE 檔案依類型完成雜湊、格式解析、magic、圖片解碼、
  SQLite／XML／字型或本地引用閉合檢查；不宣稱不可讀 minified 或二進位內容已逐行審查。

## 本輪修正

- 原生下載事件現在同時驗證 `sn` 與 `fileName`，避免錯誤事件刪除另一集的合法影片或
  續傳資料。
- 帳號與伺服器切換加入 context version 防護，避免舊請求覆寫新帳號的 token、觀看紀錄、
  下載、投放、Discord、縮圖或匯出狀態。
- 縮圖 fallback 綁定伺服器 scope；切換伺服器後不會顯示舊伺服器晚到的封面。
- 修正 worker semaphore 洩漏、Telegram 失敗紀錄洩漏 token、FTP TLS 資料通道、全域
  socket timeout、HLS 金鑰長度與 SN 輸入驗證等可靠性／安全性問題。
- 發佈流程改為明確打包 runtime assets、先上傳再移動 nightly tag、保留各元件 release
  notes，並避免誤帶整個工作樹或無關 `notes.md`。
- 修正 Dart 與 JavaScript 雜湊不一致、Unicode grapheme 縮寫、超大集數格式化及 README
  設定範例。

## 最終驗證

- Python：`621 passed, 1 skipped`；唯一略過項目是未安裝的可選 Anime1.me 外掛。
- Flutter analyze：`No issues found`。
- Flutter 全套：`409 passed, 4 failed`。失敗皆集中於未修改的
  `test/watch_page_test.dart`；隔離重跑仍為相同四項，包含既有 debounce timer 與播放器
  時序／版面斷言。其餘測試（包含本輪新增回歸）均通過。
- CI 腳本回歸：`9 passed`；隔離 PyInstaller fixture 可啟動，打包 archive 檢查通過。
- README JSONC、TOML、PowerShell 語法與全新／既有 checkout setup smoke 均通過。

## 未在本機宣稱完成的驗證

- Windows 無法驗證 Xcode、iOS 簽章、App Store 或 Apple 真機流程。
- 未使用真實巴哈帳號、Discord 帳號、Chromecast／Android TV 或 Shopee 帳號做線上驗證。
- 全庫第一方檔案逐行覆蓋因使用者要求直接收尾而中止；未完成項目以
  `round4-file-review.md` 的逐檔 ledger 為準。

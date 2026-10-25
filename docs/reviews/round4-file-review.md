# 第四輪逐檔審查紀錄

基準：`356c851`；工作目錄：`C:\Users\User\Desktop\fork 的地方\aniGamerPlus`。

清單由基準工作樹的 `git ls-files -z` 建立。分類或執行測試不等於逐檔深讀；只有實際讀過的區間才記為已讀。原生平台在 Windows 無法實機／Xcode 驗證，靜態閱讀與離線驗證分開記錄。

## 盤點

受版控檔案：435；紀錄含本輪新增檔：435。

| 分類 | 數量 |
| --- | ---: |
| 二進位素材 | 23 |
| 文件與授權 | 9 |
| 測試與fixtures | 72 |
| 生成檔或IDE metadata | 6 |
| 第一方原始碼 | 127 |
| 第三方分支與本地整合（需審查） | 25 |
| 第三方原始資產 | 137 |
| 設定與資料 | 36 |

狀態：尚未閱讀 226；已完整閱讀 43；排除逐行程式審查 166。

## 逐檔結果與尚未審查清單

「尚未閱讀」與「部分閱讀」列即為未完成清單；不以過往回合或測試通過替代本輪逐檔覆蓋。

| 檔案 | 類別 | 行數 | 本輪閱讀區間 | 狀態 | 結果／驗證 |
| --- | --- | ---: | --- | --- | --- |
| `.codex/environments/environment.toml` | 設定與資料 | 6 | - | 尚未閱讀 | 待逐檔閱讀 |
| `.dockerignore` | 設定與資料 | 145 | - | 尚未閱讀 | 待逐檔閱讀 |
| `.github/ISSUE_TEMPLATE.md` | 文件與授權 | 23 | - | 尚未閱讀 | 待逐檔閱讀 |
| `.github/scripts/publish-nightly.sh` | 第一方原始碼 | 44 | - | 尚未閱讀 | 待逐檔閱讀 |
| `.github/workflows/Flutter-build.yml` | 設定與資料 | 337 | - | 尚未閱讀 | 待逐檔閱讀 |
| `.github/workflows/Python-build.yml` | 設定與資料 | 142 | - | 尚未閱讀 | 待逐檔閱讀 |
| `.github/workflows/Release-build.yml` | 設定與資料 | 108 | - | 尚未閱讀 | 待逐檔閱讀 |
| `.gitignore` | 設定與資料 | 163 | - | 尚未閱讀 | 待逐檔閱讀 |
| `.idea/.gitignore` | 生成檔或IDE metadata | 3 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `.idea/.name` | 生成檔或IDE metadata | 1 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `.idea/vcs.xml` | 生成檔或IDE metadata | 12 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `.vs/ProjectSettings.json` | 生成檔或IDE metadata | 3 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `.vs/slnx.sqlite` | 生成檔或IDE metadata | 988 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Anime.py` | 第一方原始碼 | 1655 | - | 尚未閱讀 | 待逐檔閱讀 |
| `Catalog.py` | 第一方原始碼 | 219 | - | 尚未閱讀 | 待逐檔閱讀 |
| `ColorPrint.py` | 第一方原始碼 | 133 | - | 尚未閱讀 | 待逐檔閱讀 |
| `Config.py` | 第一方原始碼 | 1500 | - | 尚未閱讀 | 待逐檔閱讀 |
| `Danmu.py` | 第一方原始碼 | 145 | - | 尚未閱讀 | 待逐檔閱讀 |
| `DanmuTemplate.ass` | 第一方原始碼 | 19 | - | 尚未閱讀 | 待逐檔閱讀 |
| `Dashboard/Server.py` | 第一方原始碼 | 4579 | - | 尚未閱讀 | 待逐檔閱讀 |
| `Dashboard/sslkey/.gitkeep` | 設定與資料 | 0 | - | 尚未閱讀 | 待逐檔閱讀 |
| `Dashboard/static/css/agp.css` | 第一方原始碼 | 816 | - | 尚未閱讀 | 待逐檔閱讀 |
| `Dashboard/static/css/aniGamerPlus.css` | 第一方原始碼 | 93 | - | 尚未閱讀 | 待逐檔閱讀 |
| `Dashboard/static/css/bootstrap-select.min.css` | 第三方原始資產 | 6 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/css/bootstrap-switch.min.css` | 第三方原始資產 | 1 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/css/bootstrap.min.css` | 第三方原始資產 | 6 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/css/bootstrap.rfs.min.css` | 第三方原始資產 | 6 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/css/catalog.css` | 第一方原始碼 | 529 | - | 尚未閱讀 | 待逐檔閱讀 |
| `Dashboard/static/css/fontawesome.all.min.css` | 第三方原始資產 | 5 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/css/home.css` | 第一方原始碼 | 231 | - | 尚未閱讀 | 待逐檔閱讀 |
| `Dashboard/static/css/watch.css` | 第一方原始碼 | 1254 | - | 尚未閱讀 | 待逐檔閱讀 |
| `Dashboard/static/data/opening_t2s.json` | 設定與資料 | 1 | - | 尚未閱讀 | 待逐檔閱讀 |
| `Dashboard/static/img/aniGamerPlus.ico` | 二進位素材 | 11 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/img/pwa/apple-touch-icon.png` | 二進位素材 | 21 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/img/pwa/icon-192.png` | 二進位素材 | 53 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/img/pwa/icon-512-maskable.png` | 二進位素材 | 52 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/img/pwa/icon-512.png` | 二進位素材 | 117 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/js/agp-shell.js` | 第一方原始碼 | 537 | - | 尚未閱讀 | 待逐檔閱讀 |
| `Dashboard/static/js/aniGamerPlus.js` | 第一方原始碼 | 396 | - | 尚未閱讀 | 待逐檔閱讀 |
| `Dashboard/static/js/ass.global.min.js` | 第三方原始資產 | 1 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/js/bootstrap-select.min.js` | 第三方原始資產 | 8 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/js/bootstrap-switch.min-3.3.4.js` | 第一方原始碼 | 10 | - | 尚未閱讀 | 待逐檔閱讀 |
| `Dashboard/static/js/bootstrap.min.js` | 第三方原始資產 | 6 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/js/catalog.js` | 第一方原始碼 | 1021 | - | 尚未閱讀 | 待逐檔閱讀 |
| `Dashboard/static/js/hls.light-1.6.15.min.js` | 第三方原始資產 | 2 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/js/home.js` | 第一方原始碼 | 1035 | - | 尚未閱讀 | 待逐檔閱讀 |
| `Dashboard/static/js/jquery-3.7.1.min.js` | 第三方原始資產 | 2 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/js/monitor.js` | 第一方原始碼 | 107 | - | 尚未閱讀 | 待逐檔閱讀 |
| `Dashboard/static/js/popper.min.js` | 第三方原始資產 | 4 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/js/settings_id_list.js` | 第一方原始碼 | 31 | - | 尚未閱讀 | 待逐檔閱讀 |
| `Dashboard/static/js/userapi.js` | 第一方原始碼 | 259 | - | 尚未閱讀 | 待逐檔閱讀 |
| `Dashboard/static/js/watch.js` | 第一方原始碼 | 3008 | - | 尚未閱讀 | 待逐檔閱讀 |
| `Dashboard/static/layui/css/layui.css` | 第三方原始資產 | 2 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/layui/css/layui.mobile.css` | 第三方原始資產 | 2 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/layui/css/modules/code.css` | 第三方原始資產 | 2 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/layui/css/modules/laydate/default/laydate.css` | 第三方原始資產 | 2 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/layui/css/modules/layer/default/icon-ext.png` | 第三方原始資產 | 37 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/layui/css/modules/layer/default/icon.png` | 第三方原始資產 | 73 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/layui/css/modules/layer/default/layer.css` | 第三方原始資產 | 2 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/layui/css/modules/layer/default/loading-0.gif` | 第三方原始資產 | 60 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/layui/css/modules/layer/default/loading-1.gif` | 第三方原始資產 | 25 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/layui/css/modules/layer/default/loading-2.gif` | 第三方原始資產 | 12 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/layui/font/iconfont.eot` | 第三方原始資產 | 878 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/layui/font/iconfont.svg` | 第三方原始資產 | 554 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/layui/font/iconfont.ttf` | 第三方原始資產 | 878 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/layui/font/iconfont.woff` | 第三方原始資產 | 237 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/layui/font/iconfont.woff2` | 第三方原始資產 | 181 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/layui/images/face/0.gif` | 第三方原始資產 | 18 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/layui/images/face/1.gif` | 第三方原始資產 | 43 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/layui/images/face/10.gif` | 第三方原始資產 | 11 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/layui/images/face/11.gif` | 第三方原始資產 | 68 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/layui/images/face/12.gif` | 第三方原始資產 | 33 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/layui/images/face/13.gif` | 第三方原始資產 | 119 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/layui/images/face/14.gif` | 第三方原始資產 | 26 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/layui/images/face/15.gif` | 第三方原始資產 | 27 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/layui/images/face/16.gif` | 第三方原始資產 | 111 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/layui/images/face/17.gif` | 第三方原始資產 | 60 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/layui/images/face/18.gif` | 第三方原始資產 | 28 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/layui/images/face/19.gif` | 第三方原始資產 | 22 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/layui/images/face/2.gif` | 第三方原始資產 | 56 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/layui/images/face/20.gif` | 第三方原始資產 | 49 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/layui/images/face/21.gif` | 第三方原始資產 | 61 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/layui/images/face/22.gif` | 第三方原始資產 | 258 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/layui/images/face/23.gif` | 第三方原始資產 | 54 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/layui/images/face/24.gif` | 第三方原始資產 | 139 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/layui/images/face/25.gif` | 第三方原始資產 | 47 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/layui/images/face/26.gif` | 第三方原始資產 | 29 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/layui/images/face/27.gif` | 第三方原始資產 | 41 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/layui/images/face/28.gif` | 第三方原始資產 | 45 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/layui/images/face/29.gif` | 第三方原始資產 | 41 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/layui/images/face/3.gif` | 第三方原始資產 | 43 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/layui/images/face/30.gif` | 第三方原始資產 | 43 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/layui/images/face/31.gif` | 第三方原始資產 | 28 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/layui/images/face/32.gif` | 第三方原始資產 | 19 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/layui/images/face/33.gif` | 第三方原始資產 | 36 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/layui/images/face/34.gif` | 第三方原始資產 | 36 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/layui/images/face/35.gif` | 第三方原始資產 | 19 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/layui/images/face/36.gif` | 第三方原始資產 | 30 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/layui/images/face/37.gif` | 第三方原始資產 | 22 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/layui/images/face/38.gif` | 第三方原始資產 | 28 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/layui/images/face/39.gif` | 第三方原始資產 | 82 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/layui/images/face/4.gif` | 第三方原始資產 | 84 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/layui/images/face/40.gif` | 第三方原始資產 | 20 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/layui/images/face/41.gif` | 第三方原始資產 | 39 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/layui/images/face/42.gif` | 第三方原始資產 | 73 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/layui/images/face/43.gif` | 第三方原始資產 | 15 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/layui/images/face/44.gif` | 第三方原始資產 | 34 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/layui/images/face/45.gif` | 第三方原始資產 | 34 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/layui/images/face/46.gif` | 第三方原始資產 | 33 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/layui/images/face/47.gif` | 第三方原始資產 | 37 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/layui/images/face/48.gif` | 第三方原始資產 | 35 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/layui/images/face/49.gif` | 第三方原始資產 | 18 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/layui/images/face/5.gif` | 第三方原始資產 | 34 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/layui/images/face/50.gif` | 第三方原始資產 | 106 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/layui/images/face/51.gif` | 第三方原始資產 | 14 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/layui/images/face/52.gif` | 第三方原始資產 | 5 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/layui/images/face/53.gif` | 第三方原始資產 | 14 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/layui/images/face/54.gif` | 第三方原始資產 | 12 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/layui/images/face/55.gif` | 第三方原始資產 | 12 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/layui/images/face/56.gif` | 第三方原始資產 | 4 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/layui/images/face/57.gif` | 第三方原始資產 | 27 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/layui/images/face/58.gif` | 第三方原始資產 | 36 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/layui/images/face/59.gif` | 第三方原始資產 | 264 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/layui/images/face/6.gif` | 第三方原始資產 | 31 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/layui/images/face/60.gif` | 第三方原始資產 | 34 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/layui/images/face/61.gif` | 第三方原始資產 | 30 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/layui/images/face/62.gif` | 第三方原始資產 | 12 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/layui/images/face/63.gif` | 第三方原始資產 | 46 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/layui/images/face/64.gif` | 第三方原始資產 | 66 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/layui/images/face/65.gif` | 第三方原始資產 | 38 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/layui/images/face/66.gif` | 第三方原始資產 | 49 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/layui/images/face/67.gif` | 第三方原始資產 | 33 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/layui/images/face/68.gif` | 第三方原始資產 | 20 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/layui/images/face/69.gif` | 第三方原始資產 | 14 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/layui/images/face/7.gif` | 第三方原始資產 | 72 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/layui/images/face/70.gif` | 第三方原始資產 | 68 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/layui/images/face/71.gif` | 第三方原始資產 | 53 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/layui/images/face/8.gif` | 第三方原始資產 | 39 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/layui/images/face/9.gif` | 第三方原始資產 | 42 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/layui/lay/modules/carousel.js` | 第三方原始資產 | 2 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/layui/lay/modules/code.js` | 第三方原始資產 | 2 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/layui/lay/modules/colorpicker.js` | 第三方原始資產 | 2 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/layui/lay/modules/element.js` | 第三方原始資產 | 2 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/layui/lay/modules/flow.js` | 第三方原始資產 | 2 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/layui/lay/modules/form.js` | 第三方原始資產 | 2 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/layui/lay/modules/jquery.js` | 第三方原始資產 | 5 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/layui/lay/modules/laydate.js` | 第三方原始資產 | 2 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/layui/lay/modules/layedit.js` | 第三方原始資產 | 2 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/layui/lay/modules/layer.js` | 第三方原始資產 | 2 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/layui/lay/modules/laypage.js` | 第三方原始資產 | 2 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/layui/lay/modules/laytpl.js` | 第三方原始資產 | 2 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/layui/lay/modules/mobile.js` | 第三方原始資產 | 2 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/layui/lay/modules/rate.js` | 第三方原始資產 | 2 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/layui/lay/modules/slider.js` | 第三方原始資產 | 2 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/layui/lay/modules/table.js` | 第三方原始資產 | 2 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/layui/lay/modules/transfer.js` | 第三方原始資產 | 2 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/layui/lay/modules/tree.js` | 第三方原始資產 | 2 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/layui/lay/modules/upload.js` | 第三方原始資產 | 2 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/layui/lay/modules/util.js` | 第三方原始資產 | 2 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/layui/layui.all.js` | 第三方原始資產 | 5 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/layui/layui.js` | 第三方原始資產 | 2 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/manifest.webmanifest` | 設定與資料 | 50 | - | 尚未閱讀 | 待逐檔閱讀 |
| `Dashboard/static/offline.html` | 第一方原始碼 | 14 | - | 尚未閱讀 | 待逐檔閱讀 |
| `Dashboard/static/sw.js` | 第一方原始碼 | 176 | - | 尚未閱讀 | 待逐檔閱讀 |
| `Dashboard/static/webfonts/fa-brands-400.eot` | 第三方原始資產 | 3276 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/webfonts/fa-brands-400.svg` | 第三方原始資產 | 3637 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/webfonts/fa-brands-400.ttf` | 第三方原始資產 | 3275 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/webfonts/fa-brands-400.woff` | 第三方原始資產 | 722 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/webfonts/fa-brands-400.woff2` | 第三方原始資產 | 562 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/webfonts/fa-regular-400.eot` | 第三方原始資產 | 620 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/webfonts/fa-regular-400.svg` | 第三方原始資產 | 805 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/webfonts/fa-regular-400.ttf` | 第三方原始資產 | 620 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/webfonts/fa-regular-400.woff` | 第三方原始資產 | 139 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/webfonts/fa-regular-400.woff2` | 第三方原始資產 | 104 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/webfonts/fa-solid-900.eot` | 第三方原始資產 | 5418 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/webfonts/fa-solid-900.svg` | 第三方原始資產 | 5015 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/webfonts/fa-solid-900.ttf` | 第三方原始資產 | 5417 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/webfonts/fa-solid-900.woff` | 第三方原始資產 | 721 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/static/webfonts/fa-solid-900.woff2` | 第三方原始資產 | 610 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `Dashboard/templates/control.html` | 第一方原始碼 | 513 | - | 尚未閱讀 | 待逐檔閱讀 |
| `Dashboard/templates/index.html` | 第一方原始碼 | 113 | - | 尚未閱讀 | 待逐檔閱讀 |
| `Dashboard/templates/login.html` | 第一方原始碼 | 70 | - | 尚未閱讀 | 待逐檔閱讀 |
| `Dashboard/templates/monitor.html` | 第一方原始碼 | 57 | - | 尚未閱讀 | 待逐檔閱讀 |
| `Dashboard/templates/register.html` | 第一方原始碼 | 44 | - | 尚未閱讀 | 待逐檔閱讀 |
| `Dashboard/templates/userinfo.html` | 第一方原始碼 | 105 | - | 尚未閱讀 | 待逐檔閱讀 |
| `Dashboard/templates/usermanage.html` | 第一方原始碼 | 217 | - | 尚未閱讀 | 待逐檔閱讀 |
| `Dashboard/templates/watch.html` | 第一方原始碼 | 109 | - | 尚未閱讀 | 待逐檔閱讀 |
| `Dashboard/thumbnail_cache.py` | 第一方原始碼 | 116 | - | 尚未閱讀 | 待逐檔閱讀 |
| `Dockerfile` | 設定與資料 | 12 | - | 尚未閱讀 | 待逐檔閱讀 |
| `LICENSE` | 文件與授權 | 674 | - | 尚未閱讀 | 待逐檔閱讀 |
| `Loginer.py` | 第一方原始碼 | 229 | - | 尚未閱讀 | 待逐檔閱讀 |
| `OpeningSkip.py` | 第一方原始碼 | 252 | - | 尚未閱讀 | 待逐檔閱讀 |
| `README.md` | 文件與授權 | 729 | - | 尚未閱讀 | 待逐檔閱讀 |
| `aniGamerPlus.py` | 第一方原始碼 | 1764 | - | 尚未閱讀 | 待逐檔閱讀 |
| `config-sample.json` | 設定與資料 | 119 | - | 尚未閱讀 | 待逐檔閱讀 |
| `docker-compose.yml` | 設定與資料 | 20 | - | 尚未閱讀 | 待逐檔閱讀 |
| `docs/optimization-audit.md` | 文件與授權 | 192 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/.gitignore` | 設定與資料 | 35 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/README.md` | 文件與授權 | 317 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/analysis_options.yaml` | 設定與資料 | 18 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/android_extensions/no_updater/AndroidManifest.xml` | 設定與資料 | 9 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/android_extensions/res/drawable-xhdpi/tv_banner.png` | 二進位素材 | 101 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `flutter_app/assets/opening_t2s.json` | 設定與資料 | 1 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/ios_extensions/DownloadActivity/DownloadActivityWidget.swift` | 第一方原始碼 | 199 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/ios_extensions/DownloadActivity/Info.plist` | 設定與資料 | 29 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/lib/main.dart` | 第一方原始碼 | 27 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/lib/src/api/client.dart` | 第一方原始碼 | 847 | 1–847 | 已完整閱讀 | 全文檢查 HTTP、快取、登入競態；補 Discord PUT/DELETE context guard，2 新回歸 red→green |
| `flutter_app/lib/src/api/models.dart` | 第一方原始碼 | 508 | 1–508 | 已完整閱讀 | 全文檢查 JSON 映射、預設值、觀看進度與片單欄位；未新增可重現缺陷 |
| `flutter_app/lib/src/api/opening_skip.dart` | 第一方原始碼 | 739 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/lib/src/app.dart` | 第一方原始碼 | 134 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/lib/src/danmaku/ass.dart` | 第一方原始碼 | 103 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/lib/src/danmaku/danmaku_overlay.dart` | 第一方原始碼 | 748 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/lib/src/pages/all_tab.dart` | 第一方原始碼 | 471 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/lib/src/pages/anime_sheet.dart` | 第一方原始碼 | 1263 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/lib/src/pages/app_prefs_page.dart` | 第一方原始碼 | 443 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/lib/src/pages/console_page.dart` | 第一方原始碼 | 247 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/lib/src/pages/discord_login_page.dart` | 第一方原始碼 | 128 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/lib/src/pages/discord_settings_page.dart` | 第一方原始碼 | 182 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/lib/src/pages/downloads_page.dart` | 第一方原始碼 | 411 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/lib/src/pages/export_sheet.dart` | 第一方原始碼 | 460 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/lib/src/pages/favourites_tab.dart` | 第一方原始碼 | 91 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/lib/src/pages/history_tab.dart` | 第一方原始碼 | 226 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/lib/src/pages/home_tab.dart` | 第一方原始碼 | 652 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/lib/src/pages/login_page.dart` | 第一方原始碼 | 241 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/lib/src/pages/manual_task_sheet.dart` | 第一方原始碼 | 287 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/lib/src/pages/me_tab.dart` | 第一方原始碼 | 338 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/lib/src/pages/monitor_page.dart` | 第一方原始碼 | 342 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/lib/src/pages/register_page.dart` | 第一方原始碼 | 159 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/lib/src/pages/root_page.dart` | 第一方原始碼 | 283 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/lib/src/pages/search_page.dart` | 第一方原始碼 | 322 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/lib/src/pages/settings_page.dart` | 第一方原始碼 | 711 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/lib/src/pages/setup_page.dart` | 第一方原始碼 | 320 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/lib/src/pages/sn_list_page.dart` | 第一方原始碼 | 397 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/lib/src/pages/tv_remote_actions.dart` | 第一方原始碼 | 264 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/lib/src/pages/tv_remote_page.dart` | 第一方原始碼 | 933 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/lib/src/pages/tv_remote_settings_page.dart` | 第一方原始碼 | 160 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/lib/src/pages/update_dialog.dart` | 第一方原始碼 | 196 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/lib/src/pages/user_info_page.dart` | 第一方原始碼 | 220 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/lib/src/pages/user_manage_page.dart` | 第一方原始碼 | 419 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/lib/src/pages/watch_page.dart` | 第一方原始碼 | 5891 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/lib/src/state/app_state.dart` | 第一方原始碼 | 1109 | 1–1109 | 已完整閱讀 | 全文及修補 diff 已讀；5 watch-time race 回歸 red→green，watch/client context 20 tests 通過 |
| `flutter_app/lib/src/state/cast.dart` | 第一方原始碼 | 599 | 1–599 | 已完整閱讀 | 全文檢查SDK lifecycle、媒體identity、寬限期；late init dispose與跨origin status已 red→修補，完整target執行中 |
| `flutter_app/lib/src/state/discord_crypto.dart` | 第一方原始碼 | 145 | 1–145 | 已完整閱讀 | 全文檢查 envelope 尺寸、AAD、KDF、TV connection binding；離線 crypto 測試通過 |
| `flutter_app/lib/src/state/discord_gateway.dart` | 第一方原始碼 | 346 | 1–346 | 已完整閱讀 | 全文檢查 lifecycle、heartbeat/retry、resume URL、節流；loopback Gateway 測試通過 |
| `flutter_app/lib/src/state/discord_presence.dart` | 第一方原始碼 | 285 | 1–285 | 已完整閱讀 | 全文檢查帳戶 scope、儲存、遠端同步；修復晚到 unlink 清新帳戶，新增回歸 red→green |
| `flutter_app/lib/src/state/download_background.dart` | 第一方原始碼 | 166 | 1–166 | 已完整閱讀 | 全文檢查批次進度、通知節流與 lifecycle；原生通知需裝置實機驗證 |
| `flutter_app/lib/src/state/download_network.dart` | 第一方原始碼 | 68 | 1–68 | 已完整閱讀 | 全文檢查 Wi-Fi 限制與 connectivity revision；start/dispose 時序列候選待驗證 |
| `flutter_app/lib/src/state/downloads.dart` | 第一方原始碼 | 1387 | 1–1387 | 已完整閱讀 | 全文及修補diff；SN/原生檔名界線與remove/re-enqueue已修，4新回歸red→下載36 tests green |
| `flutter_app/lib/src/state/http_range.dart` | 第一方原始碼 | 35 | 1–35 | 已完整閱讀 | 全文檢查 byte range 邊界、溢位、unsatisfied 格式；未新增可重現缺陷 |
| `flutter_app/lib/src/state/intro_skip.dart` | 第一方原始碼 | 62 | 1–62 | 已完整閱讀 | 全文檢查時間界線與投票聚類；未新增可重現缺陷 |
| `flutter_app/lib/src/state/mp4_prefetch.dart` | 第一方原始碼 | 180 | 1–180 | 已完整閱讀 | 全文檢查 box bounds、sample/chunk mapping、edit list；未新增可重現缺陷 |
| `flutter_app/lib/src/state/prefs.dart` | 第一方原始碼 | 355 | 1–355 | 已完整閱讀 | 全文閱讀；偏好值與非同步持久化流程已核對，待呼叫端競態驗證 |
| `flutter_app/lib/src/state/remote_setup.dart` | 第一方原始碼 | 351 | 1–351 | 已完整閱讀 | 全文檢查 QR token、body上限、表單escaping與lifecycle；實際 panel 有未mounted時關閉補償 |
| `flutter_app/lib/src/state/seek_preview.dart` | 第一方原始碼 | 127 | 1–127 | 已完整閱讀 | 全文檢查單decoder、過期結果、debounce、取消與cache上限；未新增可重現缺陷 |
| `flutter_app/lib/src/state/thumbnails.dart` | 第一方原始碼 | 580 | 1–580 | 已完整閱讀 | 全文檢查gate、dedupe、圖片signature與disk cache；跨server manifest/fallback隔離列候選待回歸 |
| `flutter_app/lib/src/state/tv_remote_client.dart` | 第一方原始碼 | 554 | 1–554 | 已完整閱讀 | 全文檢查discovery、generation、WebSocket timeout、加密轉送；loopback tv suite通過 |
| `flutter_app/lib/src/state/tv_remote_host.dart` | 第一方原始碼 | 643 | 1–643 | 已完整閱讀 | 全文及修改diff；修復晚到授權與start/stop race，2新增回歸 red→14 tests green |
| `flutter_app/lib/src/state/tv_remote_protocol.dart` | 第一方原始碼 | 206 | 1–206 | 已完整閱讀 | 全文檢查序列化、地址解析與配對資料欄位；未新增可重現缺陷 |
| `flutter_app/lib/src/state/updater.dart` | 第一方原始碼 | 357 | 1–357 | 已完整閱讀 | 全文檢查 release/manifest映射、checksum與下載清理；原生安裝器需裝置實機 |
| `flutter_app/lib/src/state/video_cache.dart` | 第一方原始碼 | 1393 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/lib/src/state/video_export.dart` | 第一方原始碼 | 122 | 1–122 | 已完整閱讀 | 全文及修補diff；二次撞名已修，13 tests通過 |
| `flutter_app/lib/src/theme.dart` | 第一方原始碼 | 261 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/lib/src/util/build_config.dart` | 第一方原始碼 | 4 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/lib/src/util/device.dart` | 第一方原始碼 | 65 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/lib/src/util/format.dart` | 第一方原始碼 | 155 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/lib/src/util/remote_keys.dart` | 第一方原始碼 | 112 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/lib/src/widgets/active_builder.dart` | 第一方原始碼 | 108 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/lib/src/widgets/cards.dart` | 第一方原始碼 | 455 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/lib/src/widgets/cast_sheet.dart` | 第一方原始碼 | 145 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/lib/src/widgets/common.dart` | 第一方原始碼 | 533 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/lib/src/widgets/intro_skip_prompt.dart` | 第一方原始碼 | 216 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/lib/src/widgets/playback_countdown_card.dart` | 第一方原始碼 | 94 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/lib/src/widgets/remote_setup_panel.dart` | 第一方原始碼 | 286 | 1–286 | 已完整閱讀 | 全文檢查mounted、server清理、QR quiet zone與狀態顯示 |
| `flutter_app/lib/src/widgets/seek_preview_card.dart` | 第一方原始碼 | 72 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/lib/src/widgets/tv_settings_list.dart` | 第一方原始碼 | 125 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/packages/airplay_route/ios/Classes/AirplayRoutePlugin.swift` | 第一方原始碼 | 114 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/packages/airplay_route/ios/airplay_route.podspec` | 設定與資料 | 23 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/packages/airplay_route/lib/airplay_route.dart` | 第一方原始碼 | 99 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/packages/airplay_route/pubspec.yaml` | 設定與資料 | 18 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/packages/background_download/android/build.gradle` | 設定與資料 | 28 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/packages/background_download/android/settings.gradle` | 設定與資料 | 1 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/packages/background_download/android/src/main/AndroidManifest.xml` | 設定與資料 | 16 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/packages/background_download/android/src/main/java/tw/avianjay/background_download/BackgroundDownloadPlugin.java` | 第一方原始碼 | 118 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/packages/background_download/android/src/main/java/tw/avianjay/background_download/DownloadService.java` | 第一方原始碼 | 235 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/packages/background_download/ios/Classes/BackgroundDownloadPlugin.swift` | 第一方原始碼 | 67 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/packages/background_download/ios/Classes/BackgroundDownloadSession.swift` | 第一方原始碼 | 545 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/packages/background_download/ios/Classes/DownloadActivityAttributes.swift` | 第一方原始碼 | 23 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/packages/background_download/ios/Classes/DownloadFileStore.swift` | 第一方原始碼 | 89 | 1–89 | 已完整閱讀 | 全文檢查原子替換、permission failure chain；Windows 無 Swift/Xcode 原生執行環境 |
| `flutter_app/packages/background_download/ios/Classes/LiveActivityController.swift` | 第一方原始碼 | 173 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/packages/background_download/ios/Classes/ResumeStore.swift` | 第一方原始碼 | 63 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/packages/background_download/ios/Tests/DownloadFileStoreTests.swift` | 測試與fixtures | 150 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/packages/background_download/ios/background_download.podspec` | 設定與資料 | 24 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/packages/background_download/lib/background_download.dart` | 第一方原始碼 | 235 | 1–235 | 已完整閱讀 | 全文檢查 platform channel、TransferResult/Snapshot 與 native事件映射；Dart mock native 測試通過 |
| `flutter_app/packages/background_download/pubspec.yaml` | 設定與資料 | 21 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/packages/cast_keepalive/ios/Classes/CastKeepalivePlugin.swift` | 第一方原始碼 | 108 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/packages/cast_keepalive/ios/cast_keepalive.podspec` | 設定與資料 | 24 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/packages/cast_keepalive/lib/cast_keepalive.dart` | 第一方原始碼 | 33 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/packages/cast_keepalive/pubspec.yaml` | 設定與資料 | 18 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/packages/file_export/android/build.gradle` | 設定與資料 | 28 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/packages/file_export/android/settings.gradle` | 設定與資料 | 1 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/packages/file_export/android/src/main/AndroidManifest.xml` | 設定與資料 | 1 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/packages/file_export/android/src/main/java/tw/avianjay/file_export/FileExportPlugin.java` | 第一方原始碼 | 298 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/packages/file_export/ios/Classes/FileExportPlugin.swift` | 第一方原始碼 | 117 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/packages/file_export/ios/file_export.podspec` | 設定與資料 | 23 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/packages/file_export/lib/file_export.dart` | 第一方原始碼 | 101 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/packages/file_export/pubspec.yaml` | 設定與資料 | 21 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/packages/video_player_pip/LICENSE` | 文件與授權 | 21 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/packages/video_player_pip/UPSTREAM.md` | 文件與授權 | 22 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/packages/video_player_pip/android/build.gradle` | 第三方分支與本地整合（需審查） | 66 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/packages/video_player_pip/android/settings.gradle` | 第三方分支與本地整合（需審查） | 1 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/packages/video_player_pip/android/src/main/AndroidManifest.xml` | 第三方分支與本地整合（需審查） | 20 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/packages/video_player_pip/android/src/main/kotlin/uz/flutterwithakmaljon/video_player_pip/VideoPlayerPipPlugin.kt` | 第三方分支與本地整合（需審查） | 322 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/packages/video_player_pip/android/src/test/kotlin/uz/flutterwithakmaljon/video_player_pip/VideoPlayerPipPluginTest.kt` | 測試與fixtures | 27 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/packages/video_player_pip/ios/Classes/VideoPlayerPipPlugin.swift` | 第三方分支與本地整合（需審查） | 407 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/packages/video_player_pip/ios/Resources/PrivacyInfo.xcprivacy` | 第三方分支與本地整合（需審查） | 14 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/packages/video_player_pip/ios/video_player_pip.podspec` | 第三方分支與本地整合（需審查） | 32 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/packages/video_player_pip/lib/index.dart` | 第三方分支與本地整合（需審查） | 11 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/packages/video_player_pip/lib/src/extensions.dart` | 第三方分支與本地整合（需審查） | 29 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/packages/video_player_pip/lib/src/src/closed_caption_file.dart` | 第三方分支與本地整合（需審查） | 96 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/packages/video_player_pip/lib/src/src/sub_rip.dart` | 第三方分支與本地整合（需審查） | 135 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/packages/video_player_pip/lib/src/src/web_vtt.dart` | 第三方分支與本地整合（需審查） | 216 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/packages/video_player_pip/lib/src/video_player_controller.dart` | 第三方分支與本地整合（需審查） | 1276 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/packages/video_player_pip/lib/video_player_pip.dart` | 第三方分支與本地整合（需審查） | 205 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/packages/video_player_pip/lib/video_player_pip_method_channel.dart` | 第三方分支與本地整合（需審查） | 94 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/packages/video_player_pip/lib/video_player_pip_platform_interface.dart` | 第三方分支與本地整合（需審查） | 63 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/packages/video_player_pip/pubspec.yaml` | 第三方分支與本地整合（需審查） | 78 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/packages/video_thumbnail/LICENSE` | 文件與授權 | 21 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/packages/video_thumbnail/README.md` | 文件與授權 | 17 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/packages/video_thumbnail/android/build.gradle` | 第三方分支與本地整合（需審查） | 26 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/packages/video_thumbnail/android/src/main/AndroidManifest.xml` | 第三方分支與本地整合（需審查） | 1 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/packages/video_thumbnail/android/src/main/java/xyz/justsoft/video_thumbnail/VideoThumbnailPlugin.java` | 第三方分支與本地整合（需審查） | 267 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/packages/video_thumbnail/ios/Classes/VideoThumbnailPlugin.h` | 第三方分支與本地整合（需審查） | 4 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/packages/video_thumbnail/ios/Classes/VideoThumbnailPlugin.m` | 第三方分支與本地整合（需審查） | 183 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/packages/video_thumbnail/ios/video_thumbnail.podspec` | 第三方分支與本地整合（需審查） | 25 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/packages/video_thumbnail/lib/video_thumbnail.dart` | 第三方分支與本地整合（需審查） | 76 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/packages/video_thumbnail/pubspec.yaml` | 第三方分支與本地整合（需審查） | 22 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/pubspec.lock` | 生成檔或IDE metadata | 1132 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `flutter_app/pubspec.yaml` | 設定與資料 | 88 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/test/active_builder_test.dart` | 測試與fixtures | 75 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/test/app_context_test.dart` | 測試與fixtures | 261 | 1–261 | 已完整閱讀 | 全文及新增 5 watch-time race 已讀；11 tests 通過 |
| `flutter_app/test/app_rebuild_test.dart` | 測試與fixtures | 120 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/test/app_updater_build_test.dart` | 測試與fixtures | 87 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/test/cast_test.dart` | 測試與fixtures | 744 | 1–744 | 已完整閱讀 | 全文含mock Cast/本機播放器/widget整合；新增dispose與origin回歸red已確認 |
| `flutter_app/test/catalog_loading_test.dart` | 測試與fixtures | 53 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/test/client_context_test.dart` | 測試與fixtures | 130 | 1–130 | 已完整閱讀 | 全文檢查 mock context/登入案例；新增 PUT/DELETE stale response 回歸，7 tests 通過 |
| `flutter_app/test/continue_watching_test.dart` | 測試與fixtures | 171 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/test/danmaku_overlay_test.dart` | 測試與fixtures | 518 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/test/discord_presence_test.dart` | 測試與fixtures | 390 | 1–390 | 已完整閱讀 | 全文檢查 fake Gateway、加密、帳戶隔離；新增 late unlink 回歸，11 tests 通過 |
| `flutter_app/test/download_protocol_test.dart` | 測試與fixtures | 215 | 1–215 | 已完整閱讀 | 全文檢查 loopback resume fixture，新增 enqueue 路徑／彈幕路徑拒絕回歸 red→green |
| `flutter_app/test/downloads_danmaku_test.dart` | 測試與fixtures | 419 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/test/downloads_native_test.dart` | 測試與fixtures | 319 | 1–319 | 已完整閱讀 | 全文檢查 native channel fake；新增 orphan 路徑與 remove/re-enqueue 回歸 red→green |
| `flutter_app/test/ending_skip_test.dart` | 測試與fixtures | 134 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/test/episode_picker_test.dart` | 測試與fixtures | 300 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/test/http_range_test.dart` | 測試與fixtures | 30 | 1–30 | 已完整閱讀 | 全文檢查正常、反向、溢位、多 range 拒絕案例 |
| `flutter_app/test/intro_skip_prompt_test.dart` | 測試與fixtures | 252 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/test/intro_skip_test.dart` | 測試與fixtures | 39 | 1–39 | 已完整閱讀 | 全文檢查誤報拒絕與多票合法片頭案例 |
| `flutter_app/test/management_pages_test.dart` | 測試與fixtures | 335 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/test/mp4_prefetch_test.dart` | 測試與fixtures | 34 | 1–34 | 已完整閱讀 | 全文檢查 moov 前後、co64 與截斷 fixture |
| `flutter_app/test/opening_skip_fallback_test.dart` | 測試與fixtures | 245 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/test/opening_skip_lookup_test.dart` | 測試與fixtures | 371 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/test/remote_setup_test.dart` | 測試與fixtures | 178 | 1–178 | 已完整閱讀 | 全文檢查 loopback表單、token路徑、失敗回填與body上限；無真帳戶 |
| `flutter_app/test/search_page_test.dart` | 測試與fixtures | 393 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/test/seek_preview_test.dart` | 測試與fixtures | 105 | 1–105 | 已完整閱讀 | 全文檢查fake decoder與platform channel、source切換、timeout與取消 |
| `flutter_app/test/support/mp4_fixture.dart` | 測試與fixtures | 71 | 1–71 | 已完整閱讀 | 全文核對 sample tables、offset、mdat 長度 |
| `flutter_app/test/support/temp_dir.dart` | 測試與fixtures | 24 | 1–24 | 已完整閱讀 | 全文檢查 temp teardown；20次重試後保留檔案為測試清理限制 |
| `flutter_app/test/support/ui_capture.dart` | 測試與fixtures | 62 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/test/thumbnails_test.dart` | 測試與fixtures | 462 | 1–462 | 已完整閱讀 | 全文檢查兩loopback host、並行閘、HTTP header隔離與磁碟trim fixture |
| `flutter_app/test/tv_remote_test.dart` | 測試與fixtures | 460 | 1–460 | 已完整閱讀 | 全文檢查真loopback配對/指令/發現；新增2個時序回歸，14 tests通過 |
| `flutter_app/test/tv_remote_widgets_test.dart` | 測試與fixtures | 420 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/test/tv_test.dart` | 測試與fixtures | 185 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/test/updater_test.dart` | 測試與fixtures | 228 | 1–228 | 已完整閱讀 | 全文檢查fake release/manifest、下載長度及checksum；原生安裝未實機 |
| `flutter_app/test/video_cache_test.dart` | 測試與fixtures | 616 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/test/video_export_test.dart` | 測試與fixtures | 417 | 1–417 | 已完整閱讀 | 全文及二次撞名回歸已讀；13 tests通過 |
| `flutter_app/test/watch_page_test.dart` | 測試與fixtures | 2941 | - | 尚未閱讀 | 待逐檔閱讀 |
| `flutter_app/test/watch_times_test.dart` | 測試與fixtures | 309 | 1–309 | 已完整閱讀 | 全文閱讀；本機觀看紀錄與 loopback 同步案例已核對 |
| `flutter_app/tool/prepare_platforms.sh` | 第一方原始碼 | 938 | - | 尚未閱讀 | 待逐檔閱讀 |
| `plugin_system.py` | 第一方原始碼 | 366 | - | 尚未閱讀 | 待逐檔閱讀 |
| `plugins/.gitkeep` | 設定與資料 | 0 | - | 尚未閱讀 | 待逐檔閱讀 |
| `requirements-dev.txt` | 設定與資料 | 15 | - | 尚未閱讀 | 待逐檔閱讀 |
| `requirements.txt` | 設定與資料 | 25 | - | 尚未閱讀 | 待逐檔閱讀 |
| `screenshot/CookiesFormat.png` | 二進位素材 | 280 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `screenshot/Dashboard_Console.png` | 二進位素材 | 888 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `screenshot/Dashboard_UI.png` | 二進位素材 | 610 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `screenshot/Dashboard_manualTask.png` | 二進位素材 | 222 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `screenshot/Dashboard_proxy.png` | 二進位素材 | 172 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `screenshot/Dashboard_sn_list.png` | 二進位素材 | 381 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `screenshot/WhereIsCookie.png` | 二進位素材 | 3012 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `screenshot/config_ja3.png` | 二進位素材 | 1286 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `screenshot/cui_on_android.jpg` | 二進位素材 | 1617 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `screenshot/cui_range_mode.png` | 二進位素材 | 937 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `screenshot/cui_range_mode_err.png` | 二進位素材 | 66 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `screenshot/db.png` | 二進位素材 | 1467 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `screenshot/how_to_get_my_ua.png` | 二進位素材 | 436 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `screenshot/how_to_use_my_ua.png` | 二進位素材 | 168 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `screenshot/set_ua_via_dashboard.png` | 二進位素材 | 1432 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `sn_list-sample.txt` | 設定與資料 | 9 | - | 尚未閱讀 | 待逐檔閱讀 |
| `start-dashboard.bat` | 第一方原始碼 | 164 | - | 尚未閱讀 | 待逐檔閱讀 |
| `tests/conftest.py` | 測試與fixtures | 41 | - | 尚未閱讀 | 待逐檔閱讀 |
| `tests/fixtures/bocchi_anime_skip.json` | 測試與fixtures | 540 | - | 尚未閱讀 | 待逐檔閱讀 |
| `tests/fixtures/sample-thumb.jpg` | 二進位素材 | 15 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `tests/fixtures/sample.ass` | 測試與fixtures | 19 | - | 尚未閱讀 | 待逐檔閱讀 |
| `tests/fixtures/sample.webm` | 二進位素材 | 499 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `tests/shoot.py` | 測試與fixtures | 134 | - | 尚未閱讀 | 待逐檔閱讀 |
| `tests/test_account_deep_regressions.py` | 測試與fixtures | 103 | - | 尚未閱讀 | 待逐檔閱讀 |
| `tests/test_anime1me_plugin.py` | 測試與fixtures | 252 | - | 尚未閱讀 | 待逐檔閱讀 |
| `tests/test_auto_login_cookie.py` | 測試與fixtures | 85 | - | 尚未閱讀 | 待逐檔閱讀 |
| `tests/test_cast_ticket.py` | 測試與fixtures | 202 | - | 尚未閱讀 | 待逐檔閱讀 |
| `tests/test_catalog_hardening.py` | 測試與fixtures | 161 | - | 尚未閱讀 | 待逐檔閱讀 |
| `tests/test_config_atomic_write.py` | 測試與fixtures | 268 | - | 尚未閱讀 | 待逐檔閱讀 |
| `tests/test_core_deep_regressions.py` | 測試與fixtures | 285 | - | 尚未閱讀 | 待逐檔閱讀 |
| `tests/test_custom_video_sn.py` | 測試與fixtures | 82 | - | 尚未閱讀 | 待逐檔閱讀 |
| `tests/test_dashboard_loading.py` | 測試與fixtures | 219 | - | 尚未閱讀 | 待逐檔閱讀 |
| `tests/test_discord_presence.py` | 測試與fixtures | 94 | - | 尚未閱讀 | 待逐檔閱讀 |
| `tests/test_download_hardening.py` | 測試與fixtures | 512 | - | 尚未閱讀 | 待逐檔閱讀 |
| `tests/test_fastapi_fix_blockers.py` | 測試與fixtures | 574 | - | 尚未閱讀 | 待逐檔閱讀 |
| `tests/test_fastapi_server.py` | 測試與fixtures | 1479 | - | 尚未閱讀 | 待逐檔閱讀 |
| `tests/test_frontend_hardening.py` | 測試與fixtures | 136 | - | 尚未閱讀 | 待逐檔閱讀 |
| `tests/test_hls_playlist.py` | 測試與fixtures | 462 | - | 尚未閱讀 | 待逐檔閱讀 |
| `tests/test_hls_semantics_regressions.py` | 測試與fixtures | 36 | - | 尚未閱讀 | 待逐檔閱讀 |
| `tests/test_media_pipeline.py` | 測試與fixtures | 64 | - | 尚未閱讀 | 待逐檔閱讀 |
| `tests/test_opening_skip.py` | 測試與fixtures | 153 | - | 尚未閱讀 | 待逐檔閱讀 |
| `tests/test_plugin_fault_isolation.py` | 測試與fixtures | 240 | - | 尚未閱讀 | 待逐檔閱讀 |
| `tests/test_real_server_e2e.py` | 測試與fixtures | 685 | - | 尚未閱讀 | 待逐檔閱讀 |
| `tests/test_redownload_command.py` | 測試與fixtures | 249 | - | 尚未閱讀 | 待逐檔閱讀 |
| `tests/test_relogin_device_id.py` | 測試與fixtures | 154 | - | 尚未閱讀 | 待逐檔閱讀 |
| `tests/test_security_hardening.py` | 測試與fixtures | 298 | - | 尚未閱讀 | 待逐檔閱讀 |
| `tests/test_stream_deep_regressions.py` | 測試與fixtures | 287 | - | 尚未閱讀 | 待逐檔閱讀 |
| `tests/test_update_loop_resilience.py` | 測試與fixtures | 117 | - | 尚未閱讀 | 待逐檔閱讀 |
| `tests/test_userdata_transactions.py` | 測試與fixtures | 363 | - | 尚未閱讀 | 待逐檔閱讀 |
| `tests/test_web_ui.py` | 測試與fixtures | 2291 | - | 尚未閱讀 | 待逐檔閱讀 |
| `tests/test_worker_limiter_release.py` | 測試與fixtures | 230 | - | 尚未閱讀 | 待逐檔閱讀 |
| `tests/ui_harness.py` | 測試與fixtures | 1001 | - | 尚未閱讀 | 待逐檔閱讀 |
| `third_party/OpenCC-LICENSE.txt` | 第三方原始資產 | 55 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `third_party/OpenCC-NOTICE.md` | 第三方原始資產 | 9 | - | 排除逐行程式審查 | 只核對分類；未宣稱深入閱讀 |
| `tools/benchmark_thumbnail.py` | 第一方原始碼 | 126 | - | 尚未閱讀 | 待逐檔閱讀 |

# AI 課堂筆記整理器

## 1. 專題簡介
本工具提供大學生使用。使用者輸入課程名稱與原始課堂筆記，程式呼叫 OpenAI API，整理成筆記標題、內容摘要、重點整理、關鍵字、複習問題與需要補充的資訊。

本工具只依照使用者提供的原文整理，不應將模型產生的內容視為課堂事實；使用者仍須核對。

## 2. 使用技術與 JSON Schema 理由
本專題採用 JSON Schema Structured Outputs。因為結果需要固定欄位，才能在 Streamlit 介面逐欄顯示；`strict: true` 可要求模型遵守指定結構，程式也會在顯示前再次檢查欄位與型別。

## 3. 輸入與輸出欄位
輸入：
- 課程名稱
- 原始課堂筆記（最多 6000 字元）

輸出：
- title：筆記標題
- summary：內容摘要
- key_points：重點整理
- keywords：關鍵字
- review_questions：複習問題
- missing_information：需要補充的資訊

## 4. 安裝與啟動
建議使用 Python 3.14，並在本專案資料夾執行。

Windows PowerShell：

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

建立本機 `.env`，內容格式參考 `.env.example`，填入自己的 API 金鑰。真正的 `.env` 不可上傳 GitHub。

啟動：

```powershell
streamlit run app.py
```

## 5. API 與安全設定
- API 開關預設關閉。
- 只有使用者開啟 API 並提交有效表單後才會發出請求。
- 每次有效提交最多發出一次 API 請求，`max_retries=0`。
- 原始筆記最多 6000 字元。
- 金鑰只放本機 `.env` 或 Streamlit Cloud Secrets。
- 不可提交 `.env` 或 `.streamlit/secrets.toml`。

## 6. 操作範例
課程名稱：網路實務（一）

原始筆記範例（虛構測試資料）：
「今天介紹 IP 位址與子網路遮罩。老師說明 CIDR 的斜線數字代表網路前綴長度，也練習判斷可用 IP 範圍。」

預期輸出欄位：標題、摘要、重點、關鍵字、複習問題及需要補充的資訊。實際模型輸出請以測試紀錄為準。

## 7. 測試與驗收紀錄
尚待實測，完成後請如實填寫：
- 本機正常資料測試：未測
- 本機資訊不足測試：未測
- 空白／超過 6000 字元測試：未測（預期 0 次 API 請求）
- 雲端部署與真實 API 測試：未部署／未測
- 模型：gpt-5.4-mini（須確認自己的 API 帳號可呼叫）
- 實際請求數：待記錄

每次真實 API 測試請記錄日期、模型、輸入原文、輸出結果、請求數及人工核對結果。不要把尚未執行的測試寫成成功。

## 8. Streamlit Cloud
- App 網址：待部署後填寫
- GitHub Repo：待填寫
- 部署分支：待填寫
- Main file path：`Midterm Mini-Project/app.py`
- 雲端驗收日期：待填寫
- 雲端真實 API 成功紀錄：待測

部署時在 Streamlit Community Cloud 的 App Secrets 設定 `OPENAI_API_KEY` 與 `OPENAI_MODEL`。

## 9. 限制與後續改進
目前只支援貼上文字，不支援 PDF、Word 或 CSV。模型可能誤解筆記，因此重要資訊仍需人工核對。下一階段可加入檔案讀取、文字清理與分塊功能。

## 10. AI 協助與個人修改紀錄
- AI 協助：協助規劃欄位、JSON Schema、Streamlit 介面與錯誤檢查。
- 自己修改：請填寫實際修改的程式內容。
- 親自驗證：請填寫自己實際執行與核對的測試。

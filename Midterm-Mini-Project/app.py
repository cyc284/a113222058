import json
import os

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

APP_TITLE = "AI 課堂筆記整理器"
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5.4-mini")

INSTRUCTIONS = """
你是一個協助大學生整理課堂筆記的助手。
請只根據使用者提供的原始筆記整理，不可以自行補充原文沒有的事實、
人物、日期、數字、定義或例子。
如果原始筆記資訊不足，請在 summary 或 key_points 中清楚指出不足，
並在 missing_information 列出需要補充的資訊。
請使用繁體中文，內容清楚、簡單，適合大學生複習。
"""

SCHEMA = {
    "type": "object",
    "properties": {
        "title": {
            "type": "string",
            "description": "根據原始筆記產生的簡短課堂筆記標題"
        },
        "summary": {
            "type": "string",
            "description": "根據原始筆記整理的內容摘要"
        },
        "key_points": {
            "type": "array",
            "items": {"type": "string"},
            "description": "課堂重要觀念，每個項目一個重點"
        },
        "keywords": {
            "type": "array",
            "items": {"type": "string"},
            "description": "方便搜尋與複習的關鍵字"
        },
        "review_questions": {
            "type": "array",
            "items": {"type": "string"},
            "description": "根據原文設計的複習問題；資訊不足時可詢問需要補充的內容"
        },
        "missing_information": {
            "type": "array",
            "items": {"type": "string"},
            "description": "原始筆記中缺少、無法確認或需要補充的資訊；沒有則回傳空陣列"
        }
    },
    "required": [
        "title",
        "summary",
        "key_points",
        "keywords",
        "review_questions",
        "missing_information"
    ],
    "additionalProperties": False
}

FIELD_LABELS = {
    "title": "筆記標題",
    "summary": "內容摘要",
    "key_points": "重點整理",
    "keywords": "關鍵字",
    "review_questions": "複習問題",
    "missing_information": "需要補充的資訊"
}


def get_api_key():
    """先讀取 Streamlit Cloud Secrets，再讀取本機環境變數。"""
    try:
        key = st.secrets.get("OPENAI_API_KEY", "")
    except Exception:
        key = ""

    if not key:
        key = os.getenv("OPENAI_API_KEY", "")

    return key


def check_result(data):
    """在顯示結果前，再檢查一次欄位與資料型別。"""
    required_keys = set(SCHEMA["required"])

    if not isinstance(data, dict):
        raise ValueError("模型回應不是物件格式。")

    if set(data.keys()) != required_keys:
        raise ValueError("模型回應欄位不完整或包含多餘欄位。")

    for key in ["title", "summary"]:
        if not isinstance(data[key], str):
            raise ValueError(f"{FIELD_LABELS[key]}格式錯誤。")

    for key in [
        "key_points",
        "keywords",
        "review_questions",
        "missing_information"
    ]:
        if not isinstance(data[key], list):
            raise ValueError(f"{FIELD_LABELS[key]}格式錯誤。")
        if not all(isinstance(item, str) for item in data[key]):
            raise ValueError(f"{FIELD_LABELS[key]}必須全部是文字。")


def organize_notes(course_name, notes, api_key):
    client = OpenAI(
        api_key=api_key,
        timeout=60.0,
        max_retries=0
    )

    user_input = f"""
課程名稱：{course_name}

以下是學生提供的原始課堂筆記：
{notes}

請依照指定欄位整理。不要加入原文沒有的資訊。
"""

    response = client.responses.create(
        model=OPENAI_MODEL,
        input=[
            {"role": "system", "content": INSTRUCTIONS},
            {"role": "user", "content": user_input}
        ],
        text={
            "format": {
                "type": "json_schema",
                "name": "class_notes",
                "strict": True,
                "schema": SCHEMA
            }
        }
    )

    if response.status != "completed":
        raise ValueError(f"模型回應未完成，狀態：{response.status}")

    output_text = response.output_text

    if not output_text or not output_text.strip():
        raise ValueError("模型沒有回傳可用文字，可能是拒答或回應不完整。")

    data = json.loads(output_text)
    check_result(data)
    return data


st.set_page_config(
    page_title=APP_TITLE,
    page_icon="📚",
    layout="centered"
)

st.title("📚 AI 課堂筆記整理器")
st.write("貼上課堂筆記，AI 會協助整理摘要、重點、關鍵字與複習問題。")
st.caption("整理結果只根據你貼上的原文；請自行核對重要資訊。")

if "record" not in st.session_state:
    st.session_state.record = None

if "error" not in st.session_state:
    st.session_state.error = None

api_enabled = st.checkbox(
    "啟用 OpenAI API（預設關閉；開啟並送出有效資料才會請求）",
    value=False
)

with st.form("notes_form"):
    course_name = st.text_input(
        "課程名稱",
        placeholder="例如：網路實務（一）"
    )

    notes = st.text_area(
        "原始課堂筆記",
        height=260,
        placeholder="請貼上今天上課的筆記內容，最多 6000 個字元。"
    )

    submitted = st.form_submit_button(
        "整理我的筆記",
        type="primary",
        use_container_width=True
    )

if submitted:
    # 新提交先清除舊結果，避免失敗時舊結果被誤認為新結果。
    st.session_state.record = None
    st.session_state.error = None

    clean_course = course_name.strip()
    clean_notes = notes.strip()

    if not clean_course:
        st.session_state.error = "請先輸入課程名稱。"
    elif not clean_notes:
        st.session_state.error = "原始筆記不可空白。"
    elif len(clean_notes) > 6000:
        st.session_state.error = "原始筆記超過 6000 個字元，請縮短後再提交。"
    elif not api_enabled:
        st.session_state.error = "目前 API 開關是關閉的。請確認要使用 API 後，再開啟並重新提交。"
    else:
        api_key = get_api_key()

        if not api_key:
            st.session_state.error = "找不到 API 金鑰。請設定本機 .env 或 Streamlit Cloud Secrets。"
        else:
            try:
                with st.spinner("AI 正在整理課堂筆記，請稍候..."):
                    result = organize_notes(
                        clean_course,
                        clean_notes,
                        api_key
                    )

                st.session_state.record = {
                    "course_name": clean_course,
                    "original_notes": clean_notes,
                    "data": result
                }

            except json.JSONDecodeError:
                st.session_state.error = "回應無法解析成 JSON，這次結果不會顯示為成功。"
            except Exception as exc:
                st.session_state.error = (
                    f"處理失敗（{type(exc).__name__}）：{exc}"
                )

if st.session_state.error:
    st.error(st.session_state.error)

if st.session_state.record:
    record = st.session_state.record
    data = record["data"]

    st.success("筆記整理完成！")

    st.subheader("整理結果")
    st.write(f"**課程：** {record['course_name']}")
    st.write(f"**原始筆記：**\n\n{record['original_notes']}")

    st.divider()

    st.subheader(data["title"])
    st.markdown("### 內容摘要")
    st.write(data["summary"])

    st.markdown("### 重點整理")
    if data["key_points"]:
        for point in data["key_points"]:
            st.markdown(f"- {point}")
    else:
        st.write("原文沒有足夠資訊整理重點。")

    st.markdown("### 關鍵字")
    if data["keywords"]:
        st.write("、".join(data["keywords"]))
    else:
        st.write("沒有可辨識的關鍵字。")

    st.markdown("### 複習問題")
    if data["review_questions"]:
        for index, question in enumerate(data["review_questions"], start=1):
            st.write(f"{index}. {question}")
    else:
        st.write("目前沒有可產生的複習問題。")

    st.markdown("### 需要補充的資訊")
    if data["missing_information"]:
        for item in data["missing_information"]:
            st.markdown(f"- {item}")
    else:
        st.write("沒有特別指出需要補充的資訊。")

    with st.expander("查看結構化 JSON 原始結果"):
        st.json(data)

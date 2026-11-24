import os
import requests
import streamlit as st

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")

st.set_page_config(
    page_title="GuardSQL Enterprise | AI-to-SQL Security Gateway",
    page_icon="🛡️",
    layout="wide",
)

TEXTS = {
    "tr": {
        "title": "🛡️ GuardSQL Enterprise — Kurumsal AI-to-SQL Güvenlik Duvarı",
        "subtitle": "Doğal dil sorgularını AST analizi, Sütun Seviyesi RBAC, DDL/DML Koruması ve Maliyet Limitleri ile denetleyin.",
        "sidebar_header": "🏢 Kiracı & Rol Kontrolü",
        "seed_btn": "⚡ Demo Ortamını Başlat (Acme Finans A.Ş.)",
        "seed_ok": "Demo ortamı aktif! Kiracı: Acme Finans A.Ş.",
        "api_key_lbl": "Kiracı API Anahtarı (X-API-Key)",
        "role_lbl": "Aktif Kullanıcı Rolü Seçin",
        "analyst_opt": "Finance_Analyst (Sınırlı Yetki — Maaş Tablosu Kapalı)",
        "admin_opt": "Risk_Admin (Tam Denetim Yetkisi — Maaş Tablosu Açık)",
        "presets_lbl": "🎯 Tek Tıkla Test Senaryoları",
        "p_ok": "✅ Yetkili Sorgu: Son siparişleri getir",
        "p_rbac": "🚫 RBAC İhlali: Tüm çalışan maaşlarını göster",
        "p_ddl": "🔥 Siber Saldırı: Kullanıcı tablosunu sil (DROP TABLE)",
        "p_star": "⚠️ Veri Sızıntısı: Tüm sütunları getir (SELECT *)",
        "prompt_lbl": "Doğal Dil Sorgunuzu Yazın",
        "exec_chk": "Onaylanırsa veritabanında çalıştır ve önizleme getir",
        "run_btn": "🚀 Güvenlik Denetiminden Geçir ve Çalıştır",
        "sql_hdr": "🧠 Üretilen SQL Sorgusu",
        "res_hdr": "🛡️ AST Güvenlik Duvarı Kararı",
        "prev_hdr": "📊 Canlı Veri Önizlemesi",
        "audit_hdr": "📜 Kurumsal Denetim Kayıtları (Audit Logs)",
        "refresh_btn": "🔄 Kayıtları Yenile",
        "err_conn": "Backend API bağlantısı kurulamadı. Önce FastAPI sunucusunu başlatın.",
    },
    "en": {
        "title": "🛡️ GuardSQL Enterprise — AI-to-SQL Security Gateway",
        "subtitle": "Govern natural language database queries with AST parsing, Column-Level RBAC, DDL/DML Blocking, and Cost Guardrails.",
        "sidebar_header": "🏢 Tenant & Role Control",
        "seed_btn": "⚡ Initialize Demo Tenant (Acme Finance Inc.)",
        "seed_ok": "Demo environment ready! Tenant: Acme Finance Inc.",
        "api_key_lbl": "Tenant API Key (X-API-Key)",
        "role_lbl": "Select Active User Role",
        "analyst_opt": "Finance_Analyst (Restricted — HR Salaries Blocked)",
        "admin_opt": "Risk_Admin (Full Audit Access — HR Salaries Allowed)",
        "presets_lbl": "🎯 One-Click Attack & Policy Scenarios",
        "p_ok": "✅ Authorized Query: Show recent orders",
        "p_rbac": "🚫 RBAC Violation: Show all employee salaries",
        "p_ddl": "🔥 Destructive Attack: Drop users table",
        "p_star": "⚠️ Data Leak Policy: Select all columns (SELECT *)",
        "prompt_lbl": "Enter Natural Language Query",
        "exec_chk": "Execute on database and return preview if APPROVED",
        "run_btn": "🚀 Validate & Execute Query",
        "sql_hdr": "🧠 Generated SQL Query",
        "res_hdr": "🛡️ AST Security Firewall Verdict",
        "prev_hdr": "📊 Live Data Preview",
        "audit_hdr": "📜 Enterprise Compliance Audit Logs",
        "refresh_btn": "🔄 Refresh Logs",
        "err_conn": "Cannot connect to Backend API. Please start the FastAPI server first.",
    },
}
lang = st.sidebar.radio("🌐 Language / Dil", ["tr", "en"], format_func=lambda x: "Türkçe (TR)" if x == "tr" else "English (EN)", horizontal=True)
t = TEXTS[lang]

st.title(t["title"])
st.caption(t["subtitle"])

if not st.session_state.get("seed_data"):
    try:
        r = requests.post(f"{API_BASE_URL}/api/v1/tenants/seed-demo", timeout=10)
        if r.status_code == 200:
            st.session_state["seed_data"] = r.json()
    except Exception:
        st.session_state["seed_data"] = None

st.sidebar.header(t["sidebar_header"])
if st.sidebar.button(t["seed_btn"], use_container_width=True):
    try:
        r = requests.post(f"{API_BASE_URL}/api/v1/tenants/seed-demo", timeout=10)
        if r.status_code == 200:
            st.session_state["seed_data"] = r.json()
            st.sidebar.success(t["seed_ok"])
    except Exception:
        st.sidebar.error(t["err_conn"])

seed_data = st.session_state.get("seed_data")
api_key = st.sidebar.text_input(t["api_key_lbl"], value="gsql_demo_secret_key_2026", type="password")
role_choice = st.sidebar.selectbox(t["role_lbl"], ["analyst", "admin"], format_func=lambda x: t["analyst_opt"] if x == "analyst" else t["admin_opt"])

if seed_data:
    active_user_id = seed_data["analyst_id"] if role_choice == "analyst" else seed_data["admin_id"]
    if role_choice == "analyst":
        st.sidebar.info("Allowed Schema:\n- `customers(id, full_name, city)`\n- `orders(id, customer_name, total_amount, status)`")
    else:
        st.sidebar.info("Allowed Schema:\n- `customers(id, full_name, city, email)`\n- `orders(...)`\n- `hr_salaries(id, employee_name, salary)`")
else:
    active_user_id = ""
    st.warning(t["err_conn"])

st.subheader(t["presets_lbl"])
c1, c2, c3, c4 = st.columns(4)
if "prompt_input" not in st.session_state:
    st.session_state["prompt_input"] = "son siparişleri getir" if lang == "tr" else "show recent orders"

if c1.button(t["p_ok"], use_container_width=True):
    st.session_state["prompt_input"] = "son siparişleri getir" if lang == "tr" else "show recent orders"
if c2.button(t["p_rbac"], use_container_width=True):
    st.session_state["prompt_input"] = "tüm çalışan maaşlarını göster" if lang == "tr" else "show all employee salaries"
if c3.button(t["p_ddl"], use_container_width=True):
    st.session_state["prompt_input"] = "kullanıcı tablosunu sil" if lang == "tr" else "drop users table"
if c4.button(t["p_star"], use_container_width=True):
    st.session_state["prompt_input"] = "tüm sütunları getir" if lang == "tr" else "select * from customers"

prompt = st.text_input(t["prompt_lbl"], key="prompt_input")
execute_query = st.checkbox(t["exec_chk"], value=True)

if st.button(t["run_btn"], type="primary") and seed_data:
    try:
        resp = requests.post(
            f"{API_BASE_URL}/api/v1/query/ask",
            headers={"X-API-Key": api_key},
            json={"user_id": active_user_id, "prompt": prompt, "execute_query": execute_query, "language": lang},
            timeout=10,
        )
        if resp.status_code == 200:
            res = resp.json()
            val = res["validation_result"]
            col_left, col_right = st.columns(2)
            with col_left:
                st.markdown(f"### {t['sql_hdr']}")
                st.code(res["generated_sql"], language="sql")
                st.caption(f"Tenant: **{res['tenant_name']}** | User: **{res['user_email']}** | Role: **{res['role_name']}** | Latency: **{res['execution_time_ms']} ms**")
            with col_right:
                st.markdown(f"### {t['res_hdr']}")
                if val["is_valid"]:
                    st.success(f"✅ **{val['status']}** (Estimated Cost: {val['estimated_cost']})")
                else:
                    st.error(f"🛑 **{val['status']}** — {val['block_reason']}")
            if res.get("execution_preview") is not None:
                st.markdown(f"### {t['prev_hdr']}")
                st.dataframe(res["execution_preview"], use_container_width=True)
        else:
            st.error(f"API Error ({resp.status_code}): {resp.text}")
    except Exception as exc:
        st.error(f"{t['err_conn']} ({exc})")

st.divider()
col_a1, col_a2 = st.columns([4, 1])
col_a1.subheader(t["audit_hdr"])
col_a2.button(t["refresh_btn"], use_container_width=True)

if seed_data:
    try:
        logs_resp = requests.get(f"{API_BASE_URL}/api/v1/query/audit-logs", headers={"X-API-Key": api_key}, timeout=10)
        if logs_resp.status_code == 200 and logs_resp.json():
            st.dataframe(logs_resp.json(), use_container_width=True)
    except Exception:
        pass
from openai import OpenAI
from app.core.config import settings


class TextToSQLService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None

    def generate_sql(self, prompt: str, schema_map: dict, dialect: str = "postgres") -> str:
        if settings.MOCK_LLM or not self.client:
            return self._mock_generate(prompt)

        try:
            system_prompt = (
                f"You are an enterprise SQL generator for {dialect}. "
                f"Use ONLY these allowed tables and columns: {schema_map}. "
                "Never use SELECT *. Return ONLY raw SQL without markdown formatting."
            )
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
                temperature=0,
            )
            raw = next(iter(response.choices)).message.content or ""
            return raw.replace("```sql", "").replace("```", "").strip()
        except Exception:
            return self._mock_generate(prompt)

    def _mock_generate(self, prompt: str) -> str:
        p = prompt.lower()
        if "sipariş" in p or "order" in p:
            return "SELECT id, customer_name, total_amount, status FROM orders LIMIT 10"
        if any(k in p for k in ("maaş", "salary", "salaries", "employee", "çalışan")):
            return "SELECT employee_name, salary FROM hr_salaries"
        if "sil" in p or "drop" in p:
            return "DROP TABLE users"
        if "tüm sütun" in p or "select *" in p:
            return "SELECT * FROM customers"
        return "SELECT id, full_name, city FROM customers LIMIT 10"
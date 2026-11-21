import os
from openai import OpenAI

class TextToSQLService:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.mock_llm = os.getenv("MOCK_LLM", "False").lower() == "true"
        self.client = OpenAI(api_key=self.api_key) if self.api_key else None

    def generate_sql(self, prompt: str, schema_map: dict) -> str:
        if self.mock_llm or not self.client:
            return self._mock_generate(prompt)
        
        # System Prompt construction
        system_prompt = f"You are a SQL expert. Given the schema: {schema_map}. Return only SQL."
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.replace("```sql", "").replace("```", "").strip()

    def _mock_generate(self, prompt: str) -> str:
        prompt_lower = prompt.lower()
        if "sipariş" in prompt_lower:
            return "SELECT * FROM orders LIMIT 5;"
        if "maaş" in prompt_lower:
            return "SELECT name, salary FROM hr_salaries;"
        if "sil" in prompt_lower or "drop" in prompt_lower:
            return "DROP TABLE users;" # Simulated bad query
        return "SELECT * FROM customers LIMIT 5;"

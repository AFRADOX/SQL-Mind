# # backend/app/services/llm_service.py

# from __future__ import annotations
# import json
# import logging
# import re
# from app.core.config import get_settings
# from app.schemas.schema import DatabaseSchema
# from app.services.schema_service import SchemaService

# logger = logging.getLogger(__name__)
# settings = get_settings()

# SYSTEM_PROMPT = """You are an expert PostgreSQL query writer.
# Your job is to convert natural language questions into valid read-only PostgreSQL SELECT statements.

# Rules:
# - ONLY generate SELECT statements. Never INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE.
# - Use ONLY the tables and columns from the provided schema.
# - Never invent table or column names.
# - If the question is ambiguous, pick the most sensible interpretation and document it.
# - Always add a LIMIT clause (max 500 rows) unless the user asks for aggregates.
# - Use table aliases for readability.

# Respond ONLY with valid JSON matching this exact structure (no markdown, no extra text):
# {
#   "sql": "SELECT ...",
#   "confidence": 85,
#   "explanation": "This query ...",
#   "assumptions": ["I assumed X means Y"],
#   "ambiguous": false,
#   "clarifying_question": null
# }

# confidence is 0-100. ambiguous is true if the question had multiple valid interpretations.
# clarifying_question is a string if you need more info, otherwise null.
# """


# class LLMService:
#     def __init__(self):
#         self.provider = settings.llm_provider

#     async def generate_sql(
#         self,
#         natural_language: str,
#         schema: DatabaseSchema,
#         conversation_history: list[dict] | None = None,
#     ) -> dict:
#         schema_str = SchemaService.schema_to_prompt_string(schema)
#         user_message = (
#             f"DATABASE SCHEMA:\n{schema_str}\n\n"
#             f"QUESTION: {natural_language}"
#         )
#         messages = []
#         if conversation_history:
#             messages.extend(conversation_history)
#         messages.append({"role": "user", "content": user_message})

#         if self.provider == "gemini":
#             return await self._call_gemini(messages)
#         return await self._call_openai(messages)

#     async def _call_gemini(self, messages: list[dict]) -> dict:
#         import google.generativeai as genai
#         genai.configure(api_key=settings.gemini_api_key)
#         model = genai.GenerativeModel(
#             model_name=settings.gemini_model,
#             system_instruction=SYSTEM_PROMPT,
#             generation_config=genai.GenerationConfig(
#                 temperature=settings.llm_temperature,
#                 max_output_tokens=settings.llm_max_tokens,
#             ),
#         )
#         history = []
#         last_message = messages[-1]["content"]
#         for msg in messages[:-1]:
#             role = "user" if msg["role"] == "user" else "model"
#             history.append({"role": role, "parts": [msg["content"]]})

#         chat = model.start_chat(history=history)
#         response = chat.send_message(last_message)
#         return self._parse_response(response.text)

#     async def _call_openai(self, messages: list[dict]) -> dict:
#         from openai import AsyncOpenAI
#         client = AsyncOpenAI(api_key=settings.openai_api_key)
#         full_messages = [
#             {"role": "system", "content": SYSTEM_PROMPT}
#         ] + messages
#         response = await client.chat.completions.create(
#             model=settings.openai_model,
#             messages=full_messages,
#             temperature=settings.llm_temperature,
#             max_tokens=settings.llm_max_tokens,
#             timeout=settings.llm_timeout_seconds,
#         )
#         return self._parse_response(response.choices[0].message.content)

#     def _parse_response(self, raw: str) -> dict:
#         cleaned = re.sub(r"```(?:json)?|```", "", raw).strip()
#         try:
#             return json.loads(cleaned)
#         except json.JSONDecodeError as e:
#             logger.error("LLM returned non-JSON: %s", raw)
#             raise ValueError(f"LLM response was not valid JSON: {e}")

# backend/app/services/llm_service.py

from __future__ import annotations
import json
import logging
import re
from app.core.config import get_settings
from app.schemas.schema import DatabaseSchema
from app.services.schema_service import SchemaService

logger = logging.getLogger(__name__)
settings = get_settings()

SYSTEM_PROMPT = """You are an expert PostgreSQL query writer.
Your job is to convert natural language questions into valid read-only PostgreSQL SELECT statements.

Rules:
- ONLY generate SELECT statements. Never INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE.
- Use ONLY the tables and columns from the provided schema.
- Never invent table or column names.
- If the question is ambiguous, pick the most sensible interpretation and document it.
- Always add a LIMIT clause (max 500 rows) unless the user asks for aggregates.
- Use table aliases for readability.

Respond ONLY with valid JSON matching this exact structure (no markdown, no extra text):
{
  "sql": "SELECT ...",
  "confidence": 85,
  "explanation": "This query ...",
  "assumptions": ["I assumed X means Y"],
  "ambiguous": false,
  "clarifying_question": null
}

confidence is 0-100. ambiguous is true if the question had multiple valid interpretations.
clarifying_question is a string if you need more info, otherwise null.
"""


class LLMService:
    def __init__(self):
        self.provider = settings.llm_provider

    async def generate_sql(
        self,
        natural_language: str,
        schema: DatabaseSchema,
        conversation_history: list[dict] | None = None,
    ) -> dict:
        schema_str = SchemaService.schema_to_prompt_string(schema)
        user_message = (
            f"DATABASE SCHEMA:\n{schema_str}\n\n"
            f"QUESTION: {natural_language}"
        )
        messages = []
        if conversation_history:
            messages.extend(conversation_history)
        messages.append({"role": "user", "content": user_message})

        if self.provider == "groq":
            return await self._call_groq(messages)
        elif self.provider == "gemini":
            return await self._call_gemini(messages)
        return await self._call_openai(messages)

    async def _call_groq(self, messages: list[dict]) -> dict:
        from groq import Groq
        client = Groq(api_key=settings.groq_api_key)
        full_messages = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ] + messages
        response = client.chat.completions.create(
            model=settings.groq_model,
            messages=full_messages,
            temperature=settings.llm_temperature,
            max_tokens=settings.llm_max_tokens,
        )
        return self._parse_response(response.choices[0].message.content)

    async def _call_gemini(self, messages: list[dict]) -> dict:
        import google.generativeai as genai
        genai.configure(api_key=settings.gemini_api_key)
        model = genai.GenerativeModel(
            model_name=settings.gemini_model,
            system_instruction=SYSTEM_PROMPT,
            generation_config=genai.GenerationConfig(
                temperature=settings.llm_temperature,
                max_output_tokens=settings.llm_max_tokens,
            ),
        )
        history = []
        last_message = messages[-1]["content"]
        for msg in messages[:-1]:
            role = "user" if msg["role"] == "user" else "model"
            history.append({"role": role, "parts": [msg["content"]]})
        chat = model.start_chat(history=history)
        response = chat.send_message(last_message)
        return self._parse_response(response.text)

    async def _call_openai(self, messages: list[dict]) -> dict:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=settings.openai_api_key)
        full_messages = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ] + messages
        response = await client.chat.completions.create(
            model=settings.openai_model,
            messages=full_messages,
            temperature=settings.llm_temperature,
            max_tokens=settings.llm_max_tokens,
            timeout=settings.llm_timeout_seconds,
        )
        return self._parse_response(response.choices[0].message.content)

    def _parse_response(self, raw: str) -> dict:
        cleaned = re.sub(r"```(?:json)?|```", "", raw).strip()
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            logger.error("LLM returned non-JSON: %s", raw)
            raise ValueError(f"LLM response was not valid JSON: {e}")
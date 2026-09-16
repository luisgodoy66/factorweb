# factoring/services/ai_invoice_analyzer.py

from openai import OpenAI
from django.conf import settings
from django.contrib import messages
API = settings.OPENAI_API_KEY

def build_prompt(invoice, client_history, debtor_history):
    return f"""
Eres un analista financiero experto en factoring.

Evalúa la siguiente factura y su contexto histórico.

Factura:
- Monto: {invoice.ntotal }
- Emisión: {invoice.demision}
- Fecha de vencimiento: {invoice.dvencimiento}
- Cliente: {invoice.cxasignacion.cxcliente}
- Deudor: {invoice.ctcomprador}

Historial del cliente:
{client_history}

Historial del deudor:
{debtor_history}

Devuelve la respuesta en JSON con esta estructura:
{{
  "risk_level": "BAJO | MEDIO | ALTO",
  "analysis": "texto claro",
  "recommendation": "recomendación operativa"
}}
"""

def analyze_invoice_with_ai(invoice, client_history, debtor_history):

    prompt = build_prompt(invoice, client_history, debtor_history)
    print(prompt)
    cliente = OpenAI(
        api_key=API
    )
    try:
        # response = client.chat.completions.create(
        #     model="gpt-4o-mini",
        #     messages=[
        #         {"role": "system", "content": "Eres un experto en análisis de riesgo financiero."},
        #         {"role": "user", "content": prompt},
        #     ],
        #     temperature=0.2,
        # )

        # content = response.choices[0].message.content
        response = cliente.responses.create(
            model="gpt-4.1",
            instructions="Eres un experto en análisis de riesgo financiero.",
            temperature=0,
            top_p=1.0,
            input=prompt
        )
        content = response.output_text.strip()

        return content
    except Exception as e:
        print(e)
        return None

import json


def parse_ai_response(content: str) -> dict:
    try:
        data = json.loads(content)
        return {
            "risk_level": data.get("risk_level", "MEDIO"),
            "analysis": data.get("analysis", ""),
            "recommendation": data.get("recommendation", ""),
            "raw": data,
        }
    except json.JSONDecodeError:
        return {
            "risk_level": "MEDIO",
            "analysis": content,
            "recommendation": "Revisión manual recomendada.",
            "raw": {"error": "invalid_json"},
        }

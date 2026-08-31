INSUFFICIENT_EVIDENCE_MESSAGE = (
    "I don't have enough evidence in the indexed "
    "documents to answer that question."
)


def build_grounded_prompt(
    question: str,
    context: str,
) -> str:
    """Build a structured prompt restricted to retrieved evidence."""

    if not question.strip():
        raise ValueError(
            "question cannot be empty."
        )

    if not context.strip():
        raise ValueError(
            "context cannot be empty."
        )

    return f"""You are the grounded answer-generation component of NexusRAG.

Use ONLY the supplied context.

Rules:

1. Do not use outside knowledge.
2. Do not invent facts.
3. Do not explain your reasoning.
4. Do not output analysis.
5. Return ONLY valid JSON.
6. Citations must reference source numbers that exist in the context.
7. Use the minimum number of citations required to support the answer.

Your JSON response must use exactly this structure:

{{
  "answer": "Concise final answer",
  "citations": [1],
  "insufficient_evidence": false
}}

If the context does not contain enough evidence, return exactly:

{{
  "answer": "{INSUFFICIENT_EVIDENCE_MESSAGE}",
  "citations": [],
  "insufficient_evidence": true
}}

CONTEXT:

{context}

QUESTION:

{question}

Return only the JSON object.
"""
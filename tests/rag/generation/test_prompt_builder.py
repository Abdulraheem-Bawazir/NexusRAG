import pytest

from app.rag.generation import (
    INSUFFICIENT_EVIDENCE_MESSAGE,
    build_grounded_prompt,
)


def test_prompt_contains_question_and_context() -> None:
    prompt = build_grounded_prompt(
        question="Can I work remotely?",
        context=(
            "[1]\n"
            "Source: policy.txt\n"
            "Content:\n"
            "Remote work is allowed."
        ),
    )

    assert "Can I work remotely?" in prompt
    assert "Remote work is allowed." in prompt
    assert "[1]" in prompt


def test_prompt_requires_structured_json() -> None:
    prompt = build_grounded_prompt(
        question="Question",
        context="[1] Evidence",
    )

    assert "Return ONLY valid JSON" in prompt
    assert '"answer"' in prompt
    assert '"citations"' in prompt
    assert '"insufficient_evidence"' in prompt


def test_prompt_contains_grounding_rules() -> None:
    prompt = build_grounded_prompt(
        question="Question",
        context="[1] Evidence",
    )

    assert "Do not use outside knowledge" in prompt

    assert (
        INSUFFICIENT_EVIDENCE_MESSAGE
        in prompt
    )


def test_empty_question_is_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="question cannot be empty",
    ):
        build_grounded_prompt(
            question="   ",
            context="Evidence",
        )


def test_empty_context_is_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="context cannot be empty",
    ):
        build_grounded_prompt(
            question="Question",
            context="   ",
        )
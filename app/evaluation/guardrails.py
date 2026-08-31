from app.models.rag_answer import RAGAnswer


def unsupported_question_handled_correctly(
    answer: RAGAnswer,
) -> bool:
    """Check that an unsupported question produced no citations."""

    return (
        answer.insufficient_evidence
        and not answer.citations
    )


def answerable_question_handled_correctly(
    answer: RAGAnswer,
) -> bool:
    """Check that a supported answer is grounded by citations."""

    return (
        not answer.insufficient_evidence
        and bool(answer.answer.strip())
        and bool(answer.citations)
    )
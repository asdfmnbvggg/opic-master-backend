from __future__ import annotations

from typing import Any

CATEGORY_LABELS_KO = {
    "grammar": "문법",
    "fluency": "유창성",
    "vocabulary": "어휘",
    "completion": "답변 완성도",
    "relevance": "질문 적합도",
    "speed": "속도",
    "engagement": "호응 유도",
}


def build_answer_feedback(
    *,
    question_text: str,
    transcript: str,
    metrics: dict[str, float | int | bool],
) -> dict[str, Any]:
    normalized_transcript = transcript.strip()
    word_count = int(metrics["word_count"])
    speech_rate_wpm = float(metrics["speech_rate_wpm"])
    keyword_similarity = float(metrics["keyword_similarity"])
    repetition_rate = float(metrics["repetition_rate"])
    lexical_diversity = float(metrics["lexical_diversity"])
    too_short = bool(metrics["too_short"])
    too_much_silence = bool(metrics["too_much_silence"])
    is_gradable = bool(metrics["is_gradable"])

    if not normalized_transcript or word_count == 0:
        return _build_empty_answer_feedback()

    strengths: list[str] = []
    weaknesses: list[str] = []
    tips: list[str] = []

    if keyword_similarity >= 0.45:
        strengths.append("질문의 핵심을 벗어나지 않고 주제에 맞게 답변하고 있습니다.")
    else:
        weaknesses.append("질문과 직접적으로 연결되는 답변이 더 필요합니다.")
        tips.append("첫 문장에 질문의 핵심 키워드를 한두 개 넣어보세요.")

    if lexical_diversity >= 0.65:
        strengths.append("답변 길이에 비해 어휘 사용이 비교적 다양합니다.")
    else:
        weaknesses.append("같은 단어와 표현이 반복되는 부분이 있습니다.")
        tips.append("반복되는 기본 단어를 다른 표현으로 한두 개 바꿔보세요.")

    if 90 <= speech_rate_wpm <= 170:
        strengths.append("말하기 속도가 비교적 자연스럽고 안정적입니다.")
    elif speech_rate_wpm > 170:
        weaknesses.append("말이 다소 빨라서 전달력이 떨어질 수 있습니다.")
        tips.append("조금만 천천히 말하고 생각 단위마다 짧게 끊어보세요.")
    else:
        weaknesses.append("속도가 느려서 망설이는 인상으로 들릴 수 있습니다.")
        tips.append("생각을 짧은 덩어리로 나누고 멈추지 말고 이어서 말해보세요.")

    if repetition_rate <= 0.16:
        strengths.append("반복 표현 사용이 비교적 잘 억제되어 있습니다.")
    else:
        weaknesses.append("같은 표현이나 추임새가 자주 반복됩니다.")
        tips.append("같은 시작 표현 대신 바꿔 쓸 연결 표현을 두세 개 준비해보세요.")

    if too_short:
        weaknesses.append("답변이 짧아서 안정적인 평가가 어렵습니다.")
        tips.append("답변, 이유, 예시의 세 덩어리로 말하는 연습을 해보세요.")

    if too_much_silence:
        weaknesses.append("침묵 구간이 많거나 실제 발화량이 부족합니다.")
        tips.append("한 문장으로 멈추지 말고 간단한 설명을 덧붙이며 이어서 말해보세요.")

    if not strengths:
        strengths.append("기본적인 답변 틀은 갖추고 있어, 디테일을 보강하면 더 좋아질 수 있습니다.")

    if not weaknesses and is_gradable:
        weaknesses.append("구체적인 예시를 한 가지 더 넣으면 답변이 더 좋아질 수 있습니다.")

    estimated_sub_grade = _estimate_sub_grade(metrics)

    question_relevance_text = (
        "답변이 질문과 잘 맞아 있습니다."
        if keyword_similarity >= 0.45
        else "답변이 질문을 부분적으로만 반영하고 있습니다."
    )
    sentence_length_text = (
        "문장 길이가 비교적 적절해서 전달이 잘 됩니다."
        if float(metrics["avg_sentence_length"]) >= 7
        else "문장이 짧아서 답변이 충분히 전개되지 않은 느낌이 있습니다."
    )
    answer_time_text = (
        "답변 길이가 채점하기에 충분합니다."
        if not too_short
        else "답변 길이가 짧아 신뢰도 높은 채점이 어렵습니다."
    )
    repetition_text = (
        "반복 표현 사용이 비교적 안정적입니다."
        if repetition_rate <= 0.16
        else "같은 단어와 패턴의 반복이 눈에 띕니다."
    )
    keyword_similarity_text = (
        "질문 키워드가 답변에 잘 반영되어 있습니다."
        if keyword_similarity >= 0.45
        else "질문의 중요한 키워드가 답변에 충분히 반영되지 않았습니다."
    )

    scores = {
        "grammar": _bounded_score(55 + min(word_count, 80) * 0.3 - repetition_rate * 20 - (12 if too_short else 0)),
        "fluency": _bounded_score(58 + min(speech_rate_wpm, 180) * 0.18 - (10 if too_much_silence else 0)),
        "vocabulary": _bounded_score(54 + lexical_diversity * 35 - repetition_rate * 15),
        "completion": _bounded_score(50 + keyword_similarity * 30 + min(word_count, 60) * 0.35 - (15 if too_short else 0)),
        "relevance": _bounded_score(50 + keyword_similarity * 45),
        "speed": _bounded_score(65 - abs(130 - speech_rate_wpm) * 0.35 - (8 if too_much_silence else 0)),
        "engagement": _bounded_score(55 + min(word_count, 70) * 0.25 + lexical_diversity * 10),
    }

    if not is_gradable:
        scores = {key: min(value, 55) for key, value in scores.items()}

    feedback = {
        "grammar": (
            "전체적으로 이해 가능한 문장 구성이지만, 긴 문장 제어는 더 다듬을 필요가 있습니다."
            if word_count >= 20
            else "문법을 안정적으로 판단하기에는 발화 샘플이 부족합니다."
        ),
        "fluency": (
            "전체적으로는 비교적 자연스럽게 이어집니다."
            if not too_much_silence and 90 <= speech_rate_wpm <= 170
            else "멈춤이나 속도 문제 때문에 유창성이 떨어집니다."
        ),
        "vocabulary": (
            "주제에 맞는 어휘 사용이 비교적 잘 이루어졌습니다."
            if lexical_diversity >= 0.65
            else "같은 단어를 반복하기보다 더 다양한 어휘를 써보는 것이 좋습니다."
        ),
        "completion": (
            "질문을 충분한 디테일로 비교적 잘 답하고 있습니다."
            if not too_short and keyword_similarity >= 0.45
            else "답변을 더 길게 전개하거나 질문과 더 밀접하게 맞출 필요가 있습니다."
        ),
        "relevance": question_relevance_text,
        "speed": (
            "말하기 속도가 자연스러운 편입니다."
            if 90 <= speech_rate_wpm <= 170
            else "더 자연스럽게 들리도록 속도 조절이 필요합니다."
        ),
        "sentenceLength": sentence_length_text,
        "repetition": repetition_text,
        "engagement": (
            "답변에 변화와 디테일이 있어 비교적 집중을 끌 수 있습니다."
            if word_count >= 35
            else "예시나 반응, 대비 표현을 넣으면 더 생동감 있는 답변이 됩니다."
        ),
        "answerTime": answer_time_text,
        "keywordSimilarity": keyword_similarity_text,
    }

    if not is_gradable:
        if too_short:
            tips.insert(0, "답변이 짧아 정확한 평가가 어렵습니다.")
        if too_much_silence:
            tips.insert(0, "침묵 구간이 많아 피드백의 신뢰도가 제한됩니다.")

    while len(tips) < 3:
        tips.append("구체적인 예시를 한 가지 더 넣어 답변을 풍부하게 만들어보세요.")

    return {
        "strengths": strengths[:4],
        "weaknesses": weaknesses[:4],
        "scores": scores,
        "feedback": feedback,
        "tips": tips[:4],
        "estimatedSubGrade": estimated_sub_grade,
        "tooShort": too_short,
        "tooMuchSilence": too_much_silence,
        "questionRelevance": question_relevance_text,
        "sentenceLength": sentence_length_text,
        "answerTime": answer_time_text,
        "repetitionRate": repetition_text,
        "keywordSimilarity": keyword_similarity_text,
    }


def build_session_summary(answer_feedback: list[dict[str, Any]]) -> dict[str, Any]:
    if not answer_feedback:
        return {
            "strengths": [],
            "weaknesses": ["전체 요약을 보려면 최소 한 개 이상의 답변이 필요합니다."],
            "feedback": {"summary": "아직 전체 요약을 만들 수 없습니다."},
            "tips": ["한 문제 이상 답변한 뒤 다시 확인해보세요."],
            "categoryScores": {
                "grammar": 0,
                "fluency": 0,
                "vocabulary": 0,
                "completion": 0,
                "relevance": 0,
                "speed": 0,
                "engagement": 0,
            },
            "estimatedGrade": "데이터 부족",
            "isGradable": False,
        }

    strengths: list[str] = []
    weaknesses: list[str] = []
    tips: list[str] = []
    score_buckets: dict[str, list[int]] = {
        "grammar": [],
        "fluency": [],
        "vocabulary": [],
        "completion": [],
        "relevance": [],
        "speed": [],
        "engagement": [],
    }
    is_gradable = True
    gradable_answer_count = 0

    for item in answer_feedback:
        strengths.extend(item.get("strengths", []))
        weaknesses.extend(item.get("weaknesses", []))
        tips.extend(item.get("tips", []))
        answer_is_gradable = not item.get("tooShort", False) and not item.get("tooMuchSilence", False)
        if answer_is_gradable:
            gradable_answer_count += 1
        is_gradable = is_gradable and answer_is_gradable
        scores = item.get("scores", {})
        for key in score_buckets:
            value = scores.get(key)
            if isinstance(value, int):
                score_buckets[key].append(value)

    if gradable_answer_count == 0:
        return {
            "strengths": [],
            "weaknesses": _unique_items(weaknesses)[:4]
            or [
                "말한 내용이 거의 없거나 침묵 구간이 많아 전체 강점과 약점을 신뢰도 있게 판단하기 어렵습니다.",
            ],
            "feedback": {
                "summary": "채점 가능한 답변이 없어 전체 평가가 제한되었습니다.",
                "focus": "최소 2~3문장 이상 답변한 뒤 다시 평가해보세요.",
            },
            "tips": _unique_items(tips)[:4]
            or [
                "질문에 대한 이유와 예시를 함께 말해 답변 길이를 늘려보세요.",
                "침묵이 길어지지 않도록 짧은 설명이라도 이어서 말해보세요.",
            ],
            "categoryScores": {
                "grammar": 0,
                "fluency": 0,
                "vocabulary": 0,
                "completion": 0,
                "relevance": 0,
                "speed": 0,
                "engagement": 0,
            },
            "estimatedGrade": "채점 제한",
            "isGradable": False,
        }

    averaged_scores = {
        key: round(sum(values) / len(values)) if values else 0
        for key, values in score_buckets.items()
    }
    estimated_grade = _estimate_grade_from_average(averaged_scores)
    feedback = {
        "summary": (
            "전체적인 답변 흐름이 비교적 안정적이며 채점 가능한 수준입니다."
            if is_gradable
            else "일부 답변이 너무 짧거나 불완전해 전체 평가는 보수적으로 계산되었습니다."
        ),
        "focus": _pick_focus_area(averaged_scores),
    }

    return {
        "strengths": _unique_items(strengths)[:4] or ["전반적으로 이해 가능하고 정돈된 답변 흐름을 유지하고 있습니다."],
        "weaknesses": _unique_items(weaknesses)[:4] or ["답변의 디테일과 다양성을 더 보강하면 전체 점수가 좋아질 수 있습니다."],
        "feedback": feedback,
        "tips": _unique_items(tips)[:4] or ["모든 답변에 이유 하나와 예시 하나를 넣는 연습을 해보세요."],
        "categoryScores": averaged_scores,
        "estimatedGrade": estimated_grade,
        "isGradable": is_gradable,
    }


def _build_empty_answer_feedback() -> dict[str, Any]:
    message = "답변이 인식되지 않아 평가할 수 없습니다."
    return {
        "strengths": [],
        "weaknesses": [
            "말한 내용이 없거나 STT가 인식할 수 있는 발화가 거의 없었습니다.",
            "이 상태에서는 문법, 유창성, 어휘를 신뢰도 있게 평가할 수 없습니다.",
        ],
        "scores": {
            "grammar": 0,
            "fluency": 0,
            "vocabulary": 0,
            "completion": 0,
            "relevance": 0,
            "speed": 0,
            "engagement": 0,
        },
        "feedback": {
            "grammar": message,
            "fluency": message,
            "vocabulary": message,
            "completion": "답변이 거의 없어 질문에 대한 완성도를 판단할 수 없습니다.",
            "relevance": "질문과의 관련성을 판단할 수 있는 답변이 없습니다.",
            "speed": "실제 발화가 거의 없어 속도를 계산할 수 없습니다.",
            "sentenceLength": "문장 길이를 판단할 수 있는 발화가 없습니다.",
            "repetition": "반복 표현을 평가할 수 있는 발화가 없습니다.",
            "engagement": "호응 유도나 전달력을 판단할 수 있는 답변이 없습니다.",
            "answerTime": "답변이 거의 없어 답변 시간을 평가할 수 없습니다.",
            "keywordSimilarity": "질문 키워드와 비교할 답변 내용이 없습니다.",
        },
        "tips": [
            "최소 2~3문장 이상 말한 뒤 다시 평가해보세요.",
            "짧게라도 질문에 대한 이유와 예시를 함께 말해보세요.",
            "침묵이 길어지지 않도록 간단한 설명을 이어서 말해보세요.",
        ],
        "estimatedSubGrade": "채점 제한",
        "tooShort": True,
        "tooMuchSilence": True,
        "questionRelevance": "답변이 없어 질문 적합도를 판단할 수 없습니다.",
        "sentenceLength": "답변이 없어 문장 길이를 판단할 수 없습니다.",
        "answerTime": "답변이 없어 답변 시간을 판단할 수 없습니다.",
        "repetitionRate": "답변이 없어 반복 표현 사용률을 판단할 수 없습니다.",
        "keywordSimilarity": "답변이 없어 키워드 유사도를 판단할 수 없습니다.",
    }


def _estimate_sub_grade(metrics: dict[str, float | int | bool]) -> str:
    if not bool(metrics["is_gradable"]):
        return "채점 제한"

    weighted_score = (
        float(metrics["keyword_similarity"]) * 30
        + float(metrics["lexical_diversity"]) * 25
        + max(0.0, 1 - float(metrics["repetition_rate"])) * 20
        + min(float(metrics["speech_rate_wpm"]) / 150, 1.0) * 15
        + min(int(metrics["word_count"]) / 60, 1.0) * 10
    ) * 100 / 100

    if weighted_score >= 78:
        return "AL"
    if weighted_score >= 68:
        return "IH"
    if weighted_score >= 58:
        return "IM3"
    return "IM2"


def _estimate_grade_from_average(scores: dict[str, int]) -> str:
    if not scores:
        return "데이터 부족"

    average = sum(scores.values()) / len(scores)
    if average >= 82:
        return "AL"
    if average >= 72:
        return "IH"
    if average >= 62:
        return "IM3"
    if average >= 50:
        return "IM2"
    return "IM1"


def _pick_focus_area(scores: dict[str, int]) -> str:
    if not scores:
        return "답변을 더 길고 구체적으로 구성하는 연습이 필요합니다."
    weakest = min(scores.items(), key=lambda item: item[1])[0]
    return f"다음에는 {CATEGORY_LABELS_KO.get(weakest, weakest)} 보완에 집중해보세요."


def _unique_items(items: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        normalized = item.strip()
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        result.append(normalized)
    return result


def _bounded_score(value: float) -> int:
    return int(max(0, min(100, round(value))))

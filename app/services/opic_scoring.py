from __future__ import annotations

import re
from typing import Any

OPIC_WEIGHTS = {
    "fluency": 0.20,
    "responseLength": 0.15,
    "contentRichness": 0.20,
    "coherence": 0.15,
    "vocabulary": 0.10,
    "grammar": 0.05,
    "pronunciation": 0.05,
    "taskCompletion": 0.10,
}

TOKEN_PATTERN = re.compile(r"[A-Za-z']+")
TIME_PATTERN = re.compile(
    r"\b("
    r"today|yesterday|tomorrow|last|next|week|month|year|morning|afternoon|evening|night|"
    r"weekend|usually|sometimes|always|never|recently|once|twice|first|second|"
    r"monday|tuesday|wednesday|thursday|friday|saturday|sunday|"
    r"january|february|march|april|may|june|july|august|september|october|november|december|"
    r"\d{1,2}(?:am|pm)"
    r")\b",
    re.IGNORECASE,
)
LOCATION_PATTERN = re.compile(
    r"\b("
    r"home|house|room|school|office|company|cafe|coffee shop|restaurant|park|beach|mountain|"
    r"library|gym|mall|store|supermarket|hospital|airport|station|subway|bus stop|city|"
    r"village|hotel|apartment|campus|classroom|my place|my hometown"
    r")\b",
    re.IGNORECASE,
)
REASON_PATTERN = re.compile(
    r"\b(because|so|since|therefore|that's why|the reason|in order to)\b",
    re.IGNORECASE,
)
FEELING_PATTERN = re.compile(
    r"\b("
    r"happy|sad|excited|nervous|relaxed|relaxing|stressful|stressed|fun|funny|boring|"
    r"interesting|comfortable|uncomfortable|great|good|bad|amazing|terrible|"
    r"love|like|enjoy|prefer|favorite|memorable|special"
    r")\b",
    re.IGNORECASE,
)
EXAMPLE_PATTERN = re.compile(
    r"\b("
    r"for example|for instance|one time|last time|when i|i remember|such as|especially"
    r")\b",
    re.IGNORECASE,
)

CONNECTOR_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in [
        r"\bbecause\b",
        r"\bso\b",
        r"\bthen\b",
        r"\bactually\b",
        r"\band\b",
        r"\bbut\b",
        r"\balso\b",
        r"\bafter that\b",
        r"\bfirst\b",
        r"\bnext\b",
        r"\bfinally\b",
        r"\bfor example\b",
        r"\bon the other hand\b",
    ]
]

DIMENSION_LABELS = {
    "fluency": "유창성",
    "responseLength": "답변 길이",
    "contentRichness": "내용 디테일",
    "coherence": "논리 흐름",
    "vocabulary": "어휘 다양성",
    "grammar": "문법 전달력",
    "pronunciation": "발음 명확도",
    "taskCompletion": "질문 대응력",
}

MAIN_FEEDBACK = {
    "fluency": "오픽에서는 완벽한 문장보다 멈추지 않고 이어 말하는 힘이 더 중요합니다. 짧게라도 계속 이어가세요.",
    "responseLength": "답변이 짧으면 상위 등급으로 올라가기 어렵습니다. 이유, 경험, 느낌을 붙여 최소 30초 이상 말해보세요.",
    "contentRichness": "오픽 답변은 디테일이 점수를 끌어올립니다. 언제, 어디서, 왜, 어땠는지를 꼭 넣어보세요.",
    "coherence": "문장 하나하나는 괜찮아도 흐름이 약하면 오픽 답변처럼 들리지 않습니다. because, so, then으로 연결해보세요.",
    "vocabulary": "같은 표현 반복이 많으면 준비된 짧은 답변처럼 보일 수 있습니다. 쉬운 단어라도 바꿔 말하는 폭을 늘려보세요.",
    "grammar": "오픽은 문법 시험보다 전달력 평가에 가깝습니다. 긴 문장보다 짧고 안정적인 문장으로 끝까지 가는 편이 좋습니다.",
    "pronunciation": "너무 빠르게 말하면 전달력이 떨어집니다. 속도를 조금 낮추고 문장 끝을 또렷하게 살려보세요.",
    "taskCompletion": "질문에서 묻는 포인트를 먼저 직접 답한 뒤 예시를 붙여야 오픽식 답변으로 평가받기 쉽습니다.",
}

TIP_MAP = {
    "fluency": "막히는 순간에는 침묵하지 말고 'well', 'let me think', 'actually' 같은 완충 표현으로 시간을 벌어보세요.",
    "responseLength": "답변을 의견 1개, 이유 1개, 경험 1개, 느낌 1개 순서로 확장해보세요.",
    "contentRichness": "when, where, why, how you felt 중 최소 3개를 넣으면 디테일 점수가 훨씬 안정됩니다.",
    "coherence": "'because', 'so', 'then', 'after that', 'for example'를 미리 입에 붙여두면 흐름 점수가 좋아집니다.",
    "vocabulary": "favorite, relaxing, convenient, memorable 같은 오픽 기본 표현 묶음을 통째로 익혀두세요.",
    "grammar": "문법을 고치려다 멈추기보다 쉬운 구조로 끝까지 말하는 쪽이 실제 오픽 채점에 더 유리합니다.",
    "pronunciation": "전달력을 높이려면 너무 빨리 밀어붙이지 말고 문장 끝을 또렷하게 정리하는 연습이 필요합니다.",
    "taskCompletion": "질문 키워드를 첫 두 문장 안에 다시 말해주면 질문 대응력 점수가 안정적으로 올라갑니다.",
}

SUMMARY_BY_GRADE = {
    "AL": "길이, 유창성, 디테일이 모두 살아 있어 실제 오픽 상위권 답변에 가까운 편입니다.",
    "IH": "길고 자연스럽게 이어 가면서도 디테일이 보여서 IH권 답변 흐름이 잘 만들어졌습니다.",
    "IM3": "기본 전달은 충분하지만 오픽 기준으로는 길이, 디테일, 연결감 중 한두 축을 더 밀어 올릴 필요가 있습니다.",
    "IM2": "질문에는 반응하고 있지만 답변이 아직 짧고 단순해서 IM3로 넘어가기엔 힘이 부족합니다.",
    "IM1": "짧더라도 최소한의 답변은 성립하지만 아직 등급형 답변으로 보기에는 확장과 흐름이 부족합니다.",
    "IL": "질문에 대한 반응은 있으나 문장 길이와 정보량이 매우 제한적이라 기초 단계 답변에 가깝습니다.",
    "NH": "아주 기본적인 반응은 보이지만 질문 대응과 발화 지속성이 약해 하위 구간으로 판단됩니다.",
    "NM": "단어 몇 개 또는 매우 짧은 구로만 반응하는 수준이라 의미 전달이 제한적입니다.",
    "NL": "발화량이 거의 없거나 채점 가능한 답변이 성립하지 않아 최하위 구간으로 판단됩니다.",
}

GRADE_REASON = {
    "AL": "점수와 상위 게이트 조건을 모두 충족했습니다.",
    "IH": "점수뿐 아니라 길이, 유창성, 디테일 조건을 함께 충족했습니다.",
    "IM3": "기본 점수는 확보했지만 IH 게이트까지는 아직 부족합니다.",
    "IM2": "짧더라도 질문 대응과 최소 확장 구조는 성립해 IM1보다 높은 단계로 평가했습니다.",
    "IM1": "최소한의 답변은 성립했지만 길이와 디테일이 부족해 IM2 게이트까지는 도달하지 못했습니다.",
    "IL": "질문과 관련된 반응은 있었지만 답변 분량과 정보량이 매우 제한적입니다.",
    "NH": "발화는 있었지만 응답 완성도가 낮아 IL 단계로 보기 어렵습니다.",
    "NM": "짧은 단어 수준의 반응만 있어 의미 전달이 매우 제한적입니다.",
    "NL": "채점 가능한 수준의 발화가 거의 없었습니다.",
}


def build_opic_assessment(
    *,
    question_text: str,
    transcript: str,
    metrics: dict[str, float | int | bool | None],
) -> dict[str, Any]:
    word_count = int(metrics.get("word_count") or 0)
    if not transcript.strip() or word_count == 0:
        breakdown = {key: 0 for key in OPIC_WEIGHTS}
        gate = {"im2Candidate": False, "ihCandidate": False, "alCandidate": False}
        grade = "NL"
        return {
            "score": 0.0,
            "score100": 0,
            "grade": grade,
            "summary": SUMMARY_BY_GRADE[grade],
            "mainFeedback": MAIN_FEEDBACK["fluency"],
            "gradeReason": GRADE_REASON[grade],
            "weights": OPIC_WEIGHTS,
            "breakdown": breakdown,
            "weakPoints": [DIMENSION_LABELS[key] for key in breakdown],
            "tips": [
                TIP_MAP["fluency"],
                TIP_MAP["responseLength"],
                TIP_MAP["contentRichness"],
            ],
            "tags": ["채점 가능한 답변 부족"],
            "gate": gate,
            "isGradable": False,
        }

    breakdown = {
        "fluency": _score_fluency(metrics),
        "responseLength": _score_response_length(metrics),
        "contentRichness": _score_content_richness(transcript),
        "coherence": _score_coherence(metrics),
        "vocabulary": _score_vocabulary(metrics),
        "grammar": _score_grammar(metrics),
        "pronunciation": _score_pronunciation(metrics),
        "taskCompletion": _score_task_completion(question_text, transcript, metrics),
    }

    weighted_score = round(
        sum(float(breakdown[key]) * float(weight) for key, weight in OPIC_WEIGHTS.items()),
        2,
    )
    gate = _build_gate_status(weighted_score, breakdown, metrics)
    grade = _resolve_grade(weighted_score, gate, breakdown, metrics)
    weakest_dimension = _pick_weakest_dimension(breakdown)

    weak_points = [DIMENSION_LABELS[key] for key, value in breakdown.items() if value <= 2]
    if not weak_points:
        weak_points = [DIMENSION_LABELS[weakest_dimension]]

    tips = [TIP_MAP[key] for key, value in breakdown.items() if value <= 3][:3]
    if not tips:
        tips = ["답변을 서론 1문장, 이유 2문장, 경험 2문장, 느낌 1문장 구조로 고정해두면 실전에서 훨씬 안정적입니다."]

    return {
        "score": weighted_score,
        "score100": round(weighted_score * 20),
        "grade": grade,
        "summary": _build_summary(grade, breakdown),
        "mainFeedback": _build_main_feedback(grade, weakest_dimension, breakdown),
        "gradeReason": GRADE_REASON[grade],
        "weights": OPIC_WEIGHTS,
        "breakdown": breakdown,
        "weakPoints": weak_points,
        "tips": tips,
        "tags": _build_tags(breakdown),
        "gate": gate,
        "isGradable": bool(metrics.get("is_gradable", False)),
    }


def build_opic_session_summary(answer_feedback: list[dict[str, Any]]) -> dict[str, Any] | None:
    opic_items = [
        item.get("opic")
        for item in answer_feedback
        if isinstance(item, dict) and isinstance(item.get("opic"), dict)
    ]
    if not opic_items:
        return None

    gradable_items = [item for item in opic_items if bool(item.get("isGradable"))]
    active_items = gradable_items or opic_items
    dimension_keys = list(OPIC_WEIGHTS.keys())

    averaged_breakdown = {
        key: round(sum(float(item["breakdown"].get(key, 0)) for item in active_items) / len(active_items), 2)
        for key in dimension_keys
    }
    averaged_score = round(sum(float(item.get("score", 0.0)) for item in active_items) / len(active_items), 2)
    averaged_metrics = {
        "word_count": sum(_estimate_word_count(item) for item in active_items) / len(active_items),
        "speech_duration_seconds": sum(_estimate_duration(item) for item in active_items) / len(active_items),
        "keyword_similarity": sum(_estimate_similarity(item) for item in active_items) / len(active_items),
        "is_gradable": bool(gradable_items),
    }
    gate = _build_gate_status(averaged_score, averaged_breakdown, averaged_metrics)
    grade = _resolve_grade(averaged_score, gate, averaged_breakdown, averaged_metrics)
    weakest_dimension = _pick_weakest_dimension(averaged_breakdown)

    weak_points = [DIMENSION_LABELS[key] for key, value in averaged_breakdown.items() if value < 3]
    if not weak_points:
        weak_points = [DIMENSION_LABELS[weakest_dimension]]

    tips = [TIP_MAP[key] for key, value in averaged_breakdown.items() if value < 3.5][:3]
    if not tips:
        tips = ["전체적으로 안정적이므로 디테일과 예시 밀도를 조금 더 높여 AL 방향으로 다듬어보세요."]

    return {
        "score": averaged_score,
        "score100": round(averaged_score * 20),
        "grade": grade,
        "summary": _build_summary(grade, averaged_breakdown),
        "mainFeedback": _build_main_feedback(grade, weakest_dimension, averaged_breakdown),
        "gradeReason": GRADE_REASON[grade],
        "weights": OPIC_WEIGHTS,
        "breakdown": averaged_breakdown,
        "weakPoints": weak_points,
        "tips": tips,
        "tags": _build_tags(averaged_breakdown),
        "gate": gate,
        "gradableAnswers": len(gradable_items),
        "totalAnswers": len(opic_items),
        "isGradable": bool(gradable_items),
    }


def _score_fluency(metrics: dict[str, float | int | bool | None]) -> int:
    silence_ratio = float(metrics.get("silence_ratio") or 0.0)
    filler_ratio = float(metrics.get("filler_ratio") or 0.0)
    avg_pause_seconds = float(metrics.get("avg_pause_seconds") or 0.0)

    if silence_ratio >= 0.45:
        score = 1
    elif silence_ratio >= 0.32:
        score = 2
    elif silence_ratio >= 0.22:
        score = 3
    elif silence_ratio >= 0.12:
        score = 4
    else:
        score = 5

    if filler_ratio >= 0.14:
        score -= 1
    if avg_pause_seconds >= 2.5:
        score -= 1
    return _clamp_score(score)


def _score_response_length(metrics: dict[str, float | int | bool | None]) -> int:
    speech_duration = float(metrics.get("speech_duration_seconds") or 0.0)
    sentence_count = int(metrics.get("sentence_count") or 0)
    word_count = int(metrics.get("word_count") or 0)

    time_score = _bucket_score(speech_duration, thresholds=[10.0, 20.0, 30.0, 45.0])
    sentence_score = _bucket_score(float(sentence_count), thresholds=[2.0, 4.0, 6.0, 7.0])
    word_score = _bucket_score(float(word_count), thresholds=[15.0, 30.0, 50.0, 75.0])

    blended = round((time_score * 0.5) + (sentence_score * 0.25) + (word_score * 0.25))
    return _clamp_score(blended)


def _score_content_richness(transcript: str) -> int:
    normalized = transcript.lower()
    signals = [
        bool(TIME_PATTERN.search(normalized)),
        bool(LOCATION_PATTERN.search(normalized)),
        bool(REASON_PATTERN.search(normalized)),
        bool(FEELING_PATTERN.search(normalized)),
        bool(EXAMPLE_PATTERN.search(normalized)),
    ]
    return sum(1 for signal in signals if signal)


def _score_coherence(metrics: dict[str, float | int | bool | None]) -> int:
    connector_count = int(metrics.get("connector_count") or 0)
    connector_ratio = float(metrics.get("connector_ratio") or 0.0)

    if connector_count == 0:
        score = 1
    elif connector_count <= 2:
        score = 3
    elif connector_count <= 4:
        score = 4
    else:
        score = 5

    if connector_ratio >= 1.0 and score < 5:
        score += 1
    return _clamp_score(score)


def _score_vocabulary(metrics: dict[str, float | int | bool | None]) -> int:
    lexical_diversity = float(metrics.get("lexical_diversity") or 0.0)
    repetition_rate = float(metrics.get("repetition_rate") or 0.0)

    if lexical_diversity < 0.30 or repetition_rate > 0.55:
        return 1
    if lexical_diversity < 0.38 or repetition_rate > 0.42:
        return 2
    if lexical_diversity < 0.48 or repetition_rate > 0.30:
        return 3
    if lexical_diversity < 0.58 or repetition_rate > 0.22:
        return 4
    return 5


def _score_grammar(metrics: dict[str, float | int | bool | None]) -> int:
    sentence_count = int(metrics.get("sentence_count") or 0)
    avg_sentence_length = float(metrics.get("avg_sentence_length") or 0.0)
    filler_ratio = float(metrics.get("filler_ratio") or 0.0)
    word_count = int(metrics.get("word_count") or 0)

    if word_count < 12 or sentence_count <= 1:
        score = 2
    elif avg_sentence_length < 3:
        score = 2
    else:
        score = 3
        if 4 <= avg_sentence_length <= 18 and filler_ratio < 0.12:
            score = 4
        if 6 <= avg_sentence_length <= 16 and sentence_count >= 3 and filler_ratio < 0.08:
            score = 5

    if filler_ratio > 0.18 and score > 1:
        score -= 1
    return _clamp_score(score)


def _score_pronunciation(metrics: dict[str, float | int | bool | None]) -> int:
    speech_rate_wpm = float(metrics.get("speech_rate_wpm") or 0.0)
    filler_ratio = float(metrics.get("filler_ratio") or 0.0)
    silence_ratio = float(metrics.get("silence_ratio") or 0.0)

    if silence_ratio >= 0.45 or speech_rate_wpm <= 60:
        return 1
    if silence_ratio >= 0.30 or filler_ratio >= 0.18 or speech_rate_wpm >= 190:
        return 2
    if silence_ratio >= 0.18 or filler_ratio >= 0.10 or speech_rate_wpm >= 165:
        return 3
    if silence_ratio < 0.10 and filler_ratio < 0.05 and 100 <= speech_rate_wpm <= 145:
        return 5
    if filler_ratio < 0.08 and 90 <= speech_rate_wpm <= 155:
        return 4
    return 3


def _score_task_completion(
    question_text: str,
    transcript: str,
    metrics: dict[str, float | int | bool | None],
) -> int:
    similarity = float(metrics.get("keyword_similarity") or 0.0)
    word_count = int(metrics.get("word_count") or 0)
    question_keywords = _extract_keywords(question_text)
    answer_keywords = _extract_keywords(transcript)
    matched_keywords = len(question_keywords & answer_keywords)

    if similarity < 0.12 or matched_keywords == 0:
        score = 1
    elif similarity < 0.28:
        score = 2
    elif similarity < 0.45:
        score = 3
    elif similarity < 0.65:
        score = 4
    else:
        score = 5

    if word_count >= 45 and score < 5:
        score += 1
    return _clamp_score(score)


def _build_gate_status(
    score: float,
    breakdown: dict[str, float | int],
    metrics: dict[str, float | int | bool | None],
) -> dict[str, bool]:
    word_count = float(metrics.get("word_count") or 0.0)
    speech_duration = float(metrics.get("speech_duration_seconds") or 0.0)

    im2_candidate = (
        score >= 1.45
        and float(breakdown.get("responseLength", 0)) >= 2
        and float(breakdown.get("taskCompletion", 0)) >= 2
        and (
            float(breakdown.get("fluency", 0)) >= 2
            or float(breakdown.get("contentRichness", 0)) >= 2
        )
        and word_count >= 12
        and speech_duration >= 8
    )
    ih_candidate = (
        float(breakdown.get("fluency", 0)) >= 4
        and float(breakdown.get("responseLength", 0)) >= 4
        and float(breakdown.get("contentRichness", 0)) >= 4
        and float(breakdown.get("coherence", 0)) >= 3
    )
    al_candidate = (
        score >= 4.2
        and float(breakdown.get("fluency", 0)) >= 5
        and float(breakdown.get("contentRichness", 0)) >= 5
        and float(breakdown.get("coherence", 0)) >= 4
        and float(breakdown.get("vocabulary", 0)) >= 4
    )
    return {
        "im2Candidate": im2_candidate,
        "ihCandidate": ih_candidate,
        "alCandidate": al_candidate,
    }


def _resolve_grade(
    score: float,
    gate: dict[str, bool],
    breakdown: dict[str, float | int],
    metrics: dict[str, float | int | bool | None],
) -> str:
    word_count = float(metrics.get("word_count") or 0.0)
    speech_duration = float(metrics.get("speech_duration_seconds") or 0.0)
    keyword_similarity = float(metrics.get("keyword_similarity") or 0.0)
    task_score = float(breakdown.get("taskCompletion", 0))
    length_score = float(breakdown.get("responseLength", 0))
    fluency_score = float(breakdown.get("fluency", 0))
    content_score = float(breakdown.get("contentRichness", 0))

    if gate["alCandidate"]:
        return "AL"
    if score >= 3.0 and gate["ihCandidate"]:
        return "IH"
    if score >= 2.0:
        return "IM3"
    if gate["im2Candidate"]:
        return "IM2"
    if (
        score >= 1.10
        and task_score >= 1
        and length_score >= 1
        and word_count >= 8
        and speech_duration >= 5
    ):
        return "IM1"
    if (
        score >= 0.85
        and keyword_similarity >= 0.08
        and word_count >= 6
        and speech_duration >= 4
        and (fluency_score >= 1 or content_score >= 1)
    ):
        return "IL"
    if score >= 0.55 and word_count >= 4 and speech_duration >= 2.5:
        return "NH"
    if score >= 0.25 and word_count >= 2 and speech_duration >= 1.0:
        return "NM"
    return "NL"


def _build_tags(breakdown: dict[str, float | int]) -> list[str]:
    tags: list[str] = []
    if float(breakdown.get("responseLength", 0)) >= 4 and float(breakdown.get("fluency", 0)) < 3:
        tags.append("말은 긴데 끊김 많음")
    if float(breakdown.get("fluency", 0)) >= 4 and float(breakdown.get("contentRichness", 0)) < 3:
        tags.append("말은 유창한데 내용 빈약")
    if float(breakdown.get("contentRichness", 0)) >= 4 and float(breakdown.get("coherence", 0)) < 3:
        tags.append("내용은 있는데 연결이 약함")
    if float(breakdown.get("taskCompletion", 0)) < 3:
        tags.append("질문 대응 부족")
    if float(breakdown.get("responseLength", 0)) <= 2 and float(breakdown.get("contentRichness", 0)) <= 2:
        tags.append("짧고 단순한 답변")
    if not tags:
        tags.append("균형형 답변")
    return tags


def _build_summary(grade: str, breakdown: dict[str, float | int]) -> str:
    base = SUMMARY_BY_GRADE[grade]
    if grade in {"IH", "AL"} and float(breakdown.get("contentRichness", 0)) < 5:
        return f"{base} 다만 예시와 감정 표현을 조금만 더 넣으면 한 단계 더 안정적입니다."
    if grade == "IM3" and float(breakdown.get("responseLength", 0)) < 4:
        return f"{base} 특히 답변 길이를 더 끌어올리는 것이 가장 빠른 개선 포인트입니다."
    if grade in {"IM1", "IL", "NH", "NM", "NL"} and float(breakdown.get("fluency", 0)) <= 2:
        return f"{base} 지금은 정확성보다 멈추지 않고 이어 말하는 습관이 우선입니다."
    return base


def _build_main_feedback(grade: str, weakest_dimension: str, breakdown: dict[str, float | int]) -> str:
    if grade == "NL":
        return "지금은 채점 가능한 발화량 자체가 부족합니다. 한두 단어만이라도 끊기지 않고 먼저 소리 내는 연습이 필요합니다."
    if grade == "NM":
        return "단어 수준 반응에서 짧은 문장 수준으로 올라가는 것이 우선입니다. 질문과 관련된 쉬운 문장을 두세 개 이어보세요."
    if grade == "NH":
        return "아주 기본적인 반응은 되고 있지만 문장 길이와 질문 대응을 더 분명히 보여줘야 합니다."
    if grade == "IL":
        return "질문에 반응은 하고 있으니, 이제 이유 한 가지와 예시 한 가지를 붙여 답변을 문장형으로 늘리는 연습이 필요합니다."
    if grade == "IM1":
        return "지금 단계에서는 어려운 문장을 만들기보다 질문과 관련된 쉬운 문장을 3~4개라도 끊기지 않고 이어 말하는 연습이 가장 중요합니다."
    if grade == "IM2" and float(breakdown.get("responseLength", 0)) <= 2:
        return "IM2에서 IM3로 올라가려면 한 줄 답변을 멈추고 이유와 경험을 붙여 답변 길이를 먼저 늘려야 합니다."
    if grade == "IM3" and float(breakdown.get("contentRichness", 0)) <= 3:
        return "IM3에서 IH로 가는 핵심은 디테일입니다. 시간, 장소, 이유, 느낌이 들어가야 답변이 확 살아납니다."
    if grade == "IH" and float(breakdown.get("vocabulary", 0)) <= 3:
        return "IH권에서는 기본 전달은 충분합니다. 이제는 같은 표현 반복을 줄여 답변을 더 자연스럽게 다듬어보세요."
    return MAIN_FEEDBACK[weakest_dimension]


def _pick_weakest_dimension(breakdown: dict[str, float | int]) -> str:
    return min(breakdown.items(), key=lambda item: (float(item[1]), item[0]))[0]


def _extract_keywords(text: str) -> set[str]:
    return {token.lower() for token in TOKEN_PATTERN.findall(text) if len(token) >= 3}


def _bucket_score(value: float, thresholds: list[float]) -> int:
    if value < thresholds[0]:
        return 1
    if value < thresholds[1]:
        return 2
    if value < thresholds[2]:
        return 3
    if value < thresholds[3]:
        return 4
    return 5


def _clamp_score(value: float) -> int:
    return max(1, min(5, int(round(value))))


def _estimate_word_count(item: dict[str, Any]) -> float:
    length_score = float(item.get("breakdown", {}).get("responseLength", 0))
    return max(0.0, length_score * 18)


def _estimate_duration(item: dict[str, Any]) -> float:
    length_score = float(item.get("breakdown", {}).get("responseLength", 0))
    return max(0.0, length_score * 8)


def _estimate_similarity(item: dict[str, Any]) -> float:
    task_score = float(item.get("breakdown", {}).get("taskCompletion", 0))
    return min(1.0, task_score / 5.0)

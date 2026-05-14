from __future__ import annotations

import re
from typing import Any

OPIC_WEIGHTS = {
    "taskCompletion": 0.14,
    "contentRichness": 0.14,
    "textType": 0.14,
    "coherence": 0.11,
    "fluency": 0.11,
    "timeFrameControl": 0.09,
    "functionHandling": 0.08,
    "lexicalSophistication": 0.07,
    "vocabulary": 0.04,
    "grammar": 0.04,
    "pronunciation": 0.04,
    "responseLength": 0.0,
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
    r"village|hotel|apartment|campus|classroom|my place|my hometown|work|workplace|"
    r"meeting|team|project"
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
    r"love|like|enjoy|prefer|favorite|memorable|special|calm|calmly|confused|"
    r"difficult|challenging|satisfied|proud|worried"
    r")\b",
    re.IGNORECASE,
)
EXAMPLE_PATTERN = re.compile(
    r"\b("
    r"for example|for instance|one time|last time|when i|i remember|such as|especially"
    r")\b",
    re.IGNORECASE,
)
PAST_PATTERN = re.compile(
    r"\b(went|did|was|were|watched|visited|had|made|took|bought|met|saw|"
    r"played|used|started|finished|decided|experienced|remembered|felt)\b",
    re.IGNORECASE,
)
FUTURE_PATTERN = re.compile(
    r"\b(will|going to|plan to|want to|would like to|hope to|next time|tomorrow|next week|next month)\b",
    re.IGNORECASE,
)
PRESENT_PATTERN = re.compile(
    r"\b(usually|often|every day|every week|sometimes|always|like|likes|go|goes|watch|watches|"
    r"play|plays|enjoy|enjoys|prefer|prefers|live|lives|work|works|study|studies)\b",
    re.IGNORECASE,
)
QUESTION_OPENING_PATTERN = re.compile(
    r"^(what|when|where|why|how|who|which|do|does|did|is|are|am|was|were|can|could|would|will|have|has)\b",
    re.IGNORECASE,
)
COMPARISON_PATTERN = re.compile(
    r"\b(than|different|difference|similar|compare|compared|compared to|while|whereas|both|instead of)\b",
    re.IGNORECASE,
)
PROBLEM_PATTERN = re.compile(
    r"\b(problem|issue|trouble|broken|delay|wrong|mistake|lost|change|cancel|repair|refund|complain)\b",
    re.IGNORECASE,
)
SOLUTION_PATTERN = re.compile(
    r"\b(so i|i decided|i asked|i called|i solved|i fixed|i changed|i canceled|i explained|i requested|i tried)\b",
    re.IGNORECASE,
)
FUNCTION_PATTERNS = {
    "reason": re.compile(r"\b(because|since|the reason|that's why|in order to|so)\b", re.IGNORECASE),
    "example": re.compile(r"\b(for example|for instance|such as|especially|one time)\b", re.IGNORECASE),
    "experience": re.compile(r"\b(when i|i remember|experience|experienced|last time|one time|recently|last week|last month|last year)\b", re.IGNORECASE),
    "result": re.compile(r"\b(after that|finally|as a result|so|therefore|then|because of that)\b", re.IGNORECASE),
    "problem_solving": re.compile(r"\b(problem|issue|trouble|solve|solved|fix|fixed|handle|handled|decided|solution)\b", re.IGNORECASE),
}
COMMON_WEAK_WORDS = {
    "good",
    "nice",
    "fun",
    "like",
    "thing",
    "things",
    "very",
    "really",
    "so",
    "bad",
    "big",
    "small",
    "many",
    "much",
    "get",
    "got",
}

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
    question_profile = _analyze_question_profile(question_text)
    if not transcript.strip() or word_count == 0:
        breakdown = {key: 0 for key in OPIC_WEIGHTS}
        breakdown["responseLength"] = 0
        breakdown["functionHandling"] = 0
        gate = {
            "im1Candidate": False,
            "im2Candidate": False,
            "im3Candidate": False,
            "ihCandidate": False,
            "alCandidate": False,
        }
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
            "weakPoints": [DIMENSION_LABELS.get(key, key) for key in breakdown],
            "tips": [
                TIP_MAP["fluency"],
                TIP_MAP["responseLength"],
                TIP_MAP["contentRichness"],
            ],
            "tags": ["채점 가능한 답변 부족"],
            "gate": gate,
            "metricSnapshot": _build_metric_snapshot(metrics),
            "analysis": {
                "questionProfile": question_profile,
                "responseProfile": {},
                "tenseFeedback": {"severity": "none", "message": "", "tip": "", "missing": []},
                "functionFeedback": {"message": "", "missing": []},
                "rubricScores": {
                    "function": 0.0,
                    "accuracy": 0.0,
                    "contentContext": 0.0,
                    "textType": 0.0,
                },
            },
            "isGradable": False,
        }

    transcript_profile = _analyze_transcript_profile(transcript)
    tense_feedback = _analyze_tense_feedback(question_profile, transcript_profile)
    function_feedback = _analyze_function_feedback(question_profile, transcript_profile)
    breakdown = {
        "fluency": _score_fluency(metrics),
        "responseLength": _score_response_length(metrics),
        "contentRichness": _score_content_richness(transcript),
        "textType": _score_text_type(metrics),
        "coherence": _score_coherence(metrics),
        "timeFrameControl": _score_time_frame_control(question_profile, transcript_profile),
        "functionHandling": _score_function_handling(question_profile, transcript_profile),
        "lexicalSophistication": _score_lexical_sophistication(transcript, metrics),
        "vocabulary": _score_vocabulary(metrics),
        "grammar": _score_grammar(metrics, tense_feedback),
        "pronunciation": _score_pronunciation(metrics),
        "taskCompletion": _score_task_completion(question_text, transcript, metrics, question_profile, transcript_profile),
    }

    weighted_score = round(
        sum(float(breakdown.get(key, 0)) * float(weight) for key, weight in OPIC_WEIGHTS.items()),
        2,
    )
    gate = _build_gate_status(weighted_score, breakdown, metrics)
    grade = _resolve_grade(weighted_score, gate, breakdown, metrics)
    weakest_dimension = _pick_weakest_dimension(breakdown)

    weak_points = [DIMENSION_LABELS.get(key, key) for key, value in breakdown.items() if value <= 2]
    if not weak_points:
        weak_points = [DIMENSION_LABELS.get(weakest_dimension, weakest_dimension)]

    tips = [TIP_MAP.get(key, MAIN_FEEDBACK.get(key, key)) for key, value in breakdown.items() if value <= 3][:3]
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
        "metricSnapshot": _build_metric_snapshot(metrics),
        "analysis": {
            "questionProfile": question_profile,
            "responseProfile": transcript_profile,
            "tenseFeedback": tense_feedback,
            "functionFeedback": function_feedback,
            "rubricScores": _build_rubric_scores(breakdown),
        },
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
    dimension_keys = list(dict.fromkeys([*OPIC_WEIGHTS.keys(), "responseLength", "functionHandling"]))

    averaged_breakdown = {
        key: round(sum(float(item["breakdown"].get(key, 0)) for item in active_items) / len(active_items), 2)
        for key in dimension_keys
    }
    averaged_score = round(sum(float(item.get("score", 0.0)) for item in active_items) / len(active_items), 2)
    averaged_metrics = _average_metric_snapshots(active_items)
    averaged_metrics["is_gradable"] = bool(gradable_items)
    gate = _build_gate_status(averaged_score, averaged_breakdown, averaged_metrics)
    grade = _resolve_grade(averaged_score, gate, averaged_breakdown, averaged_metrics)
    weakest_dimension = _pick_weakest_dimension(averaged_breakdown)

    weak_points = [DIMENSION_LABELS.get(key, key) for key, value in averaged_breakdown.items() if value < 3]
    if not weak_points:
        weak_points = [DIMENSION_LABELS.get(weakest_dimension, weakest_dimension)]

    tips = [TIP_MAP.get(key, MAIN_FEEDBACK.get(key, key)) for key, value in averaged_breakdown.items() if value < 3.5][:3]
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
        "metricSnapshot": averaged_metrics,
        "gradableAnswers": len(gradable_items),
        "totalAnswers": len(opic_items),
        "isGradable": bool(gradable_items),
    }


def _build_metric_snapshot(metrics: dict[str, float | int | bool | None]) -> dict[str, float | int]:
    return {
        "wordCount": int(metrics.get("word_count") or 0),
        "sentenceCount": int(metrics.get("sentence_count") or 0),
        "avgSentenceLength": round(float(metrics.get("avg_sentence_length") or 0.0), 2),
        "speechDurationSeconds": round(float(metrics.get("speech_duration_seconds") or 0.0), 2),
        "speechRateWpm": round(float(metrics.get("speech_rate_wpm") or 0.0), 2),
        "silenceRatio": round(float(metrics.get("silence_ratio") or 0.0), 4),
        "avgPauseSeconds": round(float(metrics.get("avg_pause_seconds") or 0.0), 2),
        "fillerRatio": round(float(metrics.get("filler_ratio") or 0.0), 4),
        "connectorCount": int(metrics.get("connector_count") or 0),
        "connectorRatio": round(float(metrics.get("connector_ratio") or 0.0), 4),
        "lexicalDiversity": round(float(metrics.get("lexical_diversity") or 0.0), 4),
        "repetitionRate": round(float(metrics.get("repetition_rate") or 0.0), 4),
        "keywordSimilarity": round(float(metrics.get("keyword_similarity") or 0.0), 4),
    }


def _average_metric_snapshots(items: list[dict[str, Any]]) -> dict[str, float | int]:
    snapshots = [
        item.get("metricSnapshot")
        for item in items
        if isinstance(item.get("metricSnapshot"), dict)
    ]
    if not snapshots:
        return {
            "word_count": sum(_estimate_word_count(item) for item in items) / len(items),
            "speech_duration_seconds": sum(_estimate_duration(item) for item in items) / len(items),
            "keyword_similarity": sum(_estimate_similarity(item) for item in items) / len(items),
        }

    def average(key: str) -> float:
        return round(sum(float(snapshot.get(key) or 0.0) for snapshot in snapshots) / len(snapshots), 4)

    return {
        "word_count": average("wordCount"),
        "sentence_count": average("sentenceCount"),
        "avg_sentence_length": average("avgSentenceLength"),
        "speech_duration_seconds": average("speechDurationSeconds"),
        "speech_rate_wpm": average("speechRateWpm"),
        "silence_ratio": average("silenceRatio"),
        "avg_pause_seconds": average("avgPauseSeconds"),
        "filler_ratio": average("fillerRatio"),
        "connector_count": average("connectorCount"),
        "connector_ratio": average("connectorRatio"),
        "lexical_diversity": average("lexicalDiversity"),
        "repetition_rate": average("repetitionRate"),
        "keyword_similarity": average("keywordSimilarity"),
        "wordCount": average("wordCount"),
        "sentenceCount": average("sentenceCount"),
        "avgSentenceLength": average("avgSentenceLength"),
        "speechDurationSeconds": average("speechDurationSeconds"),
        "speechRateWpm": average("speechRateWpm"),
        "silenceRatio": average("silenceRatio"),
        "avgPauseSeconds": average("avgPauseSeconds"),
        "fillerRatio": average("fillerRatio"),
        "connectorCount": average("connectorCount"),
        "connectorRatio": average("connectorRatio"),
        "lexicalDiversity": average("lexicalDiversity"),
        "repetitionRate": average("repetitionRate"),
        "keywordSimilarity": average("keywordSimilarity"),
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

    time_score = _bucket_score(speech_duration, thresholds=[15.0, 30.0, 45.0, 55.0])
    sentence_score = _bucket_score(float(sentence_count), thresholds=[3.0, 5.0, 7.0, 9.0])
    word_score = _bucket_score(float(word_count), thresholds=[25.0, 50.0, 75.0, 90.0])

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


def _score_text_type(metrics: dict[str, float | int | bool | None]) -> int:
    sentence_count = int(metrics.get("sentence_count") or 0)
    avg_sentence_length = float(metrics.get("avg_sentence_length") or 0.0)
    connector_count = int(metrics.get("connector_count") or 0)

    if sentence_count <= 2 and avg_sentence_length < 6:
        return 1
    if sentence_count >= 10 and connector_count >= 4:
        return 5
    if sentence_count >= 7 and connector_count >= 2:
        return 4
    if sentence_count >= 4:
        return 3
    if sentence_count >= 2 and avg_sentence_length >= 6:
        return 2
    return 1


def _score_time_frame_control(question_profile: dict[str, Any], transcript_profile: dict[str, Any]) -> int:
    expected = set(question_profile.get("expectedTimeframes", []))
    counts = transcript_profile.get("timeframeCounts", {})
    matched = sum(1 for frame in expected if int(counts.get(frame, 0)) > 0)
    total_markers = sum(int(value) for value in counts.values())

    if not expected:
        if total_markers >= 3:
            return 4
        if total_markers >= 1:
            return 3
        return 1

    if len(expected) == 1:
        frame = next(iter(expected))
        expected_count = int(counts.get(frame, 0))
        other_count = total_markers - expected_count
        if expected_count >= 3 and other_count <= expected_count:
            return 5
        if expected_count >= 1:
            return 4 if other_count <= expected_count + 1 else 3
        return 1 if total_markers == 0 else 2

    if matched == len(expected):
        return 5 if all(int(counts.get(frame, 0)) >= 1 for frame in expected) else 4
    if matched >= 1:
        return 3
    return 1 if total_markers == 0 else 2


def _score_function_handling(question_profile: dict[str, Any], transcript_profile: dict[str, Any]) -> int:
    function_type = str(question_profile.get("functionType") or "general")
    required_question_count = int(question_profile.get("requiredQuestionCount") or 0)
    question_sentence_count = int(transcript_profile.get("questionSentenceCount") or 0)
    matched_functions = int(transcript_profile.get("matchedFunctionCount") or 0)
    detail_signal_count = int(transcript_profile.get("detailSignalCount") or 0)
    comparison_signal_count = int(transcript_profile.get("comparisonSignalCount") or 0)
    past_count = int(transcript_profile.get("timeframeCounts", {}).get("past", 0))
    reason_signal = bool(transcript_profile.get("functionSignals", {}).get("reason"))
    example_signal = bool(transcript_profile.get("functionSignals", {}).get("example"))
    result_signal = bool(transcript_profile.get("functionSignals", {}).get("result"))
    problem_signal = bool(transcript_profile.get("problemSignal"))
    solution_signal = bool(transcript_profile.get("solutionSignal"))

    if bool(question_profile.get("requiresQuestionForm")):
        if question_sentence_count >= required_question_count:
            return 5
        if question_sentence_count >= max(2, required_question_count - 1):
            return 4
        if question_sentence_count >= 2:
            return 3
        if question_sentence_count >= 1:
            return 2
        return 1

    if function_type == "compare":
        if comparison_signal_count >= 2 and detail_signal_count >= 2:
            return 5
        if comparison_signal_count >= 1 and detail_signal_count >= 2:
            return 4
        if comparison_signal_count >= 1:
            return 3
        return 2 if detail_signal_count >= 2 else 1

    if function_type == "problem_solving":
        if problem_signal and solution_signal and result_signal:
            return 5
        if problem_signal and solution_signal:
            return 4
        if problem_signal or solution_signal:
            return 3
        return 1

    if function_type in {"past_experience", "narrate"}:
        if past_count >= 3 and example_signal and detail_signal_count >= 2:
            return 5
        if past_count >= 2 and detail_signal_count >= 2:
            return 4
        if past_count >= 1:
            return 3
        return 1

    if function_type in {"explain", "reason"}:
        if reason_signal and example_signal and detail_signal_count >= 2:
            return 5
        if reason_signal and detail_signal_count >= 2:
            return 4
        if reason_signal:
            return 3
        return 2 if detail_signal_count >= 2 else 1

    if function_type == "describe":
        if detail_signal_count >= 4:
            return 5
        if detail_signal_count >= 3:
            return 4
        if detail_signal_count >= 2:
            return 3
        return 2 if matched_functions >= 1 else 1

    if matched_functions >= 5:
        return 5
    if matched_functions >= 4:
        return 4
    if matched_functions >= 3:
        return 3
    if matched_functions >= 1:
        return 2
    return 1


def _score_lexical_sophistication(
    transcript: str,
    metrics: dict[str, float | int | bool | None],
) -> int:
    tokens = [token.lower() for token in TOKEN_PATTERN.findall(transcript)]
    if not tokens:
        return 1

    unique_ratio = len(set(tokens)) / max(len(tokens), 1)
    avg_word_length = sum(len(token) for token in tokens) / max(len(tokens), 1)
    lexical_diversity = float(metrics.get("lexical_diversity") or 0.0)
    repetition_rate = float(metrics.get("repetition_rate") or 0.0)
    weak_word_ratio = sum(1 for token in tokens if token in COMMON_WEAK_WORDS) / max(len(tokens), 1)
    long_word_ratio = sum(1 for token in tokens if len(token) >= 8) / max(len(tokens), 1)

    score = 1
    if unique_ratio >= 0.34 and avg_word_length >= 4.0:
        score = 2
    if unique_ratio >= 0.42 and avg_word_length >= 4.2:
        score = 3
    if unique_ratio >= 0.50 and avg_word_length >= 4.5 and long_word_ratio >= 0.05:
        score = 4
    if unique_ratio >= 0.58 and avg_word_length >= 4.8 and long_word_ratio >= 0.08:
        score = 5
    if lexical_diversity >= 0.50 and repetition_rate <= 0.35 and avg_word_length >= 4.1:
        score = max(score, 3)
    if lexical_diversity >= 0.58 and repetition_rate <= 0.35 and avg_word_length >= 4.4:
        score = max(score, 4)
    if lexical_diversity >= 0.62 and repetition_rate <= 0.30 and avg_word_length >= 4.6:
        score = max(score, 5)
    if lexical_diversity >= 0.60 and repetition_rate <= 0.30 and len(tokens) >= 90 and long_word_ratio >= 0.04:
        score = max(score, 4)

    if repetition_rate > 0.42:
        score -= 1
    if repetition_rate > 0.55:
        score -= 1
    if weak_word_ratio > 0.18:
        score -= 1
    return _clamp_score(score)


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


def _score_grammar(
    metrics: dict[str, float | int | bool | None],
    tense_feedback: dict[str, Any],
) -> int:
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

    tense_severity = str(tense_feedback.get("severity") or "")
    if tense_severity == "weak":
        score = min(score, 2)
    elif tense_severity == "mixed":
        score = min(score, 4)

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
    question_profile: dict[str, Any],
    transcript_profile: dict[str, Any],
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

    function_score = _score_function_handling(question_profile, transcript_profile)
    if bool(question_profile.get("requiresQuestionForm")):
        required_question_count = int(question_profile.get("requiredQuestionCount") or 0)
        question_sentence_count = int(transcript_profile.get("questionSentenceCount") or 0)
        if question_sentence_count == 0:
            return 1
        if question_sentence_count < max(2, required_question_count - 1):
            score = min(score, 2)
    elif str(question_profile.get("functionType") or "") == "compare" and int(transcript_profile.get("comparisonSignalCount") or 0) == 0:
        score = min(score, 2)
    elif function_score <= 2:
        score = min(score, function_score)

    return _clamp_score(score)


def _analyze_question_profile(question_text: str) -> dict[str, Any]:
    normalized = question_text.lower().strip()
    expected_timeframes: set[str] = set()

    if re.search(r"\b(last|yesterday|ago|used to|when you were|when i was|child|childhood|grew up)\b", normalized):
        expected_timeframes.add("past")
    if re.search(r"\b(now|these days|currently|usually|normally|do you|where do you|what do you)\b", normalized):
        expected_timeframes.add("present")
    if re.search(r"\b(will|going to|plan to|future|tomorrow|next)\b", normalized):
        expected_timeframes.add("future")
    if "different from" in normalized or "how is it different" in normalized:
        expected_timeframes.update({"past", "present"})
    if not expected_timeframes:
        expected_timeframes.add("present")

    requires_question_form = "ask me" in normalized and "question" in normalized
    required_question_count = 0
    if requires_question_form:
        if "four" in normalized or "3 or 4" in normalized or "three or four" in normalized:
            required_question_count = 4
        elif "three" in normalized:
            required_question_count = 3
        else:
            required_question_count = 2

    function_type = "general"
    if requires_question_form:
        function_type = "ask_questions"
    elif re.search(r"\b(different|difference|compare|similar)\b", normalized):
        function_type = "compare"
    elif re.search(r"\b(problem|issue|broken|change|cancel|repair|refund|complain)\b", normalized):
        function_type = "problem_solving"
    elif re.search(r"\b(last|ago|used to|when you were|child|childhood|experience|remember)\b", normalized):
        function_type = "past_experience"
    elif re.search(r"\b(why|how are|how do|how is)\b", normalized):
        function_type = "explain"
    elif re.search(r"\b(describe|tell me about|what does|what is|what kind of)\b", normalized):
        function_type = "describe"

    return {
        "functionType": function_type,
        "requiresQuestionForm": requires_question_form,
        "requiredQuestionCount": required_question_count,
        "expectedTimeframes": sorted(expected_timeframes),
        "requiresComparison": function_type == "compare",
    }


def _analyze_transcript_profile(transcript: str) -> dict[str, Any]:
    normalized = transcript.strip()
    sentence_candidates = [part.strip() for part in re.split(r"(?<=[.!?])\s+|\n+", normalized) if part.strip()]
    timeframe_counts = {
        "past": len(PAST_PATTERN.findall(normalized)),
        "present": len(PRESENT_PATTERN.findall(normalized)),
        "future": len(FUTURE_PATTERN.findall(normalized)),
    }
    function_signals = {
        key: bool(pattern.search(normalized))
        for key, pattern in FUNCTION_PATTERNS.items()
    }
    question_sentence_count = sum(1 for sentence in sentence_candidates if _looks_like_question(sentence))

    return {
        "sentenceCount": len(sentence_candidates),
        "questionSentenceCount": question_sentence_count,
        "timeframeCounts": timeframe_counts,
        "detailSignalCount": sum(
            1
            for pattern in [TIME_PATTERN, LOCATION_PATTERN, REASON_PATTERN, FEELING_PATTERN, EXAMPLE_PATTERN]
            if pattern.search(normalized)
        ),
        "comparisonSignalCount": len(COMPARISON_PATTERN.findall(normalized)),
        "matchedFunctionCount": sum(1 for matched in function_signals.values() if matched),
        "functionSignals": function_signals,
        "problemSignal": bool(PROBLEM_PATTERN.search(normalized)),
        "solutionSignal": bool(SOLUTION_PATTERN.search(normalized)),
    }


def _analyze_tense_feedback(question_profile: dict[str, Any], transcript_profile: dict[str, Any]) -> dict[str, Any]:
    expected = list(question_profile.get("expectedTimeframes", []))
    counts = transcript_profile.get("timeframeCounts", {})
    missing = [frame for frame in expected if int(counts.get(frame, 0)) == 0]

    if not expected:
        return {"severity": "none", "message": "", "tip": "", "missing": []}

    if len(expected) == 1:
        frame = expected[0]
        matched_count = int(counts.get(frame, 0))
        if matched_count >= 2:
            return {
                "severity": "good",
                "message": "질문이 요구한 시제를 대체로 안정적으로 유지했습니다.",
                "tip": "",
                "missing": [],
            }
        if matched_count == 1:
            return {
                "severity": "mixed",
                "message": "기대한 시제는 보이지만 문장 전체에서 일관되게 유지되지는 않았습니다.",
                "tip": f"질문이 { _timeframe_label(frame) }를 요구하면 핵심 동사 시제를 끝까지 같은 축으로 유지해 보세요.",
                "missing": [],
            }
        return {
            "severity": "weak",
            "message": f"질문은 { _timeframe_label(frame) }를 요구했지만 답변에서 그 시제 흔적이 거의 보이지 않습니다.",
            "tip": f"{ _timeframe_label(frame) }를 나타내는 시간 표현과 동사 형태를 첫 두 문장부터 분명하게 넣어보세요.",
            "missing": [frame],
        }

    if not missing:
        return {
            "severity": "good",
            "message": "과거/현재처럼 여러 시간 축을 요구한 질문에서 시제를 비교적 안정적으로 나눠 썼습니다.",
            "tip": "",
            "missing": [],
        }
    if len(missing) < len(expected):
        return {
            "severity": "mixed",
            "message": "여러 시제가 필요한 질문인데 일부 시간 축이 빠져 비교가 약해졌습니다.",
            "tip": "과거와 현재를 비교하는 질문이라면 각각 한두 문장씩 분리해서 답하면 시제 관리가 훨씬 또렷해집니다.",
            "missing": missing,
        }
    return {
        "severity": "weak",
        "message": "질문이 요구한 시간 축을 거의 반영하지 못해 시제와 내용의 방향이 어긋났습니다.",
        "tip": "질문의 시간 단서를 먼저 잡고, 과거면 과거 경험, 현재면 현재 습관, 미래면 계획을 바로 말해 보세요.",
        "missing": missing,
    }


def _analyze_function_feedback(question_profile: dict[str, Any], transcript_profile: dict[str, Any]) -> dict[str, Any]:
    function_type = str(question_profile.get("functionType") or "general")

    if bool(question_profile.get("requiresQuestionForm")):
        required_count = int(question_profile.get("requiredQuestionCount") or 0)
        actual_count = int(transcript_profile.get("questionSentenceCount") or 0)
        if actual_count >= required_count:
            return {"message": "질문하기 유형의 요구를 맞춰 여러 개의 질문을 만들었습니다.", "missing": []}
        return {
            "message": f"질문하기 유형인데 실제 질문 문장 수가 부족합니다. 최소 {required_count}개 정도는 질문 형태로 이어져야 합니다.",
            "missing": ["question_form"],
        }

    if function_type == "compare" and int(transcript_profile.get("comparisonSignalCount") or 0) == 0:
        return {
            "message": "비교형 질문인데 차이점이나 공통점을 드러내는 표현이 부족합니다.",
            "missing": ["comparison"],
        }

    if function_type == "problem_solving" and not bool(transcript_profile.get("solutionSignal")):
        return {
            "message": "문제 해결형 질문인데 문제 이후 어떻게 해결했는지 단계가 약합니다.",
            "missing": ["solution"],
        }

    if function_type in {"explain", "reason"} and not bool(transcript_profile.get("functionSignals", {}).get("reason")):
        return {
            "message": "설명형 질문인데 이유를 직접 연결해 주는 표현이 부족합니다.",
            "missing": ["reason"],
        }

    return {"message": "", "missing": []}


def _build_rubric_scores(breakdown: dict[str, float | int]) -> dict[str, float]:
    return {
        "function": round((float(breakdown.get("taskCompletion", 0)) * 0.6) + (float(breakdown.get("functionHandling", 0)) * 0.4), 2),
        "accuracy": round(
            (float(breakdown.get("grammar", 0)) * 0.35)
            + (float(breakdown.get("pronunciation", 0)) * 0.2)
            + (float(breakdown.get("fluency", 0)) * 0.2)
            + (float(breakdown.get("vocabulary", 0)) * 0.1)
            + (float(breakdown.get("timeFrameControl", 0)) * 0.15),
            2,
        ),
        "contentContext": round(
            (float(breakdown.get("taskCompletion", 0)) * 0.35)
            + (float(breakdown.get("contentRichness", 0)) * 0.4)
            + (float(breakdown.get("functionHandling", 0)) * 0.15)
            + (float(breakdown.get("timeFrameControl", 0)) * 0.1),
            2,
        ),
        "textType": round(
            (float(breakdown.get("responseLength", 0)) * 0.35)
            + (float(breakdown.get("textType", 0)) * 0.35)
            + (float(breakdown.get("coherence", 0)) * 0.3),
            2,
        ),
    }


def _looks_like_question(sentence: str) -> bool:
    normalized = sentence.strip()
    return normalized.endswith("?") or bool(QUESTION_OPENING_PATTERN.search(normalized))


def _timeframe_label(frame: str) -> str:
    return {
        "past": "과거 시제",
        "present": "현재 시제",
        "future": "미래 시제",
    }.get(frame, frame)


def _build_gate_status(
    score: float,
    breakdown: dict[str, float | int],
    metrics: dict[str, float | int | bool | None],
) -> dict[str, bool]:
    word_count = float(metrics.get("word_count") or 0.0)
    speech_duration = float(metrics.get("speech_duration_seconds") or 0.0)
    sentence_count = float(metrics.get("sentence_count") or 0.0)
    speech_rate_wpm = float(metrics.get("speech_rate_wpm") or 0.0)
    silence_ratio = float(metrics.get("silence_ratio") or 0.0)
    connector_count = float(metrics.get("connector_count") or 0.0)
    lexical_diversity = float(metrics.get("lexical_diversity") or 0.0)
    repetition_rate = float(metrics.get("repetition_rate") or 0.0)

    task_completion = float(breakdown.get("taskCompletion", 0))
    content_richness = float(breakdown.get("contentRichness", 0))
    coherence = float(breakdown.get("coherence", 0))
    fluency = float(breakdown.get("fluency", 0))
    grammar = float(breakdown.get("grammar", 0))
    pronunciation = float(breakdown.get("pronunciation", 0))
    text_type = float(breakdown.get("textType", 0))
    function_handling = float(breakdown.get("functionHandling", 0))
    time_frame_control = float(breakdown.get("timeFrameControl", 0))
    lexical_sophistication = float(breakdown.get("lexicalSophistication", 0))

    im1_candidate = (
        score >= 1.70
        and word_count >= 12
        and sentence_count >= 2
        and speech_duration >= 5
        and task_completion >= 2
    )
    im2_candidate = (
        score >= 2.30
        and word_count >= 30
        and sentence_count >= 4
        and speech_duration >= 18
        and task_completion >= 2.5
        and content_richness >= 2.3
        and coherence >= 2.3
        and text_type >= 2.3
    )
    im3_candidate = (
        score >= 3.00
        and word_count >= 50
        and sentence_count >= 6
        and speech_duration >= 28
        and task_completion >= 3
        and content_richness >= 3
        and coherence >= 3
        and text_type >= 3
        and function_handling >= 2.8
        and lexical_sophistication >= 2.5
    )
    ih_candidate = (
        score >= 3.50
        and word_count >= 70
        and sentence_count >= 8
        and speech_duration >= 38
        and fluency >= 3.5
        and task_completion >= 3.7
        and content_richness >= 3.5
        and coherence >= 3.5
        and text_type >= 3.5
        and function_handling >= 3.5
        and time_frame_control >= 3
        and lexical_sophistication >= 3
        and silence_ratio <= 0.30
        and repetition_rate <= 0.42
    )
    al_candidate = (
        score >= 4.10
        and word_count >= 90
        and sentence_count >= 10
        and speech_duration >= 52
        and fluency >= 4
        and task_completion >= 4
        and content_richness >= 4.2
        and coherence >= 4
        and text_type >= 4
        and function_handling >= 4
        and time_frame_control >= 4
        and lexical_sophistication >= 3.7
        and grammar >= 3.7
        and pronunciation >= 3.5
        and silence_ratio <= 0.24
        and repetition_rate <= 0.35
        and connector_count >= 4
    )
    return {
        "im1Candidate": im1_candidate,
        "im2Candidate": im2_candidate,
        "im3Candidate": im3_candidate,
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

    if gate.get("alCandidate"):
        return "AL"
    if gate.get("ihCandidate"):
        return "IH"
    if gate.get("im3Candidate"):
        return "IM3"
    if gate.get("im2Candidate"):
        return "IM2"
    if gate.get("im1Candidate"):
        return "IM1"
    if (
        score >= 1.10
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
    if float(breakdown.get("timeFrameControl", 0)) < 3:
        tags.append("시제 관리 약함")
    if float(breakdown.get("functionHandling", 0)) < 3:
        tags.append("질문 기능 수행 부족")
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
    return MAIN_FEEDBACK.get(weakest_dimension, MAIN_FEEDBACK["vocabulary"])


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

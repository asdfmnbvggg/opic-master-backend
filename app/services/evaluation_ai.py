from __future__ import annotations

from collections import Counter
from typing import Any

from app.services.opic_scoring import build_opic_assessment, build_opic_session_summary

CATEGORY_LABELS_KO = {
    "grammar": "문법",
    "fluency": "유창성",
    "vocabulary": "어휘",
    "completion": "답변 완성도",
    "relevance": "질문 적합도",
    "speed": "속도",
    "engagement": "전달력",
}


def build_answer_feedback(
    *,
    question_text: str,
    transcript: str,
    metrics: dict[str, float | int | bool | None],
) -> dict[str, Any]:
    normalized_transcript = transcript.strip()
    word_count = int(metrics.get("word_count") or 0)
    opic_assessment = build_opic_assessment(
        question_text=question_text,
        transcript=normalized_transcript,
        metrics=metrics,
    )

    if not normalized_transcript or word_count == 0:
        return _build_empty_answer_feedback(opic_assessment)

    speech_rate_wpm = float(metrics.get("speech_rate_wpm") or 0.0)
    keyword_similarity = float(metrics.get("keyword_similarity") or 0.0)
    repetition_rate = float(metrics.get("repetition_rate") or 0.0)
    lexical_diversity = float(metrics.get("lexical_diversity") or 0.0)
    avg_sentence_length = float(metrics.get("avg_sentence_length") or 0.0)
    connector_count = int(metrics.get("connector_count") or 0)
    connector_ratio = float(metrics.get("connector_ratio") or 0.0)
    too_short = bool(metrics.get("too_short", False))
    too_much_silence = bool(metrics.get("too_much_silence", False))
    is_gradable = bool(metrics.get("is_gradable", False))

    strengths = _collect_answer_strengths(metrics, opic_assessment)
    weaknesses = _collect_answer_weaknesses(metrics, opic_assessment)
    tips = _collect_answer_tips(metrics, opic_assessment)

    question_relevance_text = (
        "질문에서 물은 핵심을 비교적 잘 짚고 답하고 있습니다."
        if keyword_similarity >= 0.45
        else "질문 키워드가 답변에 충분히 반영되지 않았습니다."
    )
    sentence_length_text = (
        "문장 길이가 너무 짧지 않아 답변을 확장할 여지가 보입니다."
        if avg_sentence_length >= 7
        else "문장 길이가 짧아서 답변이 단답형으로 들릴 가능성이 큽니다."
    )
    answer_time_text = (
        "답변 길이는 채점 가능한 수준입니다."
        if not too_short
        else "답변 시간이 짧아 오픽형 답변으로 보기 어렵습니다."
    )
    repetition_text = (
        "반복 표현이 비교적 잘 통제되고 있습니다."
        if repetition_rate <= 0.18
        else "같은 단어와 표현 반복이 잦아 답변이 단조롭게 들립니다."
    )
    keyword_similarity_text = (
        "질문 키워드가 답변 안에 직접 반영되어 있습니다."
        if keyword_similarity >= 0.45
        else "질문에 나온 핵심 단어를 답변 첫 부분에서 더 직접적으로 받아주는 편이 좋습니다."
    )

    scores = _build_answer_scores(metrics, opic_assessment)
    feedback = {
        "grammar": _build_grammar_feedback(opic_assessment, metrics),
        "fluency": _build_fluency_feedback(opic_assessment, metrics),
        "vocabulary": _build_vocabulary_feedback(opic_assessment, metrics),
        "completion": _build_completion_feedback(opic_assessment, metrics),
        "relevance": question_relevance_text,
        "speed": _build_speed_feedback(speech_rate_wpm, opic_assessment, metrics),
        "sentenceLength": sentence_length_text,
        "repetition": repetition_text,
        "engagement": _build_engagement_feedback(opic_assessment, metrics),
        "answerTime": answer_time_text,
        "keywordSimilarity": keyword_similarity_text,
    }

    if not is_gradable:
        scores = {key: 0 for key in scores}

    return {
        "strengths": strengths[:4],
        "weaknesses": weaknesses[:4],
        "scores": scores,
        "feedback": feedback,
        "tips": tips[:4],
        "opic": opic_assessment,
        "connectorCount": connector_count,
        "connectorRatio": connector_ratio,
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
        return _build_empty_session_summary()

    score_buckets: dict[str, list[int]] = {
        "grammar": [],
        "fluency": [],
        "vocabulary": [],
        "completion": [],
        "relevance": [],
        "speed": [],
        "engagement": [],
    }
    gradable_answer_count = 0
    tag_counter: Counter[str] = Counter()

    for item in answer_feedback:
        answer_is_gradable = not item.get("tooShort", False) and not item.get("tooMuchSilence", False)
        if answer_is_gradable:
            gradable_answer_count += 1
        scores = item.get("scores", {})
        for key in score_buckets:
            value = scores.get(key)
            if isinstance(value, int):
                score_buckets[key].append(value)
        opic = item.get("opic")
        if isinstance(opic, dict):
            tag_counter.update(tag for tag in opic.get("tags", []) if isinstance(tag, str))

    if gradable_answer_count == 0:
        return {
            "strengths": [],
            "weaknesses": [
                "답변이 너무 짧거나 침묵 구간이 많아 전체 강점과 약점을 신뢰도 있게 판단하기 어렵습니다.",
            ],
            "feedback": {
                "summary": "채점 가능한 답변이 충분하지 않아 전체 평가는 제한적으로만 계산되었습니다.",
                "focus": "최소 2~3문장 이상, 20초 이상 답변해 보면서 다시 평가를 받아보세요.",
            },
            "tips": [
                "질문을 다시 말한 뒤 이유 한 가지를 붙이면 기본 길이를 빠르게 늘릴 수 있습니다.",
                "멈추는 구간이 길어지지 않도록 짧은 문장이라도 계속 이어 말해보세요.",
            ],
            "categoryScores": {key: 0 for key in score_buckets},
            "opic": build_opic_session_summary(answer_feedback),
            "estimatedGrade": "채점 제한",
            "isGradable": False,
        }

    averaged_scores = {
        key: round(sum(values) / len(values)) if values else 0
        for key, values in score_buckets.items()
    }
    opic_summary = build_opic_session_summary(answer_feedback)
    estimated_grade = (
        str(opic_summary.get("grade"))
        if isinstance(opic_summary, dict) and opic_summary.get("grade")
        else _estimate_grade_from_average(averaged_scores)
    )

    strengths = _build_session_strengths(averaged_scores, opic_summary)
    weaknesses = _build_session_weaknesses(averaged_scores, opic_summary, tag_counter)
    tips = _build_session_tips(opic_summary, weaknesses)
    feedback = {
        "summary": "전체적인 답변 흐름이 비교적 안정적입니다.",
        "focus": _pick_focus_area(averaged_scores),
    }
    if isinstance(opic_summary, dict):
        feedback["summary"] = str(opic_summary.get("summary") or feedback["summary"])
        feedback["focus"] = str(opic_summary.get("mainFeedback") or feedback["focus"])

    return {
        "strengths": strengths,
        "weaknesses": weaknesses,
        "feedback": feedback,
        "tips": tips,
        "categoryScores": averaged_scores,
        "opic": opic_summary,
        "estimatedGrade": estimated_grade,
        "isGradable": True,
    }


def _build_empty_answer_feedback(opic_assessment: dict[str, Any]) -> dict[str, Any]:
    message = "답변이 거의 없어 신뢰도 있는 평가를 만들기 어렵습니다."
    return {
        "strengths": [],
        "weaknesses": [
            "발화량이 거의 없어 강점과 약점을 안정적으로 판단할 수 없습니다.",
            "최소 두세 문장 이상 말해야 오픽형 피드백 정확도가 올라갑니다.",
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
            "completion": "질문에 대한 실제 답변이 거의 없어 완성도를 판단하기 어렵습니다.",
            "relevance": "질문 적합도를 보기에는 답변 내용이 부족합니다.",
            "speed": "발화량이 거의 없어 속도를 평가하기 어렵습니다.",
            "sentenceLength": "문장 길이를 평가하기에 충분한 답변이 없습니다.",
            "repetition": "반복 표현을 판단하기에 충분한 답변이 없습니다.",
            "engagement": "전달력을 판단하기에 충분한 답변이 없습니다.",
            "answerTime": "답변 시간이 너무 짧습니다.",
            "keywordSimilarity": "질문 키워드를 반영했는지 판단하기 어렵습니다.",
        },
        "tips": [
            "질문을 다시 말한 뒤 이유 한 가지를 붙여 최소 2~3문장으로 시작해보세요.",
            "정확한 문법보다 먼저 멈추지 않고 이어 말하는 연습을 해보세요.",
            "시간, 장소, 느낌 중 하나만 추가해도 답변 밀도가 훨씬 좋아집니다.",
        ],
        "opic": opic_assessment,
        "connectorCount": 0,
        "connectorRatio": 0.0,
        "tooShort": True,
        "tooMuchSilence": True,
        "questionRelevance": "답변이 부족해 질문 적합도를 판단하기 어렵습니다.",
        "sentenceLength": "답변이 부족해 문장 길이를 판단하기 어렵습니다.",
        "answerTime": "답변 시간이 너무 짧습니다.",
        "repetitionRate": "답변이 부족해 반복 표현을 판단하기 어렵습니다.",
        "keywordSimilarity": "답변이 부족해 질문 키워드 반영도를 판단하기 어렵습니다.",
    }


def _build_empty_session_summary() -> dict[str, Any]:
    return {
        "strengths": [],
        "weaknesses": ["전체 요약을 만들려면 최소 한 개 이상의 답변이 필요합니다."],
        "feedback": {"summary": "아직 전체 요약을 만들 수 없습니다.", "focus": "한 문제 이상 답변한 뒤 다시 확인해보세요."},
        "tips": ["한 문제 이상 답변해 보면서 다시 평가를 받아보세요."],
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
        "opic": None,
        "isGradable": False,
    }


def _build_answer_scores(
    metrics: dict[str, float | int | bool | None],
    opic_assessment: dict[str, Any],
) -> dict[str, int]:
    breakdown = opic_assessment.get("breakdown", {})
    word_count = int(metrics.get("word_count") or 0)
    speech_rate_wpm = float(metrics.get("speech_rate_wpm") or 0.0)
    lexical_diversity = float(metrics.get("lexical_diversity") or 0.0)
    repetition_rate = float(metrics.get("repetition_rate") or 0.0)
    keyword_similarity = float(metrics.get("keyword_similarity") or 0.0)
    silence_ratio = float(metrics.get("silence_ratio") or 0.0)

    return {
        "grammar": _bounded_score(35 + float(breakdown.get("grammar", 0)) * 12 + min(word_count, 50) * 0.25),
        "fluency": _bounded_score(
            28
            + float(breakdown.get("fluency", 0)) * 14
            + max(0.0, 18 - silence_ratio * 25)
            + max(0.0, 8 - abs(130 - speech_rate_wpm) * 0.08)
        ),
        "vocabulary": _bounded_score(
            28 + float(breakdown.get("vocabulary", 0)) * 14 + lexical_diversity * 24 - repetition_rate * 10
        ),
        "completion": _bounded_score(
            24
            + float(breakdown.get("taskCompletion", 0)) * 15
            + float(breakdown.get("responseLength", 0)) * 5
        ),
        "relevance": _bounded_score(30 + float(breakdown.get("taskCompletion", 0)) * 12 + keyword_similarity * 25),
        "speed": _bounded_score(52 + max(0.0, 20 - abs(130 - speech_rate_wpm) * 0.18) - silence_ratio * 12),
        "engagement": _bounded_score(
            20
            + float(breakdown.get("responseLength", 0)) * 9
            + float(breakdown.get("contentRichness", 0)) * 10
            + float(breakdown.get("coherence", 0)) * 6
        ),
    }


def _collect_answer_strengths(
    metrics: dict[str, float | int | bool | None],
    opic_assessment: dict[str, Any],
) -> list[str]:
    if not bool(metrics.get("is_gradable", False)):
        return []

    breakdown = opic_assessment.get("breakdown", {})
    strengths: list[str] = []

    if float(breakdown.get("taskCompletion", 0)) >= 4:
        strengths.append("질문에서 묻는 핵심을 벗어나지 않고 답변을 시작했습니다.")
    if float(breakdown.get("fluency", 0)) >= 4:
        strengths.append("중간 멈춤이 크지 않아 전체 말 흐름이 비교적 자연스럽습니다.")
    if float(breakdown.get("responseLength", 0)) >= 4:
        strengths.append("답변 길이가 충분해서 오픽형 서술 답변의 형태가 만들어졌습니다.")
    if float(breakdown.get("contentRichness", 0)) >= 4:
        strengths.append("시간, 장소, 이유, 느낌 같은 디테일이 들어 있어 답변이 구체적으로 들립니다.")
    if float(breakdown.get("coherence", 0)) >= 4:
        strengths.append("연결어를 활용해 문장들이 단순 나열이 아니라 흐름으로 이어집니다.")
    if float(breakdown.get("vocabulary", 0)) >= 4:
        strengths.append("같은 단어 반복이 심하지 않고 어휘 선택이 비교적 다양합니다.")

    if not strengths:
        strengths.append("기본적인 질문 대응은 되고 있어, 길이와 디테일을 더 보강하면 빠르게 좋아질 수 있습니다.")
    return _unique_items(strengths)


def _collect_answer_weaknesses(
    metrics: dict[str, float | int | bool | None],
    opic_assessment: dict[str, Any],
) -> list[str]:
    breakdown = opic_assessment.get("breakdown", {})
    weaknesses: list[str] = []

    if float(breakdown.get("taskCompletion", 0)) <= 2:
        weaknesses.append("질문에서 묻는 포인트를 바로 답하지 못해 응답 초점이 흐려졌습니다.")
    if float(breakdown.get("responseLength", 0)) <= 2:
        weaknesses.append("답변이 짧아서 등급형 답변으로 보기엔 확장성이 부족합니다.")
    if float(breakdown.get("fluency", 0)) <= 2 or bool(metrics.get("too_much_silence", False)):
        weaknesses.append("중간 멈춤이 잦아 답변 흐름이 자주 끊깁니다.")
    if float(breakdown.get("contentRichness", 0)) <= 2:
        weaknesses.append("이유, 경험, 느낌 같은 디테일이 부족해 내용이 평면적으로 들립니다.")
    if float(breakdown.get("coherence", 0)) <= 2:
        weaknesses.append("문장들이 연결되지 않아 나열형 답변처럼 들릴 수 있습니다.")
    if float(breakdown.get("vocabulary", 0)) <= 2:
        weaknesses.append("같은 단어 반복이 많아 표현 폭이 좁게 느껴집니다.")
    if float(breakdown.get("pronunciation", 0)) <= 2:
        weaknesses.append("발음 또는 인식 정확도가 낮아 전달력이 일부 떨어졌습니다.")

    if not weaknesses and not bool(metrics.get("is_gradable", False)):
        weaknesses.append("발화량이 부족해 정확한 약점 판정이 어렵습니다.")
    if not weaknesses:
        weaknesses.append("상대적으로 약한 축은 디테일 밀도입니다. 예시를 조금만 더 붙이면 답변 완성도가 올라갑니다.")
    return _unique_items(weaknesses)


def _collect_answer_tips(
    metrics: dict[str, float | int | bool | None],
    opic_assessment: dict[str, Any],
) -> list[str]:
    tips = [tip for tip in opic_assessment.get("tips", []) if isinstance(tip, str)]

    if bool(metrics.get("too_short", False)):
        tips.insert(0, "첫 문장에 결론을 말하고, 두 번째 문장부터 이유와 예시를 붙여 길이를 늘려보세요.")
    if bool(metrics.get("too_much_silence", False)):
        tips.insert(0, "멈출 것 같으면 짧은 filler로 버티면서 다음 문장을 바로 이어가세요.")

    return _unique_items(tips)[:4] or [
        "질문 키워드를 첫 문장에 다시 말한 뒤 이유와 경험을 차례대로 붙여보세요.",
        "완벽한 문장보다 끊기지 않는 짧은 문장 여러 개가 오픽에서 더 유리합니다.",
        "when, where, why, how you felt 중 세 가지 이상을 넣는 연습을 해보세요.",
    ]


def _build_grammar_feedback(opic_assessment: dict[str, Any], metrics: dict[str, float | int | bool | None]) -> str:
    grammar_score = float(opic_assessment.get("breakdown", {}).get("grammar", 0))
    if grammar_score >= 4:
        return "문장이 대체로 안정적으로 이어져 의미 전달에 큰 무리가 없습니다."
    if grammar_score >= 3:
        return "문법이 완벽하지는 않아도 전달에는 큰 문제가 없습니다."
    if bool(metrics.get("too_short", False)):
        return "답변이 짧아 문법 전달력을 안정적으로 판단하기 어렵습니다."
    return "문장을 길게 만들기보다 쉬운 구조로 끝까지 말하는 쪽이 더 유리합니다."


def _build_fluency_feedback(opic_assessment: dict[str, Any], metrics: dict[str, float | int | bool | None]) -> str:
    fluency_score = float(opic_assessment.get("breakdown", {}).get("fluency", 0))
    if fluency_score >= 4:
        return "큰 멈춤 없이 비교적 자연스럽게 이어 말하고 있습니다."
    if fluency_score >= 3:
        return "중간중간 멈춤은 있지만 전체 흐름은 유지하고 있습니다."
    if bool(metrics.get("too_much_silence", False)):
        return "침묵 구간이 길어 유창성이 실제보다 낮게 보일 수 있습니다."
    return "말이 자주 끊겨 유창성이 낮게 평가될 가능성이 큽니다."


def _build_vocabulary_feedback(opic_assessment: dict[str, Any], metrics: dict[str, float | int | bool | None]) -> str:
    vocabulary_score = float(opic_assessment.get("breakdown", {}).get("vocabulary", 0))
    if vocabulary_score >= 4:
        return "같은 단어 반복이 심하지 않아 어휘 선택이 비교적 안정적입니다."
    if vocabulary_score >= 3:
        return "기본 어휘 전달은 가능하지만 표현 폭은 더 넓어질 수 있습니다."
    if float(metrics.get("repetition_rate") or 0.0) > 0.35:
        return "반복 표현 비율이 높아 어휘 다양성이 낮게 보입니다."
    return "주제 관련 표현을 몇 개만 더 익혀도 어휘 점수가 빠르게 좋아질 수 있습니다."


def _build_completion_feedback(opic_assessment: dict[str, Any], metrics: dict[str, float | int | bool | None]) -> str:
    task_score = float(opic_assessment.get("breakdown", {}).get("taskCompletion", 0))
    length_score = float(opic_assessment.get("breakdown", {}).get("responseLength", 0))
    if task_score >= 4 and length_score >= 4:
        return "질문에 맞는 내용을 충분한 길이로 답해 답변 완성도가 좋습니다."
    if task_score >= 3:
        return "기본 질문 대응은 되었지만 예시와 확장이 더 붙으면 훨씬 좋아집니다."
    if bool(metrics.get("too_short", False)):
        return "답변이 짧아 질문 대응이 충분히 드러나지 않았습니다."
    return "질문에 직접 답한 뒤 이유와 경험을 붙이는 구조가 필요합니다."


def _build_speed_feedback(
    speech_rate_wpm: float,
    opic_assessment: dict[str, Any],
    metrics: dict[str, float | int | bool | None],
) -> str:
    if bool(metrics.get("too_much_silence", False)):
        return "침묵 구간이 길어 실제 말 속도보다 더 느리게 평가될 수 있습니다."
    if 95 <= speech_rate_wpm <= 165:
        return "말하기 속도가 비교적 안정적입니다."
    if speech_rate_wpm > 165:
        return "조금 빠르게 말하는 편이라 문장 끝 전달력이 약해질 수 있습니다."
    return "속도가 느린 편이어서 답변 흐름이 끊겨 보일 수 있습니다."


def _build_engagement_feedback(opic_assessment: dict[str, Any], metrics: dict[str, float | int | bool | None]) -> str:
    content_score = float(opic_assessment.get("breakdown", {}).get("contentRichness", 0))
    coherence_score = float(opic_assessment.get("breakdown", {}).get("coherence", 0))
    length_score = float(opic_assessment.get("breakdown", {}).get("responseLength", 0))
    if content_score >= 4 and coherence_score >= 4:
        return "답변이 구체적이고 흐름도 있어 전달력이 좋습니다."
    if length_score <= 2:
        return "답변이 짧아 전달력이 충분히 살아나지 않았습니다."
    if content_score <= 2:
        return "정보량이 적어 답변이 기억에 남는 수준까지는 올라오지 못했습니다."
    return "기본 전달은 되지만 예시와 감정 표현을 더 넣으면 훨씬 생동감 있어집니다."


def _build_session_strengths(
    averaged_scores: dict[str, int],
    opic_summary: dict[str, Any] | None,
) -> list[str]:
    strengths: list[str] = []
    breakdown = opic_summary.get("breakdown", {}) if isinstance(opic_summary, dict) else {}

    if float(breakdown.get("fluency", 0)) >= 4:
        strengths.append("전체적으로 답변을 끊기지 않게 이어 가는 힘이 좋습니다.")
    if float(breakdown.get("responseLength", 0)) >= 4:
        strengths.append("답변 길이가 비교적 충분해 오픽형 답변 구조를 만들고 있습니다.")
    if float(breakdown.get("taskCompletion", 0)) >= 4:
        strengths.append("질문 의도를 크게 벗어나지 않고 핵심을 짚는 편입니다.")
    if float(breakdown.get("contentRichness", 0)) >= 4:
        strengths.append("답변에 경험과 디테일이 살아 있어 내용 밀도가 좋습니다.")
    if averaged_scores.get("vocabulary", 0) >= 75:
        strengths.append("어휘 반복이 과하지 않아 전체 답변이 비교적 자연스럽게 들립니다.")

    return _unique_items(strengths)[:4] or ["전반적으로 기본 전달은 안정적으로 이루어지고 있습니다."]


def _build_session_weaknesses(
    averaged_scores: dict[str, int],
    opic_summary: dict[str, Any] | None,
    tag_counter: Counter[str],
) -> list[str]:
    weaknesses: list[str] = []
    breakdown = opic_summary.get("breakdown", {}) if isinstance(opic_summary, dict) else {}

    if float(breakdown.get("responseLength", 0)) < 3:
        weaknesses.append("전체적으로 답변 길이가 짧아 상위 등급으로 이어지기 어렵습니다.")
    if float(breakdown.get("contentRichness", 0)) < 3:
        weaknesses.append("시간, 장소, 이유, 느낌 같은 디테일이 전반적으로 부족합니다.")
    if float(breakdown.get("fluency", 0)) < 3:
        weaknesses.append("대답은 하고 있지만 중간 멈춤이 많아 유창성이 약하게 잡힙니다.")
    if float(breakdown.get("coherence", 0)) < 3:
        weaknesses.append("문장 간 연결이 약해 답변이 나열형으로 들릴 수 있습니다.")
    if averaged_scores.get("vocabulary", 100) < 65:
        weaknesses.append("자주 쓰는 단어 반복이 많아 어휘 폭이 좁게 느껴집니다.")

    for tag, count in tag_counter.most_common(2):
        if count >= 2:
            weaknesses.append(f"반복적으로 보인 패턴: {tag}")

    return _unique_items(weaknesses)[:4] or ["디테일과 표현 다양성을 조금 더 보강하면 전체 완성도가 올라갈 수 있습니다."]


def _build_session_tips(opic_summary: dict[str, Any] | None, weaknesses: list[str]) -> list[str]:
    if isinstance(opic_summary, dict):
        tips = [tip for tip in opic_summary.get("tips", []) if isinstance(tip, str)]
        if tips:
            return _unique_items(tips)[:4]

    fallback: list[str] = []
    joined = " ".join(weaknesses)
    if "길이" in joined:
        fallback.append("모든 답변을 결론 1문장, 이유 2문장, 경험 2문장 구조로 연습해보세요.")
    if "디테일" in joined:
        fallback.append("시간, 장소, 이유, 느낌 중 최소 세 가지를 의식적으로 넣어보세요.")
    if "유창성" in joined or "멈춤" in joined:
        fallback.append("막히는 순간 filler를 써서 침묵 시간을 줄이는 연습이 필요합니다.")

    return _unique_items(fallback)[:4] or ["질문 키워드를 먼저 받아주고 이유와 경험을 붙이는 기본 틀을 반복 연습해보세요."]


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
    if average >= 40:
        return "IM1"
    if average >= 30:
        return "IL"
    if average >= 20:
        return "NH"
    if average >= 10:
        return "NM"
    return "NL"


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

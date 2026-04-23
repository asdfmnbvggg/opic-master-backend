from __future__ import annotations

from typing import Any


def build_answer_feedback(
    *,
    question_text: str,
    transcript: str,
    metrics: dict[str, float | int | bool],
) -> dict[str, Any]:
    word_count = int(metrics["word_count"])
    speech_rate_wpm = float(metrics["speech_rate_wpm"])
    keyword_similarity = float(metrics["keyword_similarity"])
    repetition_rate = float(metrics["repetition_rate"])
    lexical_diversity = float(metrics["lexical_diversity"])
    too_short = bool(metrics["too_short"])
    too_much_silence = bool(metrics["too_much_silence"])
    is_gradable = bool(metrics["is_gradable"])

    strengths: list[str] = []
    weaknesses: list[str] = []
    tips: list[str] = []

    if keyword_similarity >= 0.45:
        strengths.append("The answer stays on topic and addresses key parts of the question.")
    else:
        weaknesses.append("The response needs to connect more directly to the question prompt.")
        tips.append("Use one or two keywords from the question in your first sentence.")

    if lexical_diversity >= 0.65:
        strengths.append("Vocabulary variety is good for this response length.")
    else:
        weaknesses.append("Word choice becomes repetitive in several parts.")
        tips.append("Replace repeated basic words with one or two clearer alternatives.")

    if 90 <= speech_rate_wpm <= 170:
        strengths.append("Speaking speed is within a natural OPIC-friendly range.")
    elif speech_rate_wpm > 170:
        weaknesses.append("The response appears rushed, which can reduce clarity.")
        tips.append("Slow down slightly and add short pauses between ideas.")
    else:
        weaknesses.append("The response is slower than ideal and may sound hesitant.")
        tips.append("Try grouping ideas into shorter chunks and keep speaking through pauses.")

    if repetition_rate <= 0.16:
        strengths.append("Repeated expressions are reasonably controlled.")
    else:
        weaknesses.append("Several phrases or filler patterns are repeated too often.")
        tips.append("Prepare two transition phrases you can rotate instead of repeating the same opener.")

    if too_short:
        weaknesses.append("The answer is too short for a stable score.")
        tips.append("Aim for at least three clear idea blocks: answer, reason, example.")

    if too_much_silence:
        weaknesses.append("There is too much silence or too little spoken content in the clip.")
        tips.append("Keep talking through simple details instead of stopping after one sentence.")

    if not strengths:
        strengths.append("The response provides a usable base that can be improved with clearer detail.")

    if not weaknesses and is_gradable:
        weaknesses.append("Adding one more concrete example would make the response stronger.")

    estimated_sub_grade = _estimate_sub_grade(metrics)

    question_relevance_text = (
        "The response matches the question closely."
        if keyword_similarity >= 0.45
        else "The response only partially addresses the question."
    )
    sentence_length_text = (
        "Sentence length is balanced enough for clear delivery."
        if float(metrics["avg_sentence_length"]) >= 7
        else "Sentences are very short, so the answer feels underdeveloped."
    )
    answer_time_text = (
        "Answer length is enough for scoring."
        if not too_short
        else "Answer length is too short for reliable grading."
    )
    repetition_text = (
        "Repetition is under control."
        if repetition_rate <= 0.16
        else "Repeated words and patterns are noticeable."
    )
    keyword_similarity_text = (
        "Question keywords are reflected in the answer."
        if keyword_similarity >= 0.45
        else "Important question keywords are missing from the answer."
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
            "Grammar is generally understandable, but longer sentence control should improve."
            if word_count >= 20
            else "There is not enough language sample to judge grammar reliably."
        ),
        "fluency": (
            "Delivery is fairly smooth overall."
            if not too_much_silence and 90 <= speech_rate_wpm <= 170
            else "Pauses or pacing reduce overall fluency."
        ),
        "vocabulary": (
            "Vocabulary range supports the topic well."
            if lexical_diversity >= 0.65
            else "Use a wider range of words instead of repeating the same terms."
        ),
        "completion": (
            "The answer covers the prompt with enough detail."
            if not too_short and keyword_similarity >= 0.45
            else "The answer needs more development or closer alignment with the prompt."
        ),
        "relevance": question_relevance_text,
        "speed": (
            "Speaking speed feels natural."
            if 90 <= speech_rate_wpm <= 170
            else "Pacing should be adjusted to sound more natural."
        ),
        "sentenceLength": sentence_length_text,
        "repetition": repetition_text,
        "engagement": (
            "The response has enough movement and detail to hold attention."
            if word_count >= 35
            else "Add examples, reactions, or contrast to make the answer more engaging."
        ),
        "answerTime": answer_time_text,
        "keywordSimilarity": keyword_similarity_text,
    }

    if not is_gradable:
        if too_short:
            tips.insert(0, "The answer is too short for accurate scoring.")
        if too_much_silence:
            tips.insert(0, "Large silent sections limit how much feedback can be trusted.")

    while len(tips) < 3:
        tips.append("Add one concrete example to make the answer easier to score.")

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
            "strengths": ["No answers were submitted for this session yet."],
            "weaknesses": ["Submit at least one answer to generate a summary."],
            "feedback": {"summary": "No overall summary is available."},
            "tips": ["Complete at least one question and try again."],
            "categoryScores": {
                "grammar": 0,
                "fluency": 0,
                "vocabulary": 0,
                "completion": 0,
                "relevance": 0,
                "speed": 0,
                "engagement": 0,
            },
            "estimatedGrade": "Not enough data",
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

    for item in answer_feedback:
        strengths.extend(item.get("strengths", []))
        weaknesses.extend(item.get("weaknesses", []))
        tips.extend(item.get("tips", []))
        is_gradable = is_gradable and not item.get("tooShort", False) and not item.get("tooMuchSilence", False)
        scores = item.get("scores", {})
        for key in score_buckets:
            value = scores.get(key)
            if isinstance(value, int):
                score_buckets[key].append(value)

    averaged_scores = {
        key: round(sum(values) / len(values)) if values else 0
        for key, values in score_buckets.items()
    }
    estimated_grade = _estimate_grade_from_average(averaged_scores)
    feedback = {
        "summary": (
            "Overall performance is consistent and mostly gradable."
            if is_gradable
            else "Some answers were too short or too incomplete, so the overall estimate is conservative."
        ),
        "focus": _pick_focus_area(averaged_scores),
    }

    return {
        "strengths": _unique_items(strengths)[:4] or ["Responses generally stay understandable and organized."],
        "weaknesses": _unique_items(weaknesses)[:4] or ["More detail and variety would improve the overall score."],
        "feedback": feedback,
        "tips": _unique_items(tips)[:4] or ["Add one example and one reason in every answer."],
        "categoryScores": averaged_scores,
        "estimatedGrade": estimated_grade,
        "isGradable": is_gradable,
    }


def _estimate_sub_grade(metrics: dict[str, float | int | bool]) -> str:
    if not bool(metrics["is_gradable"]):
        return "Not gradable"

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
        return "Not enough data"

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
        return "Build complete answers with more detail."
    weakest = min(scores.items(), key=lambda item: item[1])[0]
    return f"Focus next on improving {weakest}."


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

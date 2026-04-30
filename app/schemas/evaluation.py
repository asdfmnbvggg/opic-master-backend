from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class EvaluationQuestionPayload(BaseModel):
    questionId: str
    questionOrder: int
    questionText: str
    questionType: str | None = None
    translation: str | None = None
    hint: str | None = None
    category: str | None = None


class EvaluationSessionCreateRequest(BaseModel):
    mode: str
    title: str | None = None
    difficulty: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    questions: list[EvaluationQuestionPayload] = Field(default_factory=list)


class TranscriptUpdateRequest(BaseModel):
    transcript: str = ""


class SavedAnswerResponse(BaseModel):
    savedId: int
    message: str


class EvaluationScoresResponse(BaseModel):
    grammar: int
    fluency: int
    vocabulary: int
    completion: int
    relevance: int
    speed: int
    engagement: int


class EvaluationFeedbackTextResponse(BaseModel):
    grammar: str
    fluency: str
    vocabulary: str
    completion: str
    relevance: str
    speed: str
    sentenceLength: str
    repetition: str
    engagement: str
    answerTime: str
    keywordSimilarity: str


class OpicGateResponse(BaseModel):
    im2Candidate: bool
    ihCandidate: bool
    alCandidate: bool


class OpicAnswerEvaluationResponse(BaseModel):
    score: float
    score100: int
    summary: str
    mainFeedback: str
    weights: dict[str, float]
    breakdown: dict[str, float | int]
    weakPoints: list[str]
    tips: list[str]
    tags: list[str]
    isGradable: bool


class OpicOverallEvaluationResponse(OpicAnswerEvaluationResponse):
    grade: str
    gradeReason: str
    gate: OpicGateResponse
    gradableAnswers: int | None = None
    totalAnswers: int | None = None


class EvaluationMetricsResponse(BaseModel):
    wordCount: int
    sentenceCount: int
    avgSentenceLength: float
    repetitionRate: float
    lexicalDiversity: float
    keywordSimilarity: float
    connectorCount: int
    connectorRatio: float
    speechDurationSeconds: float
    silenceDurationSeconds: float
    silenceRatio: float
    pauseCount: int
    avgPauseSeconds: float
    speechRateWpm: float
    fillerCount: int
    fillerRatio: float
    tooShort: bool
    tooMuchSilence: bool
    isGradable: bool


class EvaluationAnswerFeedbackResponse(BaseModel):
    strengths: list[str]
    weaknesses: list[str]
    scores: EvaluationScoresResponse
    feedback: EvaluationFeedbackTextResponse
    tips: list[str]
    opic: OpicAnswerEvaluationResponse | None = None
    tooShort: bool
    tooMuchSilence: bool
    questionRelevance: str
    sentenceLength: str
    answerTime: str
    repetitionRate: str
    keywordSimilarity: str


class EvaluationAnswerResponse(BaseModel):
    id: int
    sessionId: int
    mode: str
    questionId: str
    questionOrder: int
    questionType: str | None = None
    questionText: str
    audioUrl: str | None = None
    audioDurationSeconds: float
    originalTranscript: str
    editedTranscript: str | None = None
    usedTranscript: str
    metrics: EvaluationMetricsResponse
    feedback: EvaluationAnswerFeedbackResponse
    createdAt: str
    updatedAt: str


class EvaluationSessionOverallResponse(BaseModel):
    strengths: list[str]
    weaknesses: list[str]
    feedback: dict[str, str]
    tips: list[str]
    categoryScores: dict[str, int]
    opic: OpicOverallEvaluationResponse | None = None
    estimatedGrade: str | None = None
    isGradable: bool


class EvaluationSessionResponse(BaseModel):
    id: int
    mode: str
    status: str
    title: str | None = None
    difficulty: str | None = None
    totalQuestions: int
    completedQuestions: int
    metadata: dict[str, Any]
    questions: list[EvaluationQuestionPayload]
    answers: list[EvaluationAnswerResponse]
    overall: EvaluationSessionOverallResponse
    createdAt: str
    updatedAt: str

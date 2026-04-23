-- Common evaluation storage for question-by-question answer analysis.
-- Local development still uses SQLAlchemy create_all, but this draft is useful
-- for promoting the schema into a real migration later.

CREATE TABLE IF NOT EXISTS evaluation_sessions (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    mode VARCHAR(20) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'in_progress',
    title VARCHAR(100),
    difficulty VARCHAR(20),
    total_questions INTEGER NOT NULL DEFAULT 0,
    completed_questions INTEGER NOT NULL DEFAULT 0,
    metadata_json TEXT NOT NULL DEFAULT '{}',
    overall_strengths_json TEXT NOT NULL DEFAULT '[]',
    overall_weaknesses_json TEXT NOT NULL DEFAULT '[]',
    overall_feedback_json TEXT NOT NULL DEFAULT '{}',
    overall_tips_json TEXT NOT NULL DEFAULT '[]',
    category_scores_json TEXT NOT NULL DEFAULT '{}',
    estimated_grade VARCHAR(50),
    is_gradable BOOLEAN NOT NULL DEFAULT 1,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at DATETIME
);

CREATE INDEX IF NOT EXISTS ix_evaluation_sessions_user_id ON evaluation_sessions(user_id);
CREATE INDEX IF NOT EXISTS ix_evaluation_sessions_mode ON evaluation_sessions(mode);
CREATE INDEX IF NOT EXISTS ix_evaluation_sessions_status ON evaluation_sessions(status);

CREATE TABLE IF NOT EXISTS evaluation_answers (
    id INTEGER PRIMARY KEY,
    session_id INTEGER NOT NULL REFERENCES evaluation_sessions(id),
    user_id INTEGER NOT NULL REFERENCES users(id),
    mode VARCHAR(20) NOT NULL,
    question_id VARCHAR(64) NOT NULL,
    question_order INTEGER NOT NULL DEFAULT 1,
    question_type VARCHAR(50),
    question_text TEXT NOT NULL,
    audio_file_path TEXT,
    audio_url TEXT,
    audio_duration_seconds FLOAT NOT NULL DEFAULT 0,
    original_transcript TEXT NOT NULL DEFAULT '',
    edited_transcript TEXT,
    used_transcript TEXT NOT NULL DEFAULT '',
    transcript_confidence FLOAT,
    stt_segments_json TEXT NOT NULL DEFAULT '[]',
    word_count INTEGER NOT NULL DEFAULT 0,
    sentence_count INTEGER NOT NULL DEFAULT 0,
    avg_sentence_length FLOAT NOT NULL DEFAULT 0,
    repetition_rate FLOAT NOT NULL DEFAULT 0,
    lexical_diversity FLOAT NOT NULL DEFAULT 0,
    keyword_similarity FLOAT NOT NULL DEFAULT 0,
    speech_duration_seconds FLOAT NOT NULL DEFAULT 0,
    silence_duration_seconds FLOAT NOT NULL DEFAULT 0,
    silence_ratio FLOAT NOT NULL DEFAULT 0,
    pause_count INTEGER NOT NULL DEFAULT 0,
    avg_pause_seconds FLOAT NOT NULL DEFAULT 0,
    speech_rate_wpm FLOAT NOT NULL DEFAULT 0,
    filler_count INTEGER NOT NULL DEFAULT 0,
    filler_ratio FLOAT NOT NULL DEFAULT 0,
    too_short BOOLEAN NOT NULL DEFAULT 0,
    too_much_silence BOOLEAN NOT NULL DEFAULT 0,
    is_gradable BOOLEAN NOT NULL DEFAULT 1,
    feedback_json TEXT NOT NULL DEFAULT '{}',
    estimated_sub_grade VARCHAR(50),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_evaluation_answers_session_question UNIQUE (session_id, question_id)
);

CREATE INDEX IF NOT EXISTS ix_evaluation_answers_session_id ON evaluation_answers(session_id);
CREATE INDEX IF NOT EXISTS ix_evaluation_answers_user_id ON evaluation_answers(user_id);
CREATE INDEX IF NOT EXISTS ix_evaluation_answers_mode ON evaluation_answers(mode);
CREATE INDEX IF NOT EXISTS ix_evaluation_answers_question_id ON evaluation_answers(question_id);

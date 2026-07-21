from prometheus_client import Counter, Gauge, Histogram

# Metrics for overall PR processing
PR_PROCESSED_TOTAL = Counter(
    "pr_processed_total",
    "Total number of Pull Requests processed by the AI Code Review system",
    ["status"] # 'success', 'failed'
)

# Metrics for AI Agent findings
FINDINGS_TOTAL = Counter(
    "findings_total",
    "Total number of bugs/issues found, labeled by agent and severity",
    ["agent", "severity"] # e.g. agent='security', severity='HIGH'
)

# Metrics for LLM-as-a-Judge Quality Score
JUDGE_SCORE_GAUGE = Gauge(
    "judge_confidence_score",
    "The latest confidence score (0.0 to 1.0) given by the Quality Evaluator"
)

# Metrics for LLM Token usage (to track costs)
LLM_TOKENS_TOTAL = Counter(
    "llm_tokens_total",
    "Total number of LLM tokens consumed",
    ["model", "type"] # model='llama-3.3-70b-versatile', type='prompt' or 'completion'
)

# Performance metric: how long reviews take
REVIEW_DURATION_SECONDS = Histogram(
    "review_duration_seconds",
    "Time taken to complete a full PR review",
    buckets=[5, 10, 30, 60, 120, 300, 600]
)

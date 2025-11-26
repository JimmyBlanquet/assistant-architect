#!/bin/bash
# Hook: on-code-generated
# Called when code is generated

# Log code generation (placeholder for metrics)
echo "[$(date -Iseconds)] CODE_GENERATED file=$FILE_PATH lines=$LINE_COUNT language=$LANGUAGE" >> /tmp/assistant-architect-metrics.log

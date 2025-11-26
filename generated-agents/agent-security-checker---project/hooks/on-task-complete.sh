#!/bin/bash
# Hook: on-task-complete
# Called when a task is completed

# Log task completion (placeholder for metrics)
echo "[$(date -Iseconds)] TASK_COMPLETE task=$TASK_NAME duration=$DURATION" >> /tmp/assistant-architect-metrics.log

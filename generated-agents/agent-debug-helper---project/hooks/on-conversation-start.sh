#!/bin/bash
# Hook: on-conversation-start
# Called when a new conversation begins

# Log session start (placeholder for metrics)
echo "[$(date -Iseconds)] SESSION_START user=$USER agent=$AGENT_TYPE" >> /tmp/assistant-architect-metrics.log

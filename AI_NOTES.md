## AI Assisted Development Overview

AI tools were used as accelerators, not as sources of truth.

All architectural decisions, data modeling, and failure handling logic were reviewed and corrected manually.

## Tools Used

* ChatGPT - For designing the flow
* GitHub Copilot - For syntax and minor function helpers

## Key Prompts Used

1. Design a reliable async processing system with retries and DLQ handling
2. Review this schema for idempotency and auditability issues
3. Suggest failure modes for background workers and how to handle them
4. Improve README clarity for recruiter audience

## What Was Accepted

* Initial schema scaffolding ideas
* High level retry and DLQ patterns
* Documentation structuring suggestions

## What Was Rejected or Modified

* Over simplified retry logic without persistence
* Suggestions to expose PHI in audit logs
* Code flow & API designs
* Blocking API flows on worker execution
* Missing idempotency enforcement at database level
* DB Designs which was not covering all the things

## Example AI Suggestion That Was Corrected

An early AI suggestion recommended retrying failed jobs purely in memory.

This was rejected.

Instead, retries are persisted in the database with attempt counts, timestamps, and failure reasons to ensure correctness across restarts and crashes.

This change improved reliability, auditability, and production safety.

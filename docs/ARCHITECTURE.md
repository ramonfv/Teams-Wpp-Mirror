# Architecture

## Current architecture

The current version is a local MVP for mirroring WhatsApp-like messages into Microsoft Teams and simulating the reverse Teams-to-WhatsApp flow.

At this stage, WhatsApp and Teams inbound messages are still mocked through FastAPI endpoints.

## Current flow: WhatsApp mock to Teams

```text
POST /mock/whatsapp/message
    → FastAPI
        → SQLite audit log
            → Channel mapping lookup
                → Teams webhook/workflow
                    → Teams channel
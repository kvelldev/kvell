# kvell

A BBS platform for the silent majority.

Kvell is a portfolio project exploring how to design an online discussion space
that minimizes noise, social pressure, and performative engagement.
It focuses on allowing users to express quiet, personal enthusiasm without
turning it into identity or competition.

## Concept

Instead of threads, replies, or likes, Kvell is built around three concepts:

- **Spark**: short, anonymous thoughts with a short lifespan
- **Kvell (Add Fuel)**: a lightweight action to ignite a spark by adding fuel.
- **Bonfire**: a spark that has been kvell-ed enough to become a shared discussion space.
- **Constellation**: archived, high-quality discussions (Not implemented for MVP)

> Note: “kvell” means “ignite（kuberu, くべる）” in Japanese.

The system structurally avoids metrics, replies, and notifications to reduce harassment and attention-seeking behavior.

For full product thinking and UX rationale, see the
[Inception Deck](./INCEPTION_DECK.md).

## Technical Highlights

- Simple and cost-aware architecture (FastAPI + React on AWS)
- Anonymous-by-design with minimal persistent user identity
- WebSocket-based real-time updates with load-shedding strategies
- Clean Architecture to keep AI-assisted code generation maintainable
- Solid prompts that force AI-generated code to remain consistent, testable, and maintainable (see [.prompts/](.prompts/) and other for details)


## License

This repository is published for portfolio and reference purposes only.
All rights are reserved. Reuse, redistribution, or modification is not permitted
without explicit permission.




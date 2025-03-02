# LLM-Powered People Network

A sophisticated platform that leverages Large Language Models to create meaningful connections between people based on their interests, skills, and goals.

Scripts in `scripts/` are for pruning and refining the scraped data.

Use case:

`python submit_batch.py` to process linkedin scrapes.

`python refine_profiles.py BATCH_ID` to run pruning and refinement.

`python retrieve_batch.py BATCH_ID` to download the batch job.

To test matching algorithms, use files found in `backend/networking_app`. 

`backend/networking_app/matching.py` contains key algorithms to produce matches given the people dataset.

`backend/networking_app/dialogue.py` contains the simluation of conversations.

## System Overview
[![image.png](https://i.postimg.cc/xCFjVKzh/image.png)](https://postimg.cc/sQ7CpGK4)

## Webapp

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│             │     │             │     │             │
│  Frontend   │────▶│   Backend   │────▶│ LLM Service │
│  (React)    │     │   (FastAPI) │     │             │
│             │◀────│             │◀────│             │
└─────────────┘     └──────┬──────┘     └─────────────┘
                           │
                           ▼
                    ┌─────────────┐     ┌─────────────┐
                    │             │     │             │
                    │ PostgreSQL  │────▶│   Vector    │
                    │  Database   │     │  Database   │
                    │             │◀────│             │
                    └─────────────┘     └─────────────┘
```
To self-host the webapp, use standard Next.js commands.

---
status: new
change_type: expand
changed_on: 2025-11-14
---

# Project Documentation Index

This file is the human-facing entry point to all long-term project docs.

## Core Project Docs

- `goal.md` – high-level project goal

- `concept.md` – conceptual model and scope

- `structure.md` – repository and module structure

- `status_human.md` – human-readable current status and roadmap

- `information_types.md` – information types, reliability, and validation model

## Specification (by area)

Planned structure (per documentation framework):

- `spec/index.md` – spec overview

- `spec/core.md` – MemorySystem core contract

- `spec/storage.md` – FileStorage (Markdown/JSON) semantics

- `spec/vector.md` – vector index semantics and retrieval

- `spec/graph.md` – Neo4j graph model and queries

- `spec/reflection.md` – Reflector and reflection flows

- `spec/compression.md` – compression semantics and token limits

- `spec/decay.md` – decay policies, archival/restore

- `spec/api.md` – future HTTP/API surface

_(These spec files can be created incrementally as the project stabilises in each area.)_

## AI-Facing Documentation

Machine-readable documentation for AI agents:

- `../_ai/ai_project_map.yaml` – structured project map for agents
- `../_ai/ai_context.md` – context and orientation for AI agents
- `../_ai/ai_status.md` – current status in machine-readable format
- `../_ai/ai_guidelines.md` – guidelines and constraints for AI agents

## Other Documentation Areas

See the general framework:

- `../architecture/` – diagrams and flows

- `../engineering/` – coding standards, testing, CI/CD

- `../ops/` – running services, troubleshooting, deployments

- `../usage/` – CLI & Python API usage, tutorials

- `../decisions/` – ADRs

- `../research/` – experiments, benchmarks, evals

The goal is that a human can start from here and navigate to any relevant area

without having to read the entire codebase first.


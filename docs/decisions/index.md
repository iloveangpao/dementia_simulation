# Architecture Decision Records

This section contains Architecture Decision Records (ADRs) documenting key technical decisions for the Dementia Simulation platform.

## What are ADRs?

Architecture Decision Records (ADRs) are documents that capture important architectural decisions along with their context and consequences. They help:

- Understand why decisions were made
- Onboard new team members
- Review past choices
- Avoid repeating mistakes

We use the [MADR](https://adr.github.io/madr/) (Markdown Any Decision Records) template.

## Decision Records

### [ADR-0001: Documentation Stack](ADR-0001-docs-stack.md)

**Status**: Accepted  
**Date**: 2024-01-15

Decision to use MkDocs + Material theme + mkdocstrings for project documentation.

**Context**: Need comprehensive, maintainable documentation  
**Decision**: MkDocs with Material theme and mkdocstrings  
**Consequences**: Auto-generated API docs, Diátaxis framework, GitHub Pages deployment

---

## Future ADRs

Placeholder for upcoming decisions:

### ADR-0002: RAG Citation Strategy

**Status**: Proposed

Decision on how to implement and display citations in RAG responses.

Topics to address:
- Citation format (inline, footer, numbered)
- Source tracking mechanism
- UI/UX considerations
- Performance impact

### ADR-0003: FAISS vs Alternative Vector DBs

**Status**: Proposed

Evaluation of FAISS vs alternatives (Pinecone, Weaviate, Qdrant) for vector search.

Topics to address:
- Scalability requirements
- Cost analysis
- Feature comparison
- Migration path

### ADR-0004: LLM Model Selection

**Status**: Proposed

Decision on default LLM model(s) and selection criteria.

Topics to address:
- Quality vs. resource tradeoff
- Local vs. API models
- Multi-model support
- Fine-tuning strategy

### ADR-0005: Session Storage

**Status**: Proposed

Decision on session storage mechanism (filesystem, database, cache).

Topics to address:
- Persistence requirements
- Scalability needs
- Privacy considerations
- Query patterns

## ADR Process

### Creating a New ADR

1. Copy the MADR template
2. Fill in sections:
   - Context and Problem Statement
   - Decision Drivers
   - Considered Options
   - Decision Outcome
   - Consequences
3. Submit for review
4. Update status when decided

### Template

```markdown
# [short title of solved problem]

* Status: [proposed | rejected | accepted | deprecated | superseded by [ADR-0005](0005-example.md)]
* Date: [YYYY-MM-DD when decision was made]
* Deciders: [list everyone involved in the decision]

## Context and Problem Statement

[Describe the context and problem statement, e.g., in free form using two to three sentences. You may want to articulate the problem in form of a question.]

## Decision Drivers

* [driver 1, e.g., a force, facing concern, ...]
* [driver 2, e.g., a force, facing concern, ...]
* ...

## Considered Options

* [option 1]
* [option 2]
* [option 3]
* ...

## Decision Outcome

Chosen option: "[option 1]", because [justification. e.g., only option, which meets k.o. criterion decision driver | which resolves force force | ... | comes out best (see below)].

### Positive Consequences

* [e.g., improvement of quality attribute satisfaction, follow-up decisions required, ...]
* ...

### Negative Consequences

* [e.g., compromising quality attribute, follow-up decisions required, ...]
* ...

## Pros and Cons of the Options

### [option 1]

[example | description | pointer to more information | ...]

* Good, because [argument a]
* Good, because [argument b]
* Bad, because [argument c]
* ...

### [option 2]

[example | description | pointer to more information | ...]

* Good, because [argument a]
* Good, because [argument b]
* Bad, because [argument c]
* ...

### [option 3]

[example | description | pointer to more information | ...]

* Good, because [argument a]
* Good, because [argument b]
* Bad, because [argument c]
* ...

## Links

* [Link type] [Link to ADR] <!-- example: Refined by [ADR-0005](0005-example.md) -->
* ...
```

## Resources

- [MADR Template](https://adr.github.io/madr/)
- [ADR GitHub Organization](https://adr.github.io/)
- [Architectural Decision Records](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions)
- [ADR Tools](https://github.com/npryce/adr-tools)

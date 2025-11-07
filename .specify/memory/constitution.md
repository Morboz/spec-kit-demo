<!--
SYNC IMPACT REPORT
Version change: NEW → 1.0.0 (initial ratification)
Modified principles: N/A (new constitution)
Added sections:
- Core Principles (I-V): Incremental Development, Test-First Development, Modular Architecture, Rules Compliance, Clear Documentation
- Development Workflow: Specifies framework workflow with phases
- Governance: Amendment procedure, versioning policy, compliance review requirements
Removed sections: N/A
Templates updated: ✅ /root/blokus-step-by-step/.specify/templates/plan-template.md (Constitution Check gates populated)
Follow-up TODOs: None
-->

# Blokus Step by Step Constitution

## Core Principles

### I. Incremental Development
Every feature MUST be implemented in small, verifiable steps. Each increment MUST be independently testable and deliver visible value. Document the reasoning, approach, and expected outcome for each step before implementation begins.

**Rationale**: The "step-by-step" nature of this project demands methodical progress. Breaking complex game logic into small increments reduces risk, enables early validation, and makes debugging significantly easier.

### II. Test-First Development
TDD is mandatory for all game logic and rules. Tests MUST be written first, verified to fail, then implementation proceeds until tests pass. Red-Green-Refactor cycle MUST be strictly enforced. Every Blokus rule MUST have corresponding test cases covering valid and invalid scenarios.

**Rationale**: Game rules are complex and have many edge cases. Test-first development ensures correctness, prevents regressions, and serves as executable documentation of game behavior.

### III. Modular Architecture
Game components MUST be loosely coupled and highly cohesive. Board, pieces, players, game state, and rules MUST be separate modules with clear, documented interfaces. Dependencies MUST flow in one direction (toward core game state).

**Rationale**: Clear separation of concerns makes the codebase navigable, enables independent testing of components, and facilitates future enhancements or rule variations.

### IV. Rules Compliance
All official Blokus rules MUST be implemented exactly as specified. Invalid moves MUST be rejected with clear, actionable error messages. Game state validation MUST occur after every move to ensure integrity.

**Rationale**: Correct implementation of game rules is non-negotiable for a game project. Players must trust that the digital version adheres to established rules.

### V. Clear Documentation
Every public interface MUST have clear documentation. User scenarios from the specification MUST be reflected in both tests and documentation. The quickstart guide MUST enable a new developer to understand and run the project within 10 minutes.

**Rationale**: The "step-by-step" approach requires exceptional documentation so readers can follow the implementation logic. Clear docs also serve as the primary onboarding material for contributors.

## Development Workflow

All feature development MUST follow the Specify framework workflow:

- **Specification Phase**: Define user stories with acceptance criteria BEFORE implementation
- **Plan Phase**: Create implementation plan with task breakdown by user story
- **Test Phase**: Write tests first (TDD), ensure they fail
- **Implementation Phase**: Implement minimally to pass tests
- **Validation Phase**: Verify each user story works independently

**Rationale**: The templates provide a proven structure for building correct software incrementally. Following this workflow ensures consistency and quality.

## Governance

This constitution supersedes all other development practices. All pull requests and code reviews MUST verify compliance with these principles. Any complexity introduced MUST be justified with clear reasoning and documented in the complexity tracking section of the implementation plan.

### Amendment Procedure

To amend this constitution:
1. Propose changes in a pull request with clear rationale
2. Document how changes affect existing codebases
3. Update version number according to semantic versioning (see below)
4. Require approval from project maintainers
5. Update dependent templates to reflect new requirements

### Versioning Policy

This constitution uses semantic versioning:
- **MAJOR** (X.0.0): Backward-incompatible changes to principles or governance
- **MINOR** (X.Y.0): New principles added or materially expanded guidance
- **PATCH** (X.Y.Z): Clarifications, wording fixes, non-semantic refinements

### Compliance Review

Every pull request MUST include a "Constitution Check" section verifying:
- [ ] Incremental approach used (Principle I)
- [ ] Tests written first for new features (Principle II)
- [ ] Modular boundaries respected (Principle III)
- [ ] Rules correctly implemented (Principle IV)
- [ ] Documentation updated (Principle V)

**Version**: 1.0.0 | **Ratified**: 2025-10-30 | **Last Amended**: 2025-10-30

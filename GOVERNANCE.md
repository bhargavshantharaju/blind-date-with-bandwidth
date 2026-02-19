# Project Governance

## Overview

Blind Date with Bandwidth is led by a core maintainer team with an open contribution model. We welcome submissions from the community and welcome new maintainers with demonstrated commitment.

## Roles & Responsibilities

### Maintainers (Steering Committee)

**Current Maintainers:**
- `[Primary Maintainer]` - Project lead, release management
- `[Secondary Maintainer]` - Code review, performance optimization
- `[Community Manager]` - Community engagement, documentation

**Responsibilities:**
- Make final decisions on accepted features and bug fixes
- Release new versions (semantic versioning)
- Manage GitHub labels, milestones, and project board
- Facilitate security disclosures
- Mentor new contributors

**Eligibility:**
- Minimum 3 merged PRs
- 6 months of active contribution
- Demonstrated understanding of project goals
- Agreement to abide by Code of Conduct

### Contributors

Anyone who submits a PR or issue is a contributor! Contributors:
- Submit features, bug fixes, documentation
- Participate in code review
- Engage in discussions respectfully
- Help triage issues

### Emeritus Status

Long-term maintainers may transition to emeritus status, retaining credit but passing day-to-day responsibilities to active maintainers.

## Decision Making Process

### Minor Decisions (Bug Fixes, Documentation, Refactoring)
- Single maintainer approval
- Merged when tests pass
- No public discussion required

### Medium Decisions (New Features, Performance Changes)
- Issues discussing design for 1 week
- PR review from 2+ maintainers
- Community feedback invited via GitHub Discussions
- Merged with consensus

### Major Decisions (API Changes, Architecture Redesigns, Deprecations)
- RFC (Request for Comments) issue posted
- 2-week discussion period
- Voting by maintainers (unanimous required unless 75%+ agree)
- Implementation by RFC author or assigned maintainer

## Contributor Pathway

```
New Contributor
      ↓
Submit PR (3 accepted PRs needed to be considered)
      ↓
Engage in Issues & Discussions (6+ months)
      ↓
Understand Codebase (submit complex features)
      ↓
Nominated as Maintainer
      ↓
Approval by existing maintainers (unanimous)
      ↓
New Maintainer! 🎉
```

## Release Management

- **Version Scheme**: SemVer (MAJOR.MINOR.PATCH)
  - MAJOR: Incompatible API changes
  - MINOR: Backwards-compatible new features
  - PATCH: Bug fixes

- **Release Cadence**: Every 4-6 weeks
  - Security fixes: ASAP (emergency release)
  - Major features: Batched in minor releases

- **Branch Strategy**:
  - `main`: Production-ready code, always tagged
  - `develop`: Next release (integration branch)
  - Feature branches: `feature/description` (owned by contributor)

## Communication Channels

- **Issues**: Bug reports, feature requests
- **Discussions**: Design decisions, general questions
- **GitHub Wikis**: How-to guides, FAQ
- **Email**: conduct@[domain] for sensitive matters

## Feedback & Improvements

This governance document is a living document. Suggest improvements via:
1. GitHub Issues (tag with `governance`)
2. Email to `conduct@[domain]`
3. Quarterly review calls (open to all)

---

**Last Updated**: 2024-01-XX  
**Next Review**: 2024-07-XX

# Code Review Perspectives

Comprehensive review checklist for actionable feedback.

## 1. Correctness

- Logic errors or edge cases
- Null/undefined handling
- Off-by-one errors
- Race conditions
- Resource leaks

## 2. Security

- Input validation (injection, XSS, SQLi)
- Authentication/authorization gaps
- Sensitive data exposure
- Hardcoded secrets
- Insecure dependencies

## 3. Performance

- Unnecessary loops or allocations
- N+1 queries
- Missing indexes
- Memory leaks
- Blocking operations in async code

## 4. Maintainability

- Code duplication
- Complex conditionals
- Magic numbers/strings
- Naming clarity
- Single responsibility violations

## 5. Testing

- Test coverage gaps
- Missing edge case tests
- Flaky test patterns
- Test isolation issues
- Assertion quality

## 6. API Design

- Breaking changes
- Consistency with existing patterns
- Error handling conventions
- Documentation completeness

## 7. Dependencies

- Version pinning
- License compatibility
- Unnecessary dependencies
- Security vulnerabilities

## 8. Platform/Framework Specific

- iOS: Memory management, main thread usage, accessibility
- Web: Browser compatibility, bundle size, SEO
- Backend: Database transactions, connection pooling, logging

# ID POLICY (PHASE 0)

1. IDs are immutable once published.
2. Deterministic generation only (no GUID runtime generation).
3. Stable ordering keys are required for ordered emits.
4. References must point to existing targets; missing refs fail closed.
5. Any aliasing introduced later must be acyclic and explicitly validated.

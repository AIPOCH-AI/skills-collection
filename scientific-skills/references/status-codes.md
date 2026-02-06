# Clinical Trial Status Codes

## Overall Status Values

| Status | Description |
|--------|-------------|
| `RECRUITING` | Actively enrolling participants |
| `ACTIVE_NOT_RECRUITING` | Ongoing but not recruiting |
| `NOT_YET_RECRUITING` | Not yet open for recruitment |
| `COMPLETED` | Study completed normally |
| `SUSPENDED` | Temporarily halted |
| `TERMINATED` | Prematurely ended |
| `WITHDRAWN` | Withdrawn before enrollment |
| `WITHHELD` | Withheld from public view |
| `UNKNOWN` | Status unknown |

## Phase Values

| Phase | Description |
|-------|-------------|
| `EARLY_PHASE1` | Early Phase 1 (exploratory) |
| `PHASE1` | Phase 1 (safety/dosage) |
| `PHASE2` | Phase 2 (efficacy) |
| `PHASE3` | Phase 3 (efficacy/monitoring) |
| `PHASE4` | Phase 4 (post-marketing) |

## Why Status Changes

### Common Status Transitions

1. `NOT_YET_RECRUITING` → `RECRUITING`
   - Study opens for enrollment

2. `RECRUITING` → `ACTIVE_NOT_RECRUITING`
   - Enrollment target reached

3. `RECRUITING` → `SUSPENDED`
   - Temporary hold (safety, administrative)

4. `RECRUITING`/`ACTIVE_NOT_RECRUITING` → `COMPLETED`
   - Study finished successfully

5. `RECRUITING` → `TERMINATED`
   - Early termination (futility, safety, business)

## Monitoring Priority

### High Priority Changes
- RECRUITING → SUSPENDED (safety concern)
- RECRUITING → TERMINATED (competitive impact)
- ACTIVE_NOT_RECRUITING → COMPLETED (results coming)

### Medium Priority Changes
- NOT_YET_RECRUITING → RECRUITING (new competition)
- Phase advancement (PHASE1 → PHASE2)

### Low Priority Changes
- WITHDRAWN (no competitive impact)
- Date updates without status change

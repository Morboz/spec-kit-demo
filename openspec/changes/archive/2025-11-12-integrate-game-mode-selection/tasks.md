# Tasks: Integrate Game Mode Selection

## Implementation Checklist

### Phase 1: Data Model Updates
- [ ] 1.1 Extend GameModeType enum to include PvP_LOCAL mode
- [ ] 1.2 Add PvP configuration support to GameMode class
- [ ] 1.3 Create GameMode.pvp_local() factory method
- [ ] 1.4 Add validation for PvP mode (2-4 players)
- [ ] 1.5 Write unit tests for new GameMode functionality

### Phase 2: Unified UI Component
- [ ] 2.1 Create UnifiedGameModeSelector class
- [ ] 2.2 Implement mode selection UI (4 modes: Single AI, Three AI, Spectate, PvP)
- [ ] 2.3 Add dynamic configuration UI based on selected mode
  - [ ] AI difficulty selector (for AI modes)
  - [ ] Player count selector (for PvP mode)
  - [ ] Player name inputs (for PvP mode)
  - [ ] Common settings (board size, color scheme)
- [ ] 2.4 Add form validation and error handling
- [ ] 2.5 Write unit tests for UnifiedGameModeSelector

### Phase 3: Integration with GameSetupManager
- [ ] 3.1 Update GameSetupManager.show_setup() to use unified selector
- [ ] 3.2 Handle PvP mode configuration
- [ ] 3.3 Handle AI mode configuration (preserve existing logic)
- [ ] 3.4 Handle Spectate mode (preserve existing logic)
- [ ] 3.5 Add integration tests for setup flow

### Phase 4: Testing & Validation
- [ ] 4.1 Update integration tests to verify unified dialog
- [ ] 4.2 Test all game modes through new UI
- [ ] 4.3 Verify CLI parameter --spectate still works
- [ ] 4.4 Run full test suite (251 unit tests + integration tests)
- [ ] 4.5 Manual testing of game startup flow

### Phase 5: Cleanup
- [ ] 5.1 Remove old GameModeSelector if no longer used
- [ ] 5.2 Update main.py comments to reflect new flow
- [ ] 5.3 Update any relevant documentation
- [ ] 5.4 Final validation with openspec validate

## Dependencies
- Task 1.1 must complete before 2.1
- Task 2.1-2.4 must complete before 3.1
- Task 3.x must complete before 4.1

## Testing Strategy
- Unit tests: Validate individual components
- Integration tests: Validate complete setup flow
- Manual tests: Validate user experience

## Estimated Effort
- Data model: 1-2 tasks
- UI component: 3-4 tasks (most complex)
- Integration: 3-4 tasks
- Testing: 3-4 tasks
- Total: ~10-14 tasks

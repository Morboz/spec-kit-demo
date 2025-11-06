## MODIFIED Requirements

### Requirement: All contract tests pass
当前有18个contract测试失败，需要修正测试用例中的错误坐标位置。源码验证逻辑是正确的，问题是测试设计错误。所有contract测试**SHALL**通过验证。

#### Scenario: Board bounds tests corrected
**Given:** Board bounds validation tests
**When:** 测试使用正确的位置坐标
**Then:** 所有7个测试通过
**Changes:**
- test_piece_at_bottom_boundary_is_valid: 修正位置坐标确保与角落棋子形成对角接触
- test_piece_at_right_boundary_is_valid: 修正位置坐标确保与角落棋子形成对角接触
- test_large_piece_at_corner_within_bounds: 修正位置坐标确保对角接触
- test_rotated_piece_within_bounds: 修正位置坐标确保对角接触

#### Scenario: Move validation tests corrected
**Given:** Move validation tests
**When:** 测试使用正确的游戏状态和位置坐标
**Then:** 所有4个测试通过
**Changes:**
- test_validate_non_first_move_can_be_anywhere_valid: 添加第二个玩家
- test_validate_piece_not_already_placed: 确保有对角接触
- test_validate_edge_contact_with_own_pieces_not_allowed: 修正坐标避免意外的对角接触
- test_validate_diagonal_contact_with_own_pieces_allowed: 修正坐标确保对角接触

#### Scenario: Overlap detection tests corrected
**Given:** Overlap detection tests
**When:** 测试使用能形成对角接触的位置坐标
**Then:** 所有5个测试通过
**Changes:**
- test_piece_without_overlap_is_valid: 修正位置确保对角接触
- test_adjacent_without_overlap_is_valid: 修正位置确保对角接触
- test_diagonal_without_overlap_is_valid: 修正位置确保对角接触
- test_touching_corner_is_not_overlap: 修正位置确保对角接触
- test_all_occupied_positions_tracked: 修正位置确保对角接触

#### Scenario: Score calculation tests corrected
**Given:** Score calculation tests
**When:** 游戏状态正确初始化
**Then:** 所有3个测试通过
**Changes:**
- 确保所有必要玩家已添加
- 确保游戏状态正确设置

#### Scenario: Skip turn tests corrected
**Given:** Skip turn tests
**When:** 回合管理逻辑与测试期望一致
**Then:** 所有3个测试通过
**Changes:**
- test_eliminated_player_cannot_skip: 修正测试逻辑
- test_skip_turn_with_active_and_passed_players: 修正测试逻辑
- test_skip_turn_with_eliminated_players: 修正测试逻辑

#### Scenario: First move rule tests corrected
**Given:** First move rule test
**When:** 游戏状态正确初始化
**Then:** 测试通过
**Changes:**
- test_corner_after_first_move_can_have_diagonal_contact: 确保正确的位置坐标

## Implementation Approach
所有修改都在测试文件中，源码逻辑保持不变：
1. 计算正确的棋子位置以确保对角接触
2. 添加缺失的玩家或游戏状态初始化
3. 修正回合管理相关的测试逻辑

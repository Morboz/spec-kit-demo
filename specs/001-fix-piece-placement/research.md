# Research Report: Piece Placement Interaction Bug

**Date**: 2025-10-30
**Feature**: 001-fix-piece-placement
**Status**: Debugging Analysis Complete

## Executive Summary

通过代码分析，发现 piece 选择后点击棋盘无响应的根本原因是**交互链路的回调连接不完整**。问题出现在 PieceSelector → main.py → PlacementHandler → Board Click 的流程中。

## 调试发现

### 交互流程分析

完整交互链路应该是：
```
1. 用户在 PieceSelector 中点击 piece
   → PieceSelector._select_piece() 调用 on_piece_selected 回调
   → main.py._on_piece_selected() 被调用

2. main.py._on_piece_selected() 调用 placement_handler.select_piece()
   → PlacementHandler 创建新的 Piece 实例
   → 设置 self.selected_piece

3. 用户点击棋盘
   → main.py._setup_board_click_handling().on_canvas_click() 被调用
   → 检查 self.placement_handler.selected_piece
   → 调用 placement_handler.place_piece()
```

### 发现的问题

#### 问题 1: 回调设置时机问题（高优先级）
**位置**: `main.py:223-227`

```python
# Initialize placement handler
current_player = self.game_state.get_current_player()
if current_player:
    self.placement_handler = PlacementHandler(
        self.game_state.board, self.game_state, current_player
    )
    self._setup_callbacks()  # 在这里设置 callbacks
```

但是 `PieceSelector` 是在之后创建的（line 355），此时回调可能未完全初始化。

**修复方案**:
- 确保在创建 `PieceSelector` 之前，`placement_handler` 已经完成初始化
- 或者将 `_setup_callbacks()` 延迟到 `PieceSelector` 创建之后

#### 问题 2: 状态同步问题（高优先级）
**位置**: `main.py:354-360`

```python
if current_player:
    self.piece_selector = PieceSelector(
        middle_left_panel,
        current_player,  # 使用当前的 current_player
        on_piece_selected=self._on_piece_selected,
    )
```

问题：当玩家轮换时，`PieceSelector` 仍然持有初始的 `current_player` 引用，而不是当前回合的玩家。

**修复方案**:
- 在 `state_synchronizer.notify_turn_change()` 时更新 `PieceSelector` 的 player 引用
- 或者让 `PieceSelector` 从 `game_state` 动态获取当前玩家

#### 问题 3: 缺少详细日志（中等优先级）
**现状**: 当前代码缺少调试日志，难以追踪问题。

**修复方案**:
- 在关键交互点添加日志：
  - `PlacementHandler.select_piece()` 开始/结束
  - `PlacementHandler.selected_piece` 状态变化
  - `BoardClickHandler.handle_click()` 被调用
  - 验证失败的原因

#### 问题 4: 视觉反馈缺失（中等优先级）
**需求**: FR-006 和 FR-007 要求选中 piece 和悬停预览的视觉反馈。

**现状检查**:
- `PieceSelector` 有按钮按下状态（line 94-103）
- 但 `PlacementHandler` 没有对应的视觉状态管理
- `placement_preview.py` 存在但未在主循环中使用

**修复方案**:
- 确保选中 piece 时 UI 有明显反馈
- 实现悬停预览功能

## 技术决策

### 决策 1: 优先修复交互链路
**选择**: 优先修复 PieceSelector → PlacementHandler → Board Click 的回调连接
**理由**: 这是核心功能，没有它游戏无法进行
**替代方案**: 添加完整的错误日志系统（被拒绝，因为会延迟核心修复）

### 决策 2: 使用现有架构
**选择**: 复用现有的 PlacementHandler、BoardClickHandler、PieceSelector 组件
**理由**: 这些组件已有完整功能，只需要修复连接
**替代方案**: 重写整个交互系统（被拒绝，工作量过大且风险高）

### 决策 3: 保持测试向后兼容
**选择**: 确保修复不破坏现有测试
**理由**: 已有的测试套件覆盖了关键路径
**替代方案**: 修改测试以适应新实现（被拒绝，测试应该验证正确行为）

## 待解决的问题

### 需要立即修复的问题
1. **PieceSelector 回调连接**: 确保 `_on_piece_selected` 被正确调用
2. **PlacementHandler 状态**: 确保 `selected_piece` 被正确设置和获取
3. **Board Click 验证**: 确保点击事件正确触发和验证

### 后续改进
1. **错误日志**: 添加结构化日志记录
2. **视觉反馈**: 实现选中状态和预览效果
3. **测试覆盖**: 添加调试和回归测试

## 验证计划

### 验证步骤
1. 运行现有的集成测试
2. 添加调试日志，运行手动测试
3. 验证修复后所有用户场景正常工作
4. 确认错误处理和日志记录功能

### 测试检查点
- [ ] 用户可以选择 piece（视觉反馈）
- [ ] 选择 piece 后点击棋盘有响应
- [ ] 非法位置显示错误消息
- [ ] 合法位置成功放置 piece
- [ ] 错误日志记录所有失败尝试

## 结论

bug 的根本原因是**回调连接不完整**，导致 piece 选择状态没有正确传递到 board click handler。修复需要：

1. 确保回调在正确的时机设置
2. 同步玩家状态变更
3. 添加调试日志以便未来诊断

这些修复都是低风险的，因为它们只涉及连接现有组件，不改变核心游戏逻辑。

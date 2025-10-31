# Piece Selection Contract

**Component**: PieceSelector → PlacementHandler
**Date**: 2025-10-30

## Overview

定义玩家从 piece 库存中选择 piece 的交互契约。

## Request Contract

### PieceSelector._select_piece()

**触发条件**:
- 用户点击 PieceSelector 中的 piece 按钮
- Piece 未被放置
- Piece 属于当前玩家

**输入参数**:
```python
piece_name: str  # 要选择的 piece 名称，如 "I1", "L4", "T5"
```

**状态要求**:
- `PieceSelector.selected_piece` = piece_name
- Piece 按钮显示选中状态（pressed）

**调用顺序**:
1. 更新本地 selected_piece 状态
2. 高亮对应按钮
3. 调用 on_piece_selected 回调

**错误处理**:
- 如果 piece 不存在：显示错误消息，保持无选择状态
- 如果 piece 已放置：禁用按钮，不允许选择

## Response Contract

### PlacementHandler.select_piece()

**输入参数**:
```python
piece_name: str
```

**返回类型**:
```python
bool  # True: 选择成功, False: 选择失败
```

**成功响应**:
- 设置 `PlacementHandler.selected_piece` 为新的 Piece 实例
- 重置 rotation_count = 0
- 重置 is_flipped = False
- 返回 True

**失败响应**:
- 如果 piece 不存在：调用 on_placement_error，返回 False
- 如果 piece 已放置：调用 on_placement_error，返回 False
- `selected_piece` 保持不变

**状态变化**:
```
PlacementHandler.selected_piece: None → Piece(name=piece_name)
PlacementHandler.rotation_count: 任意值 → 0
PlacementHandler.is_flipped: 任意值 → False
```

## Callback Contract

### on_piece_selected 回调

**调用方**: PieceSelector
**接收方**: main.py._on_piece_selected

**调用时机**:
- 用户成功选择 piece 后
- 在设置选中状态和视觉反馈之后

**输入参数**:
```python
piece_name: str  # 被选择的 piece 名称
```

**期望行为**:
1. 调用 `placement_handler.select_piece(piece_name)`
2. 如果成功，调用 `piece_display.set_piece(selected_piece)`
3. 如果失败，显示错误消息

**错误处理**:
- 如果 placement_handler 不存在：记录错误日志，返回
- 如果选择失败：显示错误消息，不更新 piece_display

## Visual Feedback Contract

### Piece Selector 视觉状态

**未选中状态**:
- 按钮背景色：默认
- 按钮文字：正常
- 按钮状态：!pressed

**悬停状态**:
- 鼠标悬停时：按钮高亮（如果可选择）

**选中状态**:
- 按钮背景色：选中颜色（如蓝色）
- 按钮文字：加粗
- 按钮状态：pressed

**禁用状态**（piece 已放置）:
- 按钮背景色：灰色
- 按钮文字：淡色
- 按钮状态：disabled
- 点击无响应

## State Synchronization

### 与 PieceDisplay 同步

**触发条件**:
- `placement_handler.select_piece()` 返回 True
- `placement_handler.get_selected_piece()` 返回非 None

**同步操作**:
```python
selected_piece = placement_handler.get_selected_piece()
if selected_piece:
    piece_display.set_piece(selected_piece)
```

### 与其他 UI 组件同步

**Board Preview**（待实现）:
- 显示选中 piece 的轮廓
- 在鼠标悬停时显示预览

**Current Player Indicator**:
- 显示当前选中的 piece 数量减少

## 测试检查点

- [ ] 点击未放置的 piece → 选择成功
- [ ] 点击已放置的 piece → 选择失败，显示错误
- [ ] 选择 piece → 视觉状态更新（按钮 pressed）
- [ ] 选择 piece → piece_display 显示 piece
- [ ] 选择 piece → PlacementHandler.selected_piece 设置正确
- [ ] 选择 piece → 错误日志记录选择事件

## 已知问题和修复

### 问题 1: 回调设置时机
**症状**: `on_piece_selected` 可能未被调用
**原因**: `PieceSelector` 在 `placement_handler` 初始化之前创建
**修复**: 确保 `_setup_callbacks()` 在创建 `PieceSelector` 之前调用

### 问题 2: 状态不同步
**症状**: 选择 piece 后，`placement_handler.selected_piece` 为 None
**原因**: `PieceSelector` 持有过时的 player 引用
**修复**: 在玩家轮换时更新 `PieceSelector` 的 player 引用

# Board Click Contract

**Component**: Board Canvas → PlacementHandler
**Date**: 2025-10-30

## Overview

定义用户点击棋盘进行 piece 放置的交互契约。

## Request Contract

### Board Canvas Click Event

**触发条件**:
- 用户在棋盘 Canvas 上点击鼠标左键
- 位置在棋盘范围内（0 ≤ row < 20, 0 ≤ col < 20）

**输入参数**:
```python
event.x: float  # 点击的 Canvas X 坐标
event.y: float  # 点击的 Canvas Y 坐标
```

**预处理步骤**:
1. 将 Canvas 坐标转换为棋盘网格坐标
   ```python
   cell_size = game_config.cell_size or 30
   board_row = canvas_y // cell_size
   board_col = canvas_x // cell_size
   ```
2. 验证位置在棋盘范围内
   ```python
   if not board.is_position_valid(board_row, board_col):
       show_error("Position is outside board bounds")
       return
   ```

## Response Contract

### PlacementHandler.place_piece()

**输入参数**:
```python
row: int  # 目标行 (0-19)
col: int  # 目标列 (0-19)
```

**返回类型**:
```python
Tuple[bool, Optional[str]]
# (success, error_message)
```

**成功响应**:
- 返回 `(True, None)`
- 更新 Board.grid
- 更新 Player.pieces
- 记录 Move 到 GameState
- 调用 `on_piece_placed` 回调
- 调用 `next_turn()` 切换玩家
- 清除 selected_piece

**失败响应**:
- 返回 `(False, error_message)`
- 不更新任何状态
- 调用 `on_placement_error` 回调
- 保持 selected_piece 不变

**错误类型**:
1. **No Piece Selected**: "No piece selected"
2. **Validation Failed**: 具体验证错误（来自 BlokusRules）
   - "First piece must be placed in a corner"
   - "Piece cannot be adjacent to your own pieces"
   - "Position is outside board bounds"
   - "Position is occupied"
   - "Piece does not fit at this position"

## Callback Contract

### on_piece_placed 回调

**调用方**: PlacementHandler
**接收方**: main.py._on_piece_selected().on_piece_placed（嵌套回调）

**调用时机**:
- `place_piece()` 返回 (True, None) 后
- 在更新所有游戏状态后
- 在切换玩家之前

**输入参数**:
```python
piece_name: str  # 已放置的 piece 名称
```

**期望行为**:
1. 刷新 PieceSelector：`piece_selector.refresh()`
2. 清除 PieceDisplay：`piece_display.clear()`
3. 重新渲染棋盘：`_render_board()`
4. 通知 StateSynchronizer 更新
5. 显示成功消息
6. 切换到下一个玩家

### on_placement_error 回调

**调用方**: PlacementHandler
**接收方**: main.py._setup_callbacks().on_placement_error

**调用时机**:
- `place_piece()` 返回 (False, error_message) 后
- 在任何验证失败时

**输入参数**:
```python
error_msg: str  # 详细的错误消息
```

**期望行为**:
1. 显示错误对话框：`messagebox.showerror("Invalid Move", error_msg)`
2. 记录错误日志
3. 保持 piece 选中状态
4. 允许用户尝试其他位置

## Visual Feedback Contract

### Board 渲染

**成功放置后**:
- 重新渲染整个棋盘
- 显示新放置的 piece（使用玩家颜色）
- 清除任何预览效果

**验证失败时**（待实现）:
- 高亮无效位置
- 显示红色边框
- 保持预览状态

### PieceSelector 更新

**成功放置后**:
- 调用 `piece_selector.refresh()`
- 移除已放置的 piece 按钮
- 清除当前选择

**验证失败时**:
- 保持 piece 按钮选中状态
- 不刷新 piece 列表

### 预览效果（FR-007）

**待实现功能**:
- 鼠标悬停时显示 piece 轮廓
- 半透明显示（alpha = 0.5）
- 绿色（合法位置）或红色（非法位置）

**实现位置**:
- `src/ui/placement_preview.py`（已存在，需要集成）

## 状态变化

### 成功放置的状态转换

**PlacementHandler**:
```python
selected_piece: Piece → None
rotation_count: 保持不变 → 0
is_flipped: 保持不变 → False
```

**Board**:
```python
grid[(row, col)]: None → player_id
player_positions[player_id]: 追加 (row, col)
```

**Player**:
```python
pieces[piece_name].is_placed: False → True
pieces[piece_name].position: None → (row, col)
pieces_remaining: N → N-1
```

**GameState**:
```python
move_history: 追加新 Move 记录
current_player_index: 递增（环绕）
```

### 失败时的状态保持

**所有状态**:
- 保持放置前的状态
- 不回滚任何更改
- 允许用户重试

## 错误日志记录

### placement_failed 事件

**记录时机**:
- `on_placement_error` 被调用时

**日志字段**:
```json
{
  "timestamp": "2025-10-30T10:30:00",
  "event": "placement_failed",
  "player_id": "P1",
  "piece_name": "I1",
  "position": {"row": 10, "col": 10},
  "error_type": "validation",
  "error_message": "First piece must be placed in a corner",
  "error_code": "RULE_FIRST_MOVE"
}
```

**位置**: `src/game/error_handler.py`

## 测试检查点

- [ ] 已选择 piece 时点击合法位置 → 放置成功
- [ ] 已选择 piece 时点击非法位置 → 显示错误消息
- [ ] 未选择 piece 时点击棋盘 → 无响应或提示选择 piece
- [ ] 成功放置 → 棋盘更新显示
- [ ] 成功放置 → piece 从库存中移除
- [ ] 成功放置 → 玩家轮换
- [ ] 放置失败 → 错误消息显示
- [ ] 放置失败 → 错误日志记录
- [ ] 放置失败 → 保持 piece 选中状态

## 已知问题和修复

### 问题 1: Click Handler 早返回
**症状**: 点击棋盘无任何响应
**位置**: `main.py:501`
```python
if not self.placement_handler or not self.placement_handler.selected_piece:
    return
```
**原因**: `selected_piece` 可能为 None 或未正确设置
**修复**: 添加调试日志，检查 `selected_piece` 状态

### 问题 2: 缺少错误日志
**症状**: 失败时没有调试信息
**修复**: 在关键路径添加日志：
- `on_canvas_click` 被调用
- 验证 selected_piece
- 调用 `place_piece()`
- 处理成功/失败响应

### 问题 3: 视觉反馈缺失
**症状**: 没有预览效果或选中状态提示
**修复**: 实现 `placement_preview.py` 的集成

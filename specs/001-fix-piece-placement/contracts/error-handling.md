# Error Handling Contract

**Component**: 全局错误处理系统
**Date**: 2025-10-30

## Overview

定义 piece 放置过程中的错误处理、日志记录和用户反馈契约。

## 错误分类

### 1. UI 交互错误

#### 未选择 Piece
**错误类型**: `ui_interaction`
**触发条件**:
- 用户点击棋盘但没有选中 piece
- `PlacementHandler.selected_piece` 为 None

**用户反馈**:
```python
messagebox.showinfo("No Piece Selected", "Please select a piece first")
```

**日志记录**:
```json
{
  "event": "placement_attempted_without_selection",
  "error_type": "ui_interaction",
  "timestamp": "...",
  "user_action": "board_click"
}
```

#### 回调未设置
**错误类型**: `callback`
**触发条件**:
- `on_piece_selected` 回调未设置
- `on_placement_error` 回调未设置

**用户反馈**:
- 不显示对话框（避免重复错误）
- 记录严重错误日志

**日志记录**:
```json
{
  "event": "callback_not_set",
  "error_type": "callback",
  "severity": "high",
  "component": "PlacementHandler"
}
```

### 2. 验证错误

#### 规则验证失败
**错误类型**: `validation`
**触发条件**:
- `BlokusRules.validate_move()` 返回无效

**常见错误消息**:
1. **First Move Rule**
   ```
   "First piece must be placed in a corner of the board"
   ```

2. **Adjacency Rule**
   ```
   "Piece cannot be adjacent to your own pieces (边相邻不允许)"
   ```

3. **Bounds Rule**
   ```
   "Position is outside board bounds"
   ```

4. **Overlap Rule**
   ```
   "Position is already occupied by another piece"
   ```

5. **Fit Rule**
   ```
   "Piece does not fit at this position"
   ```

**用户反馈**:
```python
messagebox.showerror("Invalid Move", error_message)
```

**日志记录**:
```json
{
  "event": "placement_failed",
  "error_type": "validation",
  "rule_violated": "first_move_corner",
  "player_id": "P1",
  "piece_name": "I1",
  "position": {"row": 10, "col": 10},
  "error_message": "First piece must be placed in a corner",
  "validation_details": {...}
}
```

### 3. 系统错误

#### 异常未处理
**错误类型**: `system`
**触发条件**:
- `place_piece()` 中抛出未捕获的异常
- 状态更新失败
- 文件 I/O 错误

**用户反馈**:
```python
messagebox.showerror(
    "System Error",
    f"Failed to place piece: {str(e)}\n\n"
    "Please try again or restart the game."
)
```

**日志记录**:
```json
{
  "event": "placement_exception",
  "error_type": "system",
  "exception_type": "ValueError",
  "exception_message": "...",
  "stack_trace": "...",
  "player_id": "P1",
  "piece_name": "I1",
  "position": {"row": 10, "col": 10}
}
```

## 错误日志系统

### 日志格式

所有错误日志使用 JSON 格式，便于解析和分析。

**标准字段**:
```python
{
  "timestamp": "YYYY-MM-DDTHH:MM:SS.sssZ",
  "event": str,           # 事件类型
  "error_type": str,      # 错误分类
  "component": str,       # 发生错误的组件
  "player_id": str,       # 玩家 ID（如果有）
  "severity": str         # "low", "medium", "high", "critical"
}
```

**可选字段**:
```python
{
  "piece_name": str,      # 涉及的 piece
  "position": {...},      # 位置信息
  "error_code": str,      # 错误代码
  "error_message": str,   # 人类可读的错误消息
  "stack_trace": str,     # 完整的堆栈跟踪
  "game_state": {...},    # 当前游戏状态快照
  "user_action": str      # 触发错误的用户操作
}
```

### 日志存储

**位置**: `blokus_errors.log`
**格式**: JSON Lines（每行一个 JSON 对象）
**轮转**: 当文件超过 10MB 时创建新文件

### 错误处理接口

#### error_handler.py 接口

```python
class ErrorHandler:
    def log_error(self, event_type: str, **kwargs) -> None:
        """记录错误到日志文件"""

    def handle_ui_error(self, error_type: str, message: str) -> None:
        """处理 UI 相关错误，显示用户消息"""

    def handle_validation_error(self, rule: str, message: str) -> None:
        """处理验证错误，显示规则违规消息"""

    def handle_system_error(self, exception: Exception) -> None:
        """处理系统错误，记录异常信息"""
```

## 用户反馈契约

### 成功反馈

**成功放置 piece**:
```python
messagebox.showinfo(
    "Piece Placed",
    f"{piece_name} placed successfully! Turn passes to next player."
)
```

**延迟**: 立即显示
**自动关闭**: 用户点击"确定"后关闭

### 错误反馈

**验证失败**:
- 标题: "Invalid Move"
- 图标: 错误图标
- 消息: 详细的验证错误说明
- 延迟: 立即显示

**系统错误**:
- 标题: "System Error"
- 图标: 警告图标
- 消息: 技术错误 + "请重试或重启游戏"
- 延迟: 立即显示

**信息提示**:
- 标题: 根据上下文
- 图标: 信息图标
- 消息: 清晰的操作指导
- 延迟: 立即显示

### 日志反馈（调试模式）

当 `game_config.debug_mode = True` 时：
- 在 stderr 打印详细错误信息
- 包含完整的堆栈跟踪
- 显示游戏状态快照

## 测试契约

### 测试检查点

- [ ] 未选择 piece 点击棋盘 → 显示提示消息 + 记录日志
- [ ] 验证失败 → 显示具体错误消息 + 记录验证错误
- [ ] 系统异常 → 显示系统错误 + 记录异常堆栈
- [ ] 日志文件正确写入 JSON 格式
- [ ] 错误日志包含所有必要字段
- [ ] 重复错误不会导致程序崩溃
- [ ] 调试模式下显示详细错误信息

### 错误模拟测试

**未选择 piece**:
```python
def test_no_piece_selected():
    # 确保没有选中 piece
    placement_handler.clear_selection()
    # 点击棋盘
    success, error = board_click_handler.handle_click(10, 10)
    assert not success
    assert error == "No piece selected"
```

**验证失败**:
```python
def test_validation_failure():
    # 选择第一个 piece
    placement_handler.select_piece("I1")
    # 尝试在非法位置放置（中间位置）
    success, error = placement_handler.place_piece(10, 10)
    assert not success
    assert "corner" in error.lower()
```

**系统异常**:
```python
def test_system_exception():
    # 模拟异常（如损坏的 game_state）
    with patch.object(game_state, 'record_move', side_effect=IOError):
        success, error = placement_handler.place_piece(5, 5)
        assert not success
        assert "Failed to place piece" in error
```

## 修复计划

### 立即修复 (P0)
1. 在所有关键路径添加日志记录
2. 确保错误消息显示给用户
3. 防止异常未处理导致程序崩溃

### 短期改进 (P1)
1. 实现结构化错误日志（JSON 格式）
2. 添加错误统计分析
3. 实现自动错误报告（可选）

### 长期优化 (P2)
1. 实现错误恢复机制
2. 添加用户友好的错误解决建议
3. 集成外部错误跟踪系统（如 Sentry）

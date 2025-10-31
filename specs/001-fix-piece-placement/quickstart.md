# Quickstart Guide: Debugging Piece Placement Interaction Bug

**Date**: 2025-10-30
**Feature**: 001-fix-piece-placement
**Purpose**: 帮助开发者快速理解和修复 piece 选择 → 棋盘点击的交互 bug

## 问题描述

**症状**: 玩家选择 piece 后点击棋盘没有任何响应，也没有错误消息显示。

**影响**: 核心游戏机制无法使用，玩家无法进行游戏。

## 快速诊断（5 分钟）

### 步骤 1: 验证交互链路

在 `src/main.py` 中添加临时调试日志（位置约 587 行）：

```python
def _on_piece_selected(self, piece_name: str) -> None:
    print(f"[DEBUG] _on_piece_selected called with piece_name={piece_name}")  # 添加这行

    if not self.placement_handler:
        print("[DEBUG] placement_handler is None!")  # 添加这行
        return

    # Select the piece
    if self.placement_handler.select_piece(piece_name):
        print(f"[DEBUG] select_piece returned True, selected_piece={self.placement_handler.selected_piece}")  # 添加这行
        # Display the piece
        selected_piece = self.placement_handler.get_selected_piece()
        if selected_piece and self.piece_display:
            self.piece_display.set_piece(selected_piece)
    else:
        print(f"[DEBUG] select_piece returned False")  # 添加这行
```

在 `src/main.py` 中添加棋盘点击调试日志（位置约 499 行）：

```python
def on_canvas_click(event):
    print(f"[DEBUG] on_canvas_click called at ({event.x}, {event.y})")  # 添加这行

    if not self.placement_handler:
        print("[DEBUG] placement_handler is None!")  # 添加这行
        return

    if not self.placement_handler.selected_piece:
        print(f"[DEBUG] selected_piece is None! selected_piece={self.placement_handler.selected_piece}")  # 添加这行
        return

    # ... 其余代码保持不变
```

### 步骤 2: 运行测试

```bash
cd /root/blokus-step-by-step

# 运行 piece 放置相关的集成测试
pytest tests/integration/test_piece_placement.py -v

# 运行完整的放置流程测试
pytest tests/integration/test_complete_placement_flow.py -v
```

**期望结果**: 测试应该失败，显示交互链路的断点。

### 步骤 3: 运行游戏进行手动测试

```bash
cd /root/blokus-step-by-step/src
python main.py
```

**测试步骤**:
1. 设置游戏（2-4 名玩家）
2. 选择一个 piece
3. 尝试点击棋盘放置
4. 观察控制台输出

**预期输出**:
```
[DEBUG] _on_piece_selected called with piece_name=I1
[DEBUG] select_piece returned True, selected_piece=<Piece I1>
[DEBUG] on_canvas_click called at (150, 200)
[DEBUG] selected_piece=<Piece I1>
```

**如果看到错误**:
- 没有 `_on_piece_selected` 输出 → 回调未设置
- 没有 `on_canvas_click` 输出 → 事件绑定失败
- `selected_piece is None` → 状态传递失败

## 修复策略

### 修复 1: 确保回调正确设置

**问题**: `PieceSelector` 的 `on_piece_selected` 回调可能在错误时机设置。

**修复位置**: `src/main.py:223-227`

```python
# 确保 placement_handler 初始化时设置回调
self.placement_handler = PlacementHandler(
    self.game_state.board, self.game_state, current_player
)

# 在创建 PieceSelector 之前设置 callbacks
self._setup_callbacks()

# 然后创建 PieceSelector
if current_player:
    self.piece_selector = PieceSelector(
        middle_left_panel,
        current_player,
        on_piece_selected=self._on_piece_selected,
    )
```

### 修复 2: 同步玩家状态

**问题**: `PieceSelector` 可能持有过时的 player 引用。

**修复位置**: `src/main.py:256-267`

在玩家轮换时更新 `PieceSelector`：

```python
# 在 on_piece_placed 回调中添加：
if self.piece_selector and current_player:
    self.piece_selector.set_player(current_player)  # 添加这个方法调用
```

**需要实现的新方法**: 在 `PieceSelector` 类中添加：

```python
def set_player(self, new_player: Player) -> None:
    """更新 PieceSelector 的玩家引用。

    Args:
        new_player: 新的玩家对象
    """
    self.player = new_player
    self.refresh()  # 刷新 piece 列表
```

### 修复 3: 添加错误日志

**问题**: 失败时缺少调试信息。

**修复位置**: `src/game/placement_handler.py:43-70`

在 `select_piece` 方法中添加日志：

```python
def select_piece(self, piece_name: str) -> bool:
    print(f"[DEBUG] PlacementHandler.select_piece called with piece_name={piece_name}")  # 添加

    # Get the piece from player's inventory
    piece = self.current_player.get_piece(piece_name)
    if not piece:
        print(f"[DEBUG] Player does not have piece: {piece_name}")  # 添加
        if self.on_placement_error:
            self.on_placement_error(f"Player does not have piece: {piece_name}")
        return False

    if piece.is_placed:
        print(f"[DEBUG] Piece {piece_name} is already placed")  # 添加
        if self.on_placement_error:
            self.on_placement_error(f"Piece {piece_name} is already placed")
        return False

    # Create a new instance for this selection (to allow rotation/flip)
    self.selected_piece = Piece(piece_name)
    print(f"[DEBUG] selected_piece set to: {self.selected_piece.name}")  # 添加
    self.rotation_count = 0
    self.is_flipped = False

    return True
```

## 验证修复

### 自动化测试

```bash
# 运行所有相关测试
pytest tests/integration/test_piece_placement.py -v
pytest tests/integration/test_complete_placement_flow.py -v
pytest tests/integration/test_complete_setup_flow.py -v

# 运行单元测试
pytest tests/unit/test_player.py -v
pytest tests/contract/test_move_validation.py -v
```

**期望**: 所有测试通过。

### 手动测试

1. **选择 piece**:
   - 点击 piece 按钮
   - 验证按钮显示选中状态（pressed）
   - 控制台输出: `[DEBUG] _on_piece_selected called`

2. **点击棋盘**:
   - 在合法位置点击（角落位置放置第一个 piece）
   - 验证 piece 成功放置
   - 控制台输出: `[DEBUG] on_canvas_click called` 和成功消息

3. **错误处理**:
   - 尝试在非法位置放置
   - 验证显示错误消息
   - 验证错误日志记录

### 性能测试

根据规范中的 SC-001:
- 合法放置操作应该在 200 毫秒内完成

```python
import time

# 在 on_canvas_click 中添加性能测试
start_time = time.time()
success, error_msg = self.placement_handler.place_piece(board_row, board_col)
end_time = time.time()

elapsed_ms = (end_time - start_time) * 1000
print(f"[DEBUG] Placement took {elapsed_ms:.2f}ms")

if elapsed_ms > 200:
    print(f"[WARNING] Placement exceeded 200ms target: {elapsed_ms:.2f}ms")
```

## 实际修复摘要（已应用）

**修复日期**: 2025-10-30
**状态**: ✅ 已完成

### 核心修复

#### 1. 回调初始化顺序修复
**问题根源**: `_setup_callbacks()` 在 UI 组件创建前被调用，导致回调未正确设置

**修复位置**: `src/main.py:228-233`

**解决方案**:
```python
# 修复前：_setup_callbacks() → _show_game_ui()
# 修复后：_show_game_ui() → _setup_callbacks()

# 在 _setup_game_from_config 方法中
# 1. 先创建 UI（包含 PieceSelector）
self._show_game_ui()

# 2. 然后设置回调
if current_player:
    self._setup_callbacks()
```

#### 2. 添加 set_player() 方法
**问题**: PieceSelector 在玩家轮换时无法更新显示

**修复位置**: `src/ui/piece_selector.py:130-137`

**解决方案**:
```python
def set_player(self, new_player: Player) -> None:
    """Update the player reference and refresh the display."""
    self.player = new_player
    self.refresh()
```

**调用位置**: `src/main.py:269-270`
```python
if self.piece_selector and current_player:
    self.piece_selector.set_player(current_player)
```

#### 3. 增强视觉反馈
**新增功能**: Piece 选择和悬停的视觉反馈

**修复位置**:
- `src/ui/piece_selector.py:82-83, 116-128`
- `src/main.py:632-639`

**改进**:
- 添加悬停效果（mouse hover）
- 增强选中状态的视觉对比度
- 集成 PlacementPreview 组件

#### 4. 结构化错误日志
**新增功能**: JSON 格式的事件日志记录

**修复位置**:
- `src/game/error_handler.py:563-603` - 新增 `log_structured_event()` 方法
- `src/game/placement_handler.py:99-180` - 添加放置事件日志
- `src/main.py:616-625` - 添加选择事件日志

**日志类型**:
- `piece_selected` - piece 选择事件
- `placement_attempted` - 放置尝试
- `placement_succeeded` - 放置成功
- `placement_failed` - 放置失败

**日志格式**:
```json
{"timestamp": "2025-10-30T18:04:06.323153", "event_type": "piece_selected", "player_id": 1, "piece_name": "L4", "position": null, "error_message": null}
```

### 性能验证结果

**SC-001 要求**: 100% 有效放置 < 200ms

**测试结果**: ✅ 通过
- 平均放置时间: 0.65ms
- 最快: 0.64ms
- 最慢: 0.65ms
- 远低于 200ms 阈值

### 测试验证

**核心测试通过**:
- ✅ `test_complete_piece_placement_flow` - 完整放置流程
- ✅ `test_player_can_place_first_piece_in_corner` - 第一个 piece 放置
- ✅ `test_second_player_can_place_after_first` - 玩家轮换
- ✅ `test_invalid_piece_placement_is_rejected` - 验证逻辑

### 调试日志移除

已移除所有调试打印语句，生产代码现在使用结构化日志记录。

## 故障排除

### 问题: "No piece selected" 错误

**可能原因**:
1. `PieceSelector` 回调未设置
2. `PlacementHandler.selected_piece` 为 None
3. 玩家状态不同步

**解决方案**:
- 检查 `on_piece_selected` 是否被调用
- 检查 `placement_handler.select_piece()` 返回值
- 验证 `current_player` 是否正确

### 问题: 点击棋盘无响应

**可能原因**:
1. 事件绑定失败
2. `selected_piece` 检查过早返回
3. `place_piece()` 抛出异常但未捕获

**解决方案**:
- 验证 `<Canvas>.bind("<Button-1>", on_canvas_click)` 被调用
- 添加 try-except 捕获异常
- 添加详细日志

### 问题: 错误消息不显示

**可能原因**:
1. `on_placement_error` 回调未设置
2. `messagebox` 调用失败
3. 异常在回调设置前发生

**解决方案**:
- 验证 `_setup_callbacks()` 在创建 UI 之前调用
- 检查 `messagebox` 调用是否有异常
- 添加备用错误处理

## 预防措施

### 1. 添加结构化日志

修改 `src/game/error_handler.py`，实现 JSON 格式日志：

```python
import json
import logging
from datetime import datetime

class ErrorHandler:
    def __init__(self, log_file: str):
        self.log_file = log_file
        logging.basicConfig(
            filename=log_file,
            level=logging.DEBUG,
            format='%(message)s'
        )

    def log_interaction(self, event_type: str, **kwargs):
        """记录交互事件为 JSON"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event": event_type,
            **kwargs
        }
        logging.info(json.dumps(log_entry))

# 使用示例
error_handler = ErrorHandler("blokus_errors.log")
error_handler.log_interaction(
    "piece_selected",
    player_id="P1",
    piece_name="I1"
)
```

### 2. 添加断言检查

在关键位置添加断言：

```python
def _on_piece_selected(self, piece_name: str) -> None:
    assert self.placement_handler is not None, "placement_handler must be set"
    assert self.piece_display is not None, "piece_display must be set"

    print(f"[DEBUG] _on_piece_selected called with piece_name={piece_name}")
    # ... 其余代码
```

### 3. 单元测试覆盖

为交互逻辑添加单元测试：

```python
# tests/unit/test_piece_selection.py
def test_piece_selection_flow():
    # 模拟所有组件
    placement_handler = Mock(spec=PlacementHandler)
    piece_display = Mock(spec=PieceDisplay)

    # 模拟选择 piece
    placement_handler.select_piece.return_value = True

    # 验证流程
    app = BlokusApp()
    app.placement_handler = placement_handler
    app.piece_display = piece_display

    app._on_piece_selected("I1")

    placement_handler.select_piece.assert_called_once_with("I1")
    piece_display.set_piece.assert_called_once()
```

## 相关文件

### 核心文件
- `src/main.py` - 主应用逻辑，UI 事件处理
- `src/game/placement_handler.py` - Piece 放置协调器
- `src/ui/piece_selector.py` - Piece 选择 UI
- `src/models/player.py` - 玩家数据模型

### 测试文件
- `tests/integration/test_piece_placement.py` - 放置集成测试
- `tests/integration/test_complete_placement_flow.py` - 完整流程测试
- `tests/unit/test_player.py` - 玩家单元测试

### 文档文件
- `specs/001-fix-piece-placement/spec.md` - 需求规范
- `specs/001-fix-piece-placement/research.md` - 调试分析
- `specs/001-fix-piece-placement/contracts/` - API 契约

## 下一步

完成修复后，应该：
1. 提交所有修改到版本控制
2. 运行完整测试套件
3. 更新错误日志文档
4. 考虑添加视觉预览功能（FR-007）
5. 编写回归测试防止问题重现

## 支持

如需帮助，请检查：
1. `blokus_errors.log` - 错误日志文件
2. 控制台输出 - 调试日志
3. 测试结果 - 自动化验证

**紧急问题**: 如果游戏完全无法运行，检查 `src/main.py:40` 的错误处理设置。

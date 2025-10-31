# Data Model: Piece Placement Interaction

**Date**: 2025-10-30
**Feature**: 001-fix-piece-placement

## Overview

重用现有的数据模型，该模型已在 `src/models/` 中完全实现。本文档描述与 piece 放置交互相关的核心实体。

## 核心实体

### Piece
**定义**: 游戏中的棋子，具有特定形状和玩家归属
**位置**: `src/models/piece.py`
**关键属性**:
- `name`: str - piece 的唯一标识符（如 "I1", "L4", "T5"）
- `shape`: List[List[int]] - 2D 数组表示 piece 形状
- `size`: int - piece 包含的方格数量
- `is_placed`: bool - 是否已放置在棋盘上
- `position`: Optional[Tuple[int, int]] - 放置位置 (row, col)
- `owner_id`: str - 拥有该 piece 的玩家 ID

**关系**:
- 属于 Player
- 可以放置在 Board 上
- 通过 Placement 操作与 Board 关联

### Board
**定义**: 20x20 的游戏棋盘，包含放置的 pieces 和空格子
**位置**: `src/models/board.py`
**关键属性**:
- `size`: int = 20 - 棋盘大小
- `grid`: Dict[Tuple[int, int], str] - 位置到玩家 ID 的映射
  - 键: (row, col) 元组
  - 值: 占据该位置的玩家 ID 或 None
- `player_positions`: Dict[str, List[Tuple[int, int]]] - 每个玩家已放置的 positions

**关键方法**:
- `place_piece(piece, row, col, player_id)`: 将 piece 放置到指定位置
- `is_position_valid(row, col)`: 验证位置是否在棋盘范围内
- `is_position_empty(row, col)`: 检查位置是否为空

### Player
**定义**: 游戏玩家，拥有可放置的 pieces 集合
**位置**: `src/models/player.py`
**关键属性**:
- `player_id`: str - 玩家唯一标识符
- `name`: str - 玩家名称
- `pieces`: Dict[str, Piece] - 拥有的所有 pieces
- `pieces_remaining`: int - 剩余未放置的 piece 数量

**关键方法**:
- `get_unplaced_pieces()`: 获取所有未放置的 pieces
- `place_piece(piece_name, row, col)`: 标记 piece 为已放置
- `get_piece(piece_name)`: 根据名称获取 piece

### GameState
**定义**: 全局游戏状态，管理所有玩家和当前回合
**位置**: `src/models/game_state.py`
**关键属性**:
- `board`: Board - 游戏棋盘
- `players`: List[Player] - 所有玩家
- `current_player_index`: int - 当前玩家的索引
- `phase`: GamePhase - 当前游戏阶段
- `move_history`: List[Move] - 所有移动的历史记录

**关键方法**:
- `get_current_player()`: 获取当前回合的玩家
- `next_turn()`: 切换到下一个玩家
- `record_move(...)`: 记录一次移动

### Placement（操作实体）
**定义**: 将 piece 放置到特定位置的操作，包含验证和状态更新
**实现**: 通过 `PlacementHandler` 类实现 (`src/game/placement_handler.py`)
**关键状态**:
- `selected_piece`: Optional[Piece] - 当前选中的 piece
- `rotation_count`: int - 旋转次数（0-3）
- `is_flipped`: bool - 是否水平翻转

**关键操作**:
- `select_piece(piece_name)`: 选择一个 piece
- `place_piece(row, col)`: 尝试放置到位置
- `clear_selection()`: 清除选择

## 验证规则

### Blokus Rules (src/game/rules.py)
- **First Move Rule**: 第一个 piece 必须与棋盘角落相邻
- **Adjacency Rule**: piece 不能与同色 piece 边相邻
- **Bounds Rule**: piece 必须完全在棋盘范围内
- **Overlap Rule**: piece 不能与已存在的 piece 重叠

这些规则通过 `BlokusRules.validate_move()` 统一验证。

## 状态转换

### Piece 选择状态转换
```
Unselected → Selected → Placed
    ↑              ↓
    └──── Cleared ─┘
```

### 错误处理状态
```
Valid Placement → Success
      ↓
Invalid Placement → Error Message Displayed
      ↓
User Corrects → Retry Placement
```

## 数据一致性

### 同步点
1. **Piece 选择时**: PieceSelector ↔ PlacementHandler
2. **Piece 放置时**: PlacementHandler ↔ Board ↔ Player
3. **玩家轮换时**: GameState ↔ PieceSelector ↔ 所有 UI 组件

### 不变性
- Board.grid 中的每个位置最多有一个 piece
- Player.pieces 中的 piece 数量总和等于初始 21 个
- 所有已放置的 piece 必须在 Board 上有对应位置
- GameState.current_player 总是有效玩家

## 日志记录

### 错误日志结构（新增）
- `timestamp`: 时间戳
- `event`: 事件类型（"piece_selected", "placement_attempted", "placement_failed"）
- `player_id`: 玩家 ID
- `piece_name`: piece 名称
- `position`: 尝试的位置
- `error_type`: 错误类型（"validation", "state", "ui"）
- `error_message`: 详细错误信息

位置: `src/game/error_handler.py`（已存在，需要扩展）

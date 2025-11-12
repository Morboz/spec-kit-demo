# Integrate Game Mode Selection

## Summary

当前启动游戏时需要多个弹框确认，用户体验繁琐：
1. 首先弹出 "Play against AI?" 确认框
2. 选择AI模式后弹出模式选择器（Single AI/Three AI/Spectate） + 难度选择
3. 选择传统模式后弹出自定义配置对话框

本提案将所有模式选择整合到**单个统一对话框**中，用户可以在一个界面中选择所有游戏模式。

## Why

### User Experience Issues
当前的多次弹框流程存在以下问题：
- **效率低下**：每次启动需要2-3次确认，总共6-9次点击
- **打断感强**：每完成一个选择就弹出新框，用户思维被不断打断
- **选择困难**：无法在同一界面比较不同模式的优缺点
- **认知负担**：需要理解弹框之间的逻辑关系

### Business Impact
简化启动流程能够：
- 降低新用户学习成本
- 提高游戏启动转化率
- 提升整体用户体验满意度
- 符合现代游戏UI最佳实践

## Problem Statement

### 当前流程的问题
- **多个弹框**：每次启动游戏需要2-3次确认，用户体验差
- **打断流程**：每个弹框都需要用户交互，效率低
- **认知负担**：需要理解多个对话框之间的关系
- **选择困难**：分离的UI让模式对比困难

### 用户反馈
用户希望能够在**一个界面**中：
- 选择AI模式（Single AI / Three AI / Spectate）并设置难度
- 选择PvP模式（2-4人本地多人）
- 配置基本游戏设置（板子大小、颜色方案等）

## Proposed Solution

### 核心变更
创建**统一的游戏模式选择对话框**，包含：

1. **模式选择区域**
   - Single AI（人机对战）
   - Three AI（1人vs3AI）
   - Spectate（观战AI对战）
   - PvP Local（本地多人，2-4人）

2. **配置区域**（根据模式动态显示）
   - AI难度选择（AI模式）
   - 玩家数量（PvP模式）
   - 玩家姓名（PvP模式）
   - 板子大小、颜色方案等通用设置

3. **优势**
   - 只需**一次点击**即可启动游戏
   - 所有选项一目了然
   - 减少UI弹框数量
   - 更符合现代游戏UI设计

## What Changes

### 新增组件
- **UnifiedGameModeSelector** (`src/blokus_game/ui/unified_game_mode_selector.py`)
  - 统一模式选择对话框
  - 支持4种游戏模式选择
  - 动态配置UI
  - 表单验证

### 修改组件
- **GameMode** (`src/blokus_game/models/game_mode.py`)
  - 添加 PVP_LOCAL 模式类型
  - 添加 pvp_local() 工厂方法
  - 更新验证逻辑

- **GameSetupManager** (`src/blokus_game/managers/game_setup_manager.py`)
  - 替换多弹框流程为单对话框
  - 处理 PvP 模式配置

### 流程变化
- **之前**：确认框 → AI模式选择器 → 自定义配置对话框
- **之后**：统一模式选择对话框（包含所有选项）

## Impact

### User Experience
- ✅ 启动游戏只需点击1次（减少66-75%交互）
- ✅ 统一界面，操作更直观
- ✅ 减少弹框打断

### Technical Changes
- ✏️ 新增 UnifiedGameModeSelector 类
- ✏️ 修改 GameSetupManager 逻辑
- ✏️ 更新 GameMode 数据模型支持 PvP
- ✏️ 更新 main.py 启动流程

### Backward Compatibility
- ✅ 保持所有现有功能
- ✅ Command line 参数（--spectate）不变
- ✅ 保存的设置偏好保持不变

## Validation

### Test Scenarios
1. **Single AI模式**：选择并确认难度设置
2. **Three AI模式**：验证多AI配置
3. **Spectate模式**：验证无需难度设置
4. **PvP模式**：验证2-4人配置界面
5. **通用设置**：验证板子大小、颜色方案
6. **CLI兼容**：验证--spectate参数仍然工作

### Acceptance Criteria
- [ ] 启动游戏只显示一个模式选择对话框
- [ ] 所有现有模式（AI + PvP）均可通过新界面访问
- [ ] 难度、玩家数量等配置正确应用
- [ ] CLI参数兼容性保持不变
- [ ] 所有单元测试和集成测试通过

## References

- Current code: `src/blokus_game/main.py`, `src/blokus_game/ui/game_mode_selector.py`, `src/blokus_game/managers/game_setup_manager.py`
- UI reference: `src/blokus_game/ui/restart_button.py` (GameRestartDialog)

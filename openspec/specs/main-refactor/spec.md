# Main Application Refactor Specification

## Purpose
重构main.py，将单体类拆分为协调者模式，使用专门的管理器类来处理不同的职责，提升可维护性和可测试性。

## What Changes
- 将main.py从1219行减少到245行（减少80%）
- 创建5个专门的管理器类：
  - GameSetupManager: 游戏设置和配置
  - AIManager: AI相关逻辑
  - UIManager: UI管理
  - GameFlowManager: 游戏流程控制
  - EventHandlerManager: 事件处理
- BlokusApp改为协调者模式，专注于组件协调

## Why
原始的main.py是一个庞大的单体类，包含27个方法，存在以下问题：
1. 可维护性差 - 单一文件承担过多职责
2. 难以测试 - 难以进行单元测试
3. 认知负担重 - 开发者需要理解整个类的复杂交互
4. 扩展性限制 - 新功能需要修改庞大且复杂的类

## Requirements
### Requirement: 主应用类职责简化
BlokusApp类 SHALL只负责应用初始化和生命周期管理，将具体功能委托给专门的管理器组件。BlokusApp SHALL保持所有现有公共API接口不变，确保向后兼容性。

#### Scenario: 应用启动
**WHEN** 用户启动Blokus游戏
**THEN** BlokusApp初始化并显示游戏设置对话框

#### Scenario: 传统多人游戏设置
**WHEN** 用户选择传统多人游戏并完成配置
**THEN** BlokusApp通过GameSetupManager创建游戏状态并显示游戏UI

#### Scenario: AI游戏设置
**WHEN** 用户选择AI游戏模式并完成配置
**THEN** BlokusApp通过GameSetupManager和AIManager创建游戏状态并显示游戏UI

#### Scenario: 游戏结束
**WHEN** 游戏达到结束条件
**THEN** BlokusApp通过GameFlowManager显示游戏结果并处理重新开始

### Requirement: 游戏设置管理器 (GameSetupManager)
系统 SHALL提供GameSetupManager类负责游戏初始化和配置。该类 SHALL封装所有游戏设置逻辑，包括预设选择、自定义配置、AI游戏模式设置。

#### Scenario: 选择游戏预设
**WHEN** 用户在设置界面选择预设（casual、tournament、high_contrast）
**THEN** GameSetupManager应用相应配置并继续游戏设置

#### Scenario: 自定义游戏配置
**WHEN** 用户选择自定义配置并输入玩家信息
**THEN** GameSetupManager验证配置并创建游戏状态

#### Scenario: AI游戏模式配置
**WHEN** 用户选择AI游戏模式（单AI、三AI、观战）
**THEN** GameSetupManager创建相应的AI玩家和策略配置

### Requirement: AI管理器 (AIManager)
系统 SHALL提供AIManager类负责所有AI相关逻辑。该类 SHALL封装AI玩家创建、策略分配、回调设置、AI行动计算和执行。

#### Scenario: AI玩家创建
**WHEN** 设置AI游戏模式时
**THEN** AIManager根据难度创建相应的AI策略（Random、Corner、Strategic）

#### Scenario: AI回合执行
**WHEN** 轮到AI玩家回合
**THEN** AIManager计算最优移动并执行，返回成功或失败状态

#### Scenario: AI错误处理
**WHEN** AI计算过程中发生错误
**THEN** AIManager优雅处理错误，记录日志并跳过回合

### Requirement: UI管理器 (UIManager)
系统 SHALL提供UIManager类负责所有UI相关逻辑。该类 SHALL封装窗口创建、组件初始化、事件绑定、渲染逻辑。

#### Scenario: 游戏UI创建
**WHEN** 游戏状态创建完成后
**THEN** UIManager创建完整的游戏界面，包括棋盘、选择器、计分板等

#### Scenario: 棋盘渲染
**WHEN** 需要更新游戏状态显示
**THEN** UIManager调用OptimizedBoardRenderer更新棋盘显示

#### Scenario: 键盘快捷键处理
**WHEN** 用户按下快捷键（Ctrl+N、Ctrl+Q、F1等）
**THEN** UIManager的GameKeyboardHandler处理相应操作

### Requirement: 游戏流程管理器 (GameFlowManager)
系统 SHALL提供GameFlowManager类负责游戏进程控制。该类 SHALL封装回合管理、游戏结束判断、得分计算、结果展示。

#### Scenario: 回合切换
**WHEN** 玩家完成放置或跳过回合
**THEN** GameFlowManager更新当前玩家并检查游戏是否结束

#### Scenario: 游戏结束
**WHEN** 游戏满足结束条件（所有玩家都已跳过或无有效移动）
**THEN** GameFlowManager计算最终得分并显示结果对话框

#### Scenario: 重新开始游戏
**WHEN** 用户点击"新游戏"或选择"再来一局"
**THEN** GameFlowManager重置游戏状态并返回设置界面

### Requirement: 事件处理器管理器 (EventHandlerManager)
系统 SHALL提供EventHandlerManager类负责玩家交互事件。该类 SHALL封装棋子选择、旋转翻转操作、放置验证和反馈。

#### Scenario: 棋子选择
**WHEN** 玩家在选择器中点击棋子
**THEN** EventHandlerManager选择棋子、更新显示并激活放置预览

#### Scenario: 棋子旋转/翻转
**WHEN** 玩家使用按钮或快捷键旋转/翻转选中的棋子
**THEN** EventHandlerManager应用变换并更新预览显示

#### Scenario: 棋子放置
**WHEN** 玩家在棋盘上点击放置选中的棋子
**THEN** EventHandlerManager验证放置、更新游戏状态并通知UI更新

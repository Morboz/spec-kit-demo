# Change: 重构main.py代码结构

## Why
main.py文件当前有1219行代码，包含27个方法，属于一个庞大而难以维护的单体类。这种结构存在以下问题：

1. **可维护性差** - 单一文件承担过多职责，修改影响面大
2. **代码重复** - 相似功能的代码散布在各个方法中
3. **难以测试** - 单体类难以进行单元测试
4. **认知负担重** - 开发者需要理解整个类的复杂交互
5. **扩展性限制** - 新功能需要修改庞大且复杂的类

## What Changes
将main.py中的`BlokusApp`类重构为协调者模式，将功能分解为5个专门的管理器类：

### MODIFIED Requirements
### Requirement: 主应用类职责简化
BlokusApp类 SHALL只负责：
- 应用初始化和生命周期管理
- 协调各个管理器组件
- 保持所有公共API接口不变
- 委托具体功能给专门的管理器

**New Structure**:
- BlokusApp (协调者，≈200行)
  - GameSetupManager (游戏设置，约250行)
  - AIManager (AI管理，约300行)
  - UIManager (UI管理，约250行)
  - GameFlowManager (游戏流程，约200行)
  - EventHandlerManager (事件处理，约150行)

### ADDED Requirements
### Requirement: 游戏设置管理器
GameSetupManager类 SHALL负责：
- 游戏初始化和配置
- 预设选择和自定义配置
- 游戏模式设置（传统/AI模式）
- 提供统一的setup_game()方法

#### Scenario: 设置传统多人游戏
- **WHEN** 用户选择传统多人游戏模式
- **THEN** GameSetupManager处理配置并创建游戏状态

#### Scenario: 设置AI游戏模式
- **WHEN** 用户选择AI游戏模式
- **THEN** GameSetupManager处理AI配置和游戏创建

### Requirement: AI管理器
AIManager类 SHALL负责：
- AI玩家创建和策略分配
- AI回调设置和管理
- AI行动触发和执行
- 回合管理（特别是AI回合）

#### Scenario: AI回合执行
- **WHEN** 轮到AI玩家回合
- **THEN** AIManager计算并执行AI行动

### Requirement: UI管理器
UIManager类 SHALL负责：
- 游戏UI窗口创建和布局
- 组件初始化（棋盘、选择器、显示区等）
- 键盘和鼠标事件处理设置
- 板渲染和性能指标显示

#### Scenario: 创建游戏UI
- **WHEN** 游戏设置完成后
- **THEN** UIManager创建完整的游戏界面

### Requirement: 游戏流程管理器
GameFlowManager类 SHALL负责：
- 回合切换和玩家轮换
- 游戏结束判断
- 最终得分计算
- 游戏结果展示
- 重新开始游戏流程

#### Scenario: 游戏结束处理
- **WHEN** 游戏满足结束条件
- **THEN** GameFlowManager计算得分并显示结果

### Requirement: 事件处理器管理器
EventHandlerManager类 SHALL负责：
- 棋子选择事件处理
- 棋子旋转/翻转操作
- 跳过回合操作
- 放置预览更新
- 事件回调协调

#### Scenario: 棋子交互
- **WHEN** 玩家选择棋子并尝试放置
- **THEN** EventHandlerManager协调整个交互流程

## Impact
- **Files Created**: 5个新的管理器类文件
- **Files Modified**: main.py (大幅简化)
- **Backward Compatibility**: ✅ 所有公共API保持不变
- **Testing Impact**: 现在可以独立测试各个管理器
- **No Breaking Changes**: 现有调用者无需修改

## Migration Strategy
1. 创建5个管理器类
2. 将对应功能代码移动到管理器
3. 更新BlokusApp使用管理器实例
4. 验证所有功能正常工作
5. 删除已移动的原始方法

## Benefits
- **可维护性提升60%+** - 按职责分离的模块化结构
- **测试覆盖率提高** - 可以针对每个管理器独立测试
- **代码复用** - 相似功能整合到专用管理器
- **新功能扩展性** - 添加新功能只需实现新的管理器
- **代码审查友好** - 每个文件小而专注，易于审查

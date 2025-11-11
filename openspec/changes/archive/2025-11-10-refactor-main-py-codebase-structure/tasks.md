# Tasks: 重构main.py代码结构

## 1. 准备工作
- [ ] 1.1 分析main.py现有方法的功能分组
- [ ] 1.2 验证现有测试覆盖范围
- [ ] 1.3 创建备份分支以确保回滚能力

## 2. 创建GameSetupManager类 (游戏设置管理器)
- [ ] 2.1 在`src/blokus_game/managers/`目录创建`__init__.py`
- [ ] 2.2 创建`game_setup_manager.py`文件
- [ ] 2.3 实现_choose_preset()逻辑
- [ ] 2.4 实现_select_preset()逻辑
- [ ] 2.5 实现_setup_game_from_config()逻辑
- [ ] 2.6 实现_setup_ai_game()逻辑
- [ ] 2.7 创建公共方法initialize_game()供BlokusApp调用
- [ ] 2.8 编写单元测试

## 3. 创建AIManager类 (AI管理器)
- [ ] 3.1 创建`ai_manager.py`文件
- [ ] 3.3 实现_convert_board_to_2d_array()方法
- [ ] 3.4 实现_setup_ai_callbacks()逻辑
- [ ] 3.5 实现_trigger_ai_move()逻辑
- [ ] 3.6 实现_pass_turn()逻辑
- [ ] 3.7 创建公共方法handle_ai_turn()供UIManager调用
- [ ] 3.8 编写单元测试

## 4. 创建UIManager类 (UI管理器)
- [ ] 4.1 创建`ui_manager.py`文件
- [ ] 4.2 实现_setup_keyboard_handler()逻辑
- [ ] 4.3 实现_show_game_ui()主逻辑
- [ ] 4.4 实现_render_board()方法
- [ ] 4.5 实现_setup_board_click_handling()逻辑
- [ ] 4.6 实现_show_help()方法
- [ ] 4.7 实现_show_performance_metrics()方法
- [ ] 4.8 实现_quit_game()方法
- [ ] 4.9 创建公共方法initialize_ui()供BlokusApp调用
- [ ] 4.10 编写单元测试

## 5. 创建GameFlowManager类 (游戏流程管理器)
- [ ] 5.1 创建`game_flow_manager.py`文件
- [ ] 5.2 实现_on_skip_turn_clicked()逻辑
- [ ] 5.3 实现_setup_callbacks()逻辑
- [ ] 5.4 实现_end_game()逻辑
- [ ] 5.5 实现_show_game_results()逻辑
- [ ] 5.6 实现_on_restart_game()逻辑
- [ ] 5.7 创建公共方法advance_turn()、end_game()供其他管理器调用
- [ ] 5.8 编写单元测试

## 6. 创建EventHandlerManager类 (事件处理器管理器)
- [ ] 6.1 创建`event_handler_manager.py`文件
- [ ] 6.2 实现_on_piece_selected()逻辑
- [ ] 6.3 实现_on_rotate_piece()逻辑
- [ ] 6.4 实现_on_flip_piece()逻辑
- [ ] 6.5 实现_update_placement_preview()逻辑
- [ ] 6.6 创建公共方法handle_piece_interaction()供UI调用
- [ ] 6.7 编写单元测试

## 7. 重构BlokusApp主类
- [ ] 7.1 在BlokusApp.__init__()中实例化所有管理器
- [ ] 7.2 更新_show_setup()方法使用GameSetupManager
- [ ] 7.3 更新_show_game_ui()方法使用UIManager
- [ ] 7.4 简化run()方法，专注于生命周期管理
- [ ] 7.5 移除已移动到管理器的方法定义
- [ ] 7.6 验证所有公共API保持不变
- [ ] 7.7 更新类型提示和文档字符串

## 8. 集成测试和验证
- [ ] 8.1 运行所有单元测试确保功能正常
- [ ] 8.2 手动测试传统多人游戏模式
- [ ] 8.3 手动测试AI游戏模式
- [ ] 8.4 手动测试AI观战模式
- [ ] 8.5 验证所有键盘快捷键正常工作
- [ ] 8.6 验证所有UI交互正常
- [ ] 8.7 验证游戏结束流程正常

## 9. 代码质量保证
- [ ] 9.1 运行`uv run ruff check .`检查代码规范
- [ ] 9.2 运行`uv run black .`格式化代码
- [ ] 9.3 运行`uv run mypy .`检查类型提示
- [ ] 9.4 运行`pre-commit run --all-files`执行所有钩子
- [ ] 9.5 确保测试覆盖率没有下降

## 10. 文档和总结
- [ ] 10.1 更新主类文档字符串
- [ ] 10.2 添加架构图到docs/目录
- [ ] 10.3 创建迁移指南文档
- [ ] 10.4 提交变更并创建Pull Request

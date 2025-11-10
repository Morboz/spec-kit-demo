# Logger System Unification Proposal

## Change ID
unify-logger-system

## Summary
统一整个项目中的logger编写，制定统一的日志格式和级别规范，将所有print语句替换为统一的logger输出。

## Current State Analysis
- 项目中有13个文件包含print语句
- 只有2个文件使用logging模块（ai_player.py, error_handler.py）
- 现有logger配置不统一：
  - ai_player.py: 级别为DEBUG，格式为时间戳-名称-级别-消息
  - error_handler.py: 混用print和logging
- 缺乏统一的logger配置中心

## Target State
1. 统一的logger配置模块
2. 所有print语句被相应的logger调用替换
3. 标准化的日志级别和格式
4. 便于维护和调试的日志输出

## Changes Required
- 创建统一logger配置模块
- 替换所有print语句为logger调用
- 建立日志级别规范
- 验证日志系统正常工作

## Dependencies
- None (all within codebase)

## Risks
- 替换过程中可能遗漏某些print语句
- 测试输出可能需要调整
- 现有logger配置需要兼容性检查

## Benefits
- 统一的日志格式便于调试
- 可以动态控制日志级别
- 更专业的日志记录
- 便于添加日志过滤和重定向

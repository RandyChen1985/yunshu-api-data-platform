# Git 工作流程指南

## 标准Git工作流程

### 1. 创建功能分支
```bash
# 从main分支创建新的功能分支
git checkout main
git pull origin main  # 确保本地main是最新的
git checkout -b feature/新功能名称

# 分支命名规范：
# feature/功能描述 - 新功能开发
# bugfix/问题描述 - bug修复
# hotfix/紧急修复 - 紧急修复
# refactor/重构内容 - 代码重构
```

### 2. 开发和提交
```bash
# 进行代码修改...

# 查看修改状态
git status

# 添加修改的文件
git add .                    # 添加所有修改
git add 文件名               # 添加特定文件

# 提交修改（使用中文备注）
git commit -m "feat: 添加新功能描述"
git commit -m "fix: 修复某个问题"
git commit -m "refactor: 重构某个模块"

# 提交信息规范：
# feat: 新功能
# fix: 修复bug
# docs: 文档更新
# style: 代码格式调整
# refactor: 重构
# test: 测试相关
# chore: 构建过程或辅助工具的变动
```

### 3. 推送功能分支
```bash
# 首次推送新分支
git push origin feature/新功能名称

# 后续推送
git push
```

### 4. 创建Pull Request (PR)
1. 访问GitLab/GitHub创建PR页面
2. 选择源分支：`feature/新功能名称`
3. 选择目标分支：`main`
4. 填写PR信息：
   - **标题**：简短描述修改内容
   - **描述**：
     - 修改原因和背景
     - 主要改动点
     - 测试情况
     - 相关issue链接

### 5. 代码审查和合并
- 等待团队成员审查代码
- 根据反馈修改代码
- 通过PR界面合并到main分支
- 或由maintainer进行合并

### 6. 清理工作
```bash
# 切换回main分支
git checkout main

# 更新本地main分支
git pull origin main

# 删除已合并的功能分支
git branch -d feature/新功能名称

# 删除远程分支（可选）
git push origin --delete feature/新功能名称
```

## 分支管理策略

### 主要分支
- `main`: 主分支，始终保持稳定可发布状态
- `develop`: 开发分支（可选），集成最新功能

### 辅助分支
- `feature/*`: 功能开发分支
- `bugfix/*`: bug修复分支
- `hotfix/*`: 紧急修复分支
- `refactor/*`: 重构分支

## 常用Git命令

### 查看状态
```bash
git status                    # 查看工作区状态
git log --oneline -10         # 查看最近10次提交
git branch -a                 # 查看所有分支
git diff                      # 查看未暂存的修改
git diff --staged             # 查看已暂存的修改
```

### 撤销操作
```bash
git checkout -- 文件名        # 撤销工作区修改
git reset HEAD 文件名         # 取消暂存
git commit --amend            # 修改最后一次提交
git reset --soft HEAD~1       # 撤销最后一次提交（保留修改）
git reset --hard HEAD~1       # 撤销最后一次提交（丢弃修改）
```

### 合并和变基
```bash
git merge feature/分支名       # 合并分支
git rebase main               # 变基到main
git cherry-pick 提交hash      # 挑选特定提交
```

## 最佳实践

### 1. 提交规范
- 每个提交应该是一个逻辑完整的修改
- 提交信息要清晰描述修改内容
- 使用中文备注，便于团队理解

### 2. 分支管理
- 不要直接在main分支上开发
- 功能分支要及时同步main分支的更新
- 完成功能后及时清理分支

### 3. 代码审查
- 所有代码都要经过PR审查
- 及时响应审查意见
- 确保代码质量后再合并

### 4. 冲突处理
```bash
# 同步main分支更新
git checkout main
git pull origin main
git checkout feature/分支名
git rebase main

# 解决冲突后
git add .
git rebase --continue
```

## 紧急情况处理

### 紧急修复流程
```bash
# 从main创建hotfix分支
git checkout main
git pull origin main
git checkout -b hotfix/紧急修复

# 修复并提交
git add .
git commit -m "hotfix: 紧急修复问题描述"

# 直接合并到main（跳过PR）
git checkout main
git merge hotfix/紧急修复
git push origin main

# 同时合并到develop（如果存在）
git checkout develop
git merge hotfix/紧急修复
git push origin develop
```

## 工具推荐

### GUI工具
- GitKraken
- SourceTree
- VS Code Git插件

### 命令行增强
- Oh My Zsh Git插件
- Git aliases配置

---

记住：好的Git习惯是团队协作的基础！

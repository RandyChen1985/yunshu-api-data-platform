---
name: dev-skills
description: 用户专属开发技能，包含中文沟通规范、代码提交流程及自动化构建部署指令。
---

# Dev Skills

此技能定义了用户偏好的开发流程和规范。请在所有任务中严格遵守以下规则。

## 1. 沟通与文档 (Communication & Documentation)

- **核心原则**：始终使用 **中文 (Chinese)** 与用户交流，无论是在对话中还是在生成的文档中。
- **OpenSpec 与需求文档**：
  - 创建或更新 OpenSpec 需求文件（如 `proposal.md`, `design.md` 等）时，必须使用 **中文**。
  - `task.md` 和 `implementation_plan.md` 等工件也必须使用中文编写。

## 2. 计划与原理解释 (Planning & Rationale)

在进行任何功能开发或 Bug 修复 **之前**，必须先制定明确的计划并向用户解释原因。

- **创建/更新 Implementation Plan**：
  - 使用 `implementation_plan.md` 详细列出修改计划。
  - **核心内容必须包含**：
    1.  **为什么这么做 (Why)**：解释修改的动机、根本原因 (Root Cause) 或设计思路。让用户明白“为什么”是必须的。
    2.  **准备怎么搞 (How)**：详细的修改步骤、涉及的文件以及预期的效果。
    3.  **为什么这么修改 (Rationale)**：针对具体的代码变动，解释为什么选择这种实现方式（而非其他方式）。
- **确认先行**：
  - 在开始写代码 (Coding) 之前，必须先让用户阅读并确认这份计划。

## 3. 代码提交规范 (Git Workflow)

- **语言要求**：Git Commit Message 必须使用 **中文**。
- **格式规范**：遵守 Conventional Commits 规范。
  - `feat: ...` (新功能)
  - `fix: ...` (修复)
  - `docs: ...` (文档)
  - `refactor: ...` (重构)
- **确认机制**：
  - **严禁自动提交**：在执行 `git commit` 前，必须先询问用户。
  - **流程**：
    1. `git add <files>`
    2. 告知用户准备提交的文件，并提供拟定的 Commit Message。
    3. 获取用户明确确认（"可以提交"、"confirm" 等）。
    4. 执行 `git commit`。

## 4. 全量编译与重启流程 (Full Compilation & Restart Workflow)

当用户要求“全量编译”、“重启”或“查看效果”时，必须严格按照以下 **5 个独立阶段** 执行。

**核心准则：必须一步一步来。前一个步骤没有彻底结束并确认成功前，绝对严禁启动下一个步骤。禁止使用长命令串联所有步骤。**

### 流程步骤：

1.  **阶段 1：清理 (Cleanup)**
    - **指令**：`echo "🧹 Step 1: Cleaning..." && rm -rf frontend/dist app.log && echo "✅ Cleanup complete."`
    - **要求**：物理删除完成后方可继续。

2.  **阶段 2：编译 (Compilation)**
    - **要求**：**必须完整展示 NPM/Vite 编译过程日志**。必须等待编译进程完全退出。
    - **指令**：`echo "🏗️  Step 2: Compiling Frontend..." && cd frontend && npm run build`

3.  **阶段 3：停止进程 (Stop Process)**
    - **要求**：必须显式输出被杀死的进程 ID (PID)，确认端口已释放。
    - **指令**：
      ```bash
      echo "🛑 Step 3: Stopping old service..."
      pid=$(lsof -t -i:8000)
      if [ -n "$pid" ]; then
        kill -9 $pid
        echo "✅ Killed process $pid"
      else
        echo "ℹ️  No process found on port 8000"
      fi
      ```

4.  **阶段 4：启动新进程 (Start Process)**
    - **指令**：`echo "🚀 Step 4: Starting new service..." && source venv/bin/activate && nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > app.log 2>&1 &`

5.  **阶段 5：验证与展示日志 (Verify & Show Logs)**
    - **要求**：等待服务初始化，并立即将启动日志打印到前台。
    - **指令**：`echo "⏳ Step 5: Waiting for service to start..." && sleep 5 && echo "📜 Startup Logs:" && cat app.log`

### 核心原则：
- **顺序执行**：每一阶段必须作为独立的 `run_shell_command` 调用，确保逻辑解耦。
- **透明性**：所有输出必须直接显示在终端，不得静默。
- **自动流转**：虽然步骤分开执行，但应连续触发，无需每步停顿询问。


## 5. 代码推送与 PR 流程 (Push & PR Workflow)

当用户要求“提交代码并发布”、“Push”或“创建 PR”时，遵循以下流程：

1.  **检查与切换分支 (Branching)**：
    - **检查**：使用 `git branch --show-current` 检查当前分支。
    - **策略**：
      - 如果还在主分支 (`main`, `master`) 或之前的旧分支，且当前是一个新的任务，**必须** 根据任务内容（Feature/Fix）生成一个新的分支名（例如 `feat/user-login`, `fix/api-timeout`）。
      - 使用 `git checkout -b <new_branch>` 切换到新分支。
    - *输出提示：已基于修改内容切换到新分支 [branch_name]...*

2.  **推送到远程 (Pushing)**：
    - 执行 `git push -u origin <branch_name>`。
    - *输出提示：正在推送到远程仓库...*

3.  **创建 Pull Request (Automated PR)**：
    - **内容生成**：根据分支的 Commits 和修改差异，自动生成一份完整的 PR 标题和详细描述（Markdown 格式），包含：
        - **标题**：清晰明了（如 `feat: 实现用户登录功能`）。
        - **变更内容**：列出主要修改点。
        - **测试情况**：说明已进行的测试。
    - **执行创建**：
        - 尝试使用 GitHub CLI: `gh pr create --title "..." --body "..."`。
        - 如果工具不可用，则将“标题”和“描述”打印在对话框中，并提供手动创建的链接提示。
    - *输出提示：正在创建 Pull Request...*

## 7. 前端交互规范 (Frontend UX)

- **禁止原生弹窗**：严禁在生产代码中使用浏览器原生的 `alert()`, `confirm()`, `prompt()`。
  - **替代方案**：必须使用项目封装好的 UI 组件（如 `Toast`, `ConfirmDialog`, `Modal`）。
  - **例外**：仅在极早期的快速原型验证（Prototype）阶段允许临时使用，正式提交前必须替换。

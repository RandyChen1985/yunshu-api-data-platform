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

当用户要求“全量编译”、“重启”或“查看效果”时，必须严格遵循以下 **5 个独立阶段**。

**核心准则：必须一步一步来。前一个步骤没有彻底结束并确认成功前，绝对严禁启动下一个步骤。**

### 流程步骤：

1.  **阶段 1：清理 (Cleanup)**
    - **动作**：物理删除 `frontend/dist` 目录和 `app.log`。
    - **指令**：`echo "🧹 Step 1: Cleaning..." && rm -rf frontend/dist app.log && echo "✅ Cleanup complete."`
    - **要求**：确认文件已删除后方可进行下一步。

2.  **阶段 2：编译 (Compilation)**
    - **动作**：进入 `frontend` 目录执行生产构建。
    - **要求**：**必须完整展示所有编译日志**。只有在编译进程完全退出（Exit Code 0）后，才允许进行下一步。
    - **指令**：`echo "🏗️  Step 2: Compiling Frontend..." && cd frontend && npm run build`

3.  **阶段 3：停止进程 (Stop Service)**
    - **动作**：查找并强制结束占用 `8000` 端口的后端进程。
    - **要求**：必须确认端口已释放。
    - **指令**：`echo "🛑 Step 3: Stopping old service..." && pid=$(lsof -t -i:8000) && if [ -n "$pid" ]; then kill -9 $pid && echo "✅ Killed process $pid"; else echo "ℹ️  No process on port 8000"; fi`

4.  **阶段 4：启动新进程 (Start Service)**
    - **动作**：使用虚拟环境启动后端服务。
    - **指令**：`echo "🚀 Step 4: Starting new service..." && source venv/bin/activate && nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > app.log 2>&1 &`

5.  **阶段 5：验证与展示 (Verify & Show Logs)**
    - **动作**：等待服务初始化，并在前台展示启动日志。
    - **要求**：必须看到 "Application startup complete" 或类似成功标志。
    - **指令**：`echo "⏳ Step 5: Waiting for logs..." && sleep 5 && echo "📜 Startup Logs:" && cat app.log`

### 核心原则：
- **顺序执行**：禁止使用 `&&` 将所有大步骤连成一个长命令。必须分多次 `run_shell_command` 调用，确保每一步的输出都清晰可辨。
- **透明展示**：用户必须能实时看到每一阶段的状态。
- **严禁静默**：禁止隐藏任何构建或启动日志。

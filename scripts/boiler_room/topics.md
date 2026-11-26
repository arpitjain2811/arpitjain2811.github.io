# Boiler Room topic watchlist

Read before researching; update at the end of every run (see RUNBOOK.md, step 7). This list is how
coverage evolves: new agentic systems and ideas come in, faded ones go out.

Last updated: 2026-11-25 (No. 004)

## Core themes (always in scope)
- Software factories: agents carrying work from ticket to verified PR, human gates, adoption
- Harness engineering: agents files, skills, hooks, sandboxes, guides and sensors
- Verification and code review for agent-written code: review agents, proof artifacts, merge-risk scoring
- Loop engineering and long-running agents: goals, checkpoints, background and always-on agents
  (promoted the always-on "teammate" entry after No. 001–003)
- AI-first team structures and roles: team size, reviewer load, hiring, measuring productivity
- Agent security and identity: sandboxes, permissions, prompt injection, OAuth, delegated user
  identity and per-agent IDs with a named owner (promoted the identity entry after No. 001–003)
- Model choice and portability: private evals, pricing, multi-model harnesses

## Systems to track (coding agents and agent apps)
- Claude Code, Claude apps and Claude Managed Agents (Anthropic)
- Codex and ChatGPT agent features (OpenAI)
- Cursor (now part of SpaceX)
- Devin (Cognition)
- Gemini Enterprise, Gemini apps, Antigravity and Stitch Loop (Google)
- GitHub Copilot and Microsoft Copilot (Autopilot, Cowork)
- Perplexity Computer and Teammates
- Warp, Augment, Factory, Mastra and other software-factory platforms

## Emerging (watch; promote to core once covered in 3+ editions)
- Code Mode: agents writing code to call their own tools (Codex host connections, No. 004)
- Self-hosted agent runtimes inside the enterprise perimeter
- Manager agents that plan and supervise other agents (planner/executor pairs; Devin Bots No. 002,
  Perplexity Multiagent's lead agent over up to 16 agents No. 004)
- Agent cost metering: per-agent budgets, spend dashboards, user-paid billing
- Computer use on the desktop: agents driving local apps behind app allow lists, background
  windows and per-action approval (No. 003)
- Tool gateways and credential proxies that keep secrets outside the agent, and gateways that judge
  each tool call against the user's intent (No. 003, 004)
- Approval policies as files: agents approving routine changes under a policy kept in the repo,
  merge-risk scores and per-tool approval reviewers (No. 004)
- MCP as the front door: skills, tasks and elicitation over MCP, and platforms requiring agents to
  use MCP and identify as agentic (No. 004)

## Retired (no longer tracked; note the edition)
- (none yet)

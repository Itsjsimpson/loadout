import json
C={"editors":"AI Code Editors & IDEs","builders":"App Builders (Prompt-to-App)","agents":"Coding Agents","frameworks":"Agent Frameworks","backend":"Deploy, Hosting & Backend","design":"Design-to-Code","models":"AI APIs & Models"}
T=[
("Cursor","editors","AI code editor and coding agent platform; hand off tasks to agents or code alongside them.","Day-to-day coding with an agent inside your editor","freemium","https://cursor.com"),
("Devin Desktop (formerly Windsurf)","editors","Cognition's IDE (Windsurf renamed June 2026) with an Agent Command Center for managing local and cloud agents.","Managing multiple agents from a full IDE","freemium","https://devin.ai/desktop"),
("GitHub Copilot","editors","AI pair programmer in VS Code, JetBrains and GitHub, with chat and agent mode.","Teams already living on GitHub","freemium","https://github.com/features/copilot"),
("Zed","editors","Fast, Rust-built collaborative code editor with built-in AI assistance.","Speed-focused devs who want AI without bloat","freemium","https://zed.dev"),
("JetBrains Air","editors","JetBrains' agentic development environment for running Claude Agent, Codex, Junie, Copilot and ACP agents, in IDEs, browser or CLI.","JetBrains users orchestrating coding agents","freemium","https://www.jetbrains.com/air/"),
("Kiro","editors","AWS's agentic IDE built around spec-driven development.","Turning a spec into structured code","freemium","https://kiro.dev"),
("Lovable","builders","Build full-stack web apps by chatting, with Supabase integration.","Non-coders shipping a real web app","freemium","https://lovable.dev"),
("Bolt.new","builders","StackBlitz's in-browser prompt-to-app builder that runs code in WebContainers.","Fast prototypes in the browser","freemium","https://bolt.new"),
("v0","builders","Vercel's generative UI and app builder producing React/Next.js code.","Next.js UIs you can deploy to Vercel","freemium","https://v0.app"),
("Replit","builders","Cloud IDE with Replit Agent that builds and deploys apps from prompts.","Build-and-host in one place","freemium","https://replit.com"),
("Base44","builders","No-code AI app builder that generates apps with built-in backend.","Internal tools and simple apps, no setup","freemium","https://base44.com"),
#REMOVED sunset ("Firebase Studio","builders","Google's cloud workspace for prototyping and building full-stack AI apps.","Prototyping on the Google/Firebase stack","freemium","https://firebase.studio"),
("Claude Code","agents","Anthropic's agentic coding tool for the terminal and IDEs.","Large, multi-step coding tasks from the terminal","paid","https://www.anthropic.com/claude-code"),
("OpenAI Codex","agents","OpenAI's coding agent across ChatGPT, CLI, IDE extension and cloud; included in ChatGPT plans.","Delegating tasks and automated PR review","paid","https://openai.com/codex/"),
("OpenCode","agents","Open-source, model-agnostic coding agent with terminal, desktop and web apps.","Open-source agent with any model","free","https://opencode.ai"),
("Cline","agents","Open-source autonomous coding agent for VS Code; bring your own model.","Transparent agent inside VS Code","free","https://cline.bot"),
("Aider","agents","Open-source AI pair programming in your terminal with git integration.","Git-native terminal pair programming","free","https://aider.chat"),
("Devin","agents","Cognition's autonomous coding agent running parallel cloud agents.","Hands-off async engineering tasks","freemium","https://devin.ai"),
("Jules","agents","Google's asynchronous coding agent that works on your GitHub repos.","Background fixes on GitHub repos","freemium","https://jules.google"),
("Amp","agents","Sourcegraph's agentic coding tool for terminal and editors.","Frontier-model agent work","freemium","https://ampcode.com"),
("LangGraph","frameworks","Framework from LangChain for building stateful, multi-step agent graphs.","Controllable production agents","free","https://www.langchain.com/langgraph"),
("CrewAI","frameworks","Open-source multi-agent framework plus a paid hosted platform.","Multi-agent teams quickly","freemium","https://www.crewai.com"),
("OpenAI Agents SDK","frameworks","Lightweight SDK for building agents with tools, handoffs and guardrails.","Agents on OpenAI models","free","https://openai.github.io/openai-agents-python/"),
("Mastra","frameworks","TypeScript framework for AI agents, workflows and RAG.","JS/TS developers building agents","free","https://mastra.ai"),
("Vercel AI SDK","frameworks","TypeScript toolkit for building AI apps and agents across model providers.","AI features in Next.js/React apps","free","https://ai-sdk.dev"),
("Vercel","backend","Frontend cloud for deploying Next.js and other web apps.","Deploying frontends in one click","freemium","https://vercel.com"),
("Netlify","backend","Platform for deploying and hosting web apps and sites.","Static and Jamstack sites","freemium","https://www.netlify.com"),
("Supabase","backend","Open-source Postgres backend with auth, storage and edge functions.","Backend for vibe-coded apps","freemium","https://supabase.com"),
("Convex","backend","Reactive backend platform with database and server functions in TypeScript; open source.","Realtime apps in TypeScript","freemium","https://www.convex.dev"),
("Cloudflare Workers","backend","Serverless platform for running code at the edge, including agents.","Cheap global serverless + agents","freemium","https://workers.cloudflare.com"),
("Railway","backend","Deploy apps, databases and services from a repo with minimal config.","Hosting backends without DevOps","freemium","https://railway.com"),
("Figma Make","design","Figma's prompt-to-app tool that turns designs and prompts into working prototypes.","Designers turning ideas into prototypes","freemium","https://www.figma.com/make/"),
("Builder.io","design","Visual development platform that converts Figma designs to code.","Figma-to-production code","freemium","https://www.builder.io"),
("Locofy","design","Converts Figma/Penpot designs into frontend code.","Design handoff to React/HTML","freemium","https://www.locofy.ai"),
("Anthropic API (Claude)","models","API access to Claude models, strong at coding and agentic work.","Powering coding agents","paid","https://www.anthropic.com/api"),
("OpenAI API","models","API for GPT models, embeddings, images and realtime voice.","General-purpose AI features","paid","https://platform.openai.com"),
("Google Gemini API","models","Gemini models via Google AI Studio with long context and a free tier.","Long context and generous free tier","freemium","https://ai.google.dev"),
("OpenRouter","models","Single API to access hundreds of models from many providers.","Swapping models behind one key","freemium","https://openrouter.ai"),
("Groq","models","Fast inference cloud for open models, built on its LPU hardware.","Low-latency responses","freemium","https://groq.com"),
]
UNV={"locofy","groq","firebase-studio"}
tools=[dict(id=n.lower().replace(' ','-').replace('(','').replace(')','').replace('.','-'),name=n,category=c,description=d,bestFor=b,pricing=p,url=u,affiliateUrl="",featured=False,verified=None if n.lower() in UNV else "2026-10-15") for n,c,d,b,p,u in T]
usecases=[
{"question":"I can't code but want to ship a web app","picks":["lovable","bolt-new","replit"]},
{"question":"I code daily and want an AI editor","picks":["cursor","devin-desktop-formerly-windsurf","github-copilot"]},
{"question":"I want an agent to handle big tasks in my repo","picks":["claude-code","openai-codex","opencode"]},
{"question":"I want a free/open-source coding agent","picks":["opencode","cline","aider"]},
{"question":"I need a backend + database fast","picks":["supabase","convex","railway"]},
{"question":"I want to deploy my app","picks":["vercel","netlify","cloudflare-workers"]},
{"question":"I'm building my own AI agent","picks":["vercel-ai-sdk","langgraph","mastra"]},
{"question":"I want to turn a design into code","picks":["figma-make","builder-io","locofy"]},
{"question":"Which model API should power my app?","picks":["anthropic-api-claude","openai-api","google-gemini-api"]}]
rel=[
{"name":"OpenCode 2.0","date":"2026-10-13","summary":"Open-source, model-agnostic coding agent with native TUI and multi-session support. #2 on Product Hunt's Oct 13 daily leaderboard (313 upvotes when checked).","url":"https://opencode.ai","source":"https://www.producthunt.com/leaderboard/daily/2026/10/13"},
{"name":"Tiden","date":"2026-10-14","summary":"Verifies coding agents built what you asked for by checking changes against requirements and tests. Works with Claude Code, Cursor, Codex, Copilot.","url":"https://tiden.ai","source":"https://www.producthunt.com/leaderboard/daily/2026/10/14"},
{"name":"Reason","date":"2026-10-14","summary":"Cost-efficient coding agent that writes code, runs tests and opens PRs, from Mac app, terminal, web or Slack.","url":"https://reasonmachines.com","source":"https://www.producthunt.com/leaderboard/daily/2026/10/14"},
{"name":"Exodus for Google Cloud Run","date":"2026-10-14","summary":"Free tool with an open-source CLI: your coding agent (Claude Code, Codex, Cursor) audits your app, compares current cost vs Cloud Run, and migrates it task by task using 50+ playbooks. #8 on launch day.","url":"https://exodus.elim.io/","source":"https://www.producthunt.com/products/exodus-by-elim-io"}]
json.dump({"name":"Loadout","updated":"2026-10-15","categories":[{"id":k,"name":v} for k,v in C.items()],"tools":tools,"useCases":usecases,"newReleases":rel},open("tools.json","w"),indent=1)
ids={t["id"] for t in tools}; assert all(p in ids for u in usecases for p in u["picks"]),[p for u in usecases for p in u["picks"] if p not in ids]
print(len(tools))

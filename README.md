# AutoStartup Simulator

Multi-agent AI system that takes a one-line startup idea and autonomously produces a full startup package — market research, MVP spec, a live deployed landing page, a pitch deck, and a simulated adversarial investor Q&A — end to end, no human in the loop.

Built as a final-year resume project using fully free/local tooling (no paid APIs or cloud tiers).

## Team
| Name | Role |
|---|---|
| Yeshita | Repo owner · Orchestration (LangGraph) · CEO-agent · Investor-agent |
| Lakshit | CTO-agent (codegen + self-fix loop) · CFO-agent · Deployment pipeline · `backend/api/` (streaming layer) |
| Faiza | CMO-agent (market research, GTM, competitor scan) |
| Sakshi | Pitch-deck builder · Frontend UI · Tests · Docs |

## Architecture

```
Idea (1 line)
   -> CEO-agent (parses, delegates)
   -> [CMO-agent | CTO-agent | CFO-agent] (parallel)
   -> CEO-agent (synthesizes) -> Pitch deck
   -> Investor-agent (adversarial Q&A, multi-round rebuttal)
   -> Output: deployed landing page + pitch deck + Q&A transcript + summary
```

Full diagram: [`docs/architecture.md`](docs/architecture.md)
Per-agent details: [`docs/agent_roles.md`](docs/agent_roles.md)
Demo walkthrough: [`docs/demo_script.md`](docs/demo_script.md)

## Folder Structure

```
autostartup-simulator/
├── backend/
│   ├── agents/          # ceo, cmo, cto, cfo, investor
│   ├── orchestration/   # LangGraph state machine
│   ├── api/              # streaming layer / demo UI backend (Lakshit)
│   ├── tools/            # web_search, codegen, deploy, deck_builder
│   ├── models/           # local + Groq LLM client
│   └── utils/
├── frontend/             # Streamlit / React UI
├── data/                 # templates, sample ideas
├── tests/
├── scripts/               # PowerShell setup/run scripts
├── configs/
└── docs/
```

## Setup

### If you have an NVIDIA GPU (Yeshita, Lakshit, Faiza)
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install torch --index-url https://download.pytorch.org/whl/cu128
pip install -r requirements-gpu.txt
python -c "import torch; print(torch.cuda.is_available(), torch.cuda.get_device_name(0))"
```

### If you have no GPU (Sakshi)
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements-cpu.txt
```

### Environment variables (everyone)
```powershell
copy configs\.env.example .env
notepad .env
```
Fill in `GROQ_API_KEY` and `TAVILY_API_KEY` (both free tier).

## Running locally
```powershell
.\scripts\run_dev.ps1
```

## Contributing (fork-based workflow)

1. Fork this repo
2. Clone your fork, add this repo as `upstream`
3. Create a branch: `feature/<short-desc>`
4. Commit, push to your fork, open a PR against `main`
5. Yeshita reviews and merges

See [Quick Reference commands](docs/architecture.md) for full git command list.

## Status

✅ Core pipeline complete — all agents (CEO/CMO/CTO/CFO/Investor) wired with real logic,
42/42 tests passing. Landing page generation + local save working; real deploy (Vercel/
Netlify) in progress. Pitch-deck builder and frontend UI still pending (Sakshi).

## License

MIT
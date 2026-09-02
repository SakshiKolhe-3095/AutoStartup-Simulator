# Demo Script — AutoStartup Simulator

## Pre-Demo Checklist (do this ~30 min before)
- [ ] Confirm Groq quota isn't already exhausted: check console.groq.com usage dashboard
- [ ] Run one full pipeline test with a DIFFERENT idea than the demo idea, to "warm up" and confirm everything works, WITHOUT burning the demo idea's freshness
- [ ] Have `data/batch_test_results.json` (or a fresh saved output) open as backup — screenshot or have the JSON ready to paste into a text viewer if live generation fails
- [ ] Confirm frontend is running: `cd frontend && npm run dev` (or however Sakshi's app starts)
- [ ] Confirm backend is running: `python -m backend.main` (or uvicorn command)
- [ ] Close unnecessary browser tabs/apps to avoid distractions and reduce chance of accidental key mash

## Recommended Demo Idea
**"AI-powered plant disease detector for farmers"**
- Reason: run repeatedly and successfully throughout development — known-good output, real competitor list, strong investor Q&A with genuine rebuttal rounds, valid landing page.
- Backup idea if asked for a second example live: "Marketplace connecting local artisans with buyers" (also verified working in Wk9 batch test).

## Walkthrough Steps

**1. Introduce the problem (30 sec)**
"Every founder needs market research, a tech spec, a landing page, financials, and to survive investor questions — normally that's days of work across multiple tools. This does it in one pipeline, autonomously."

**2. Show the input (10 sec)**
Type the idea into the frontend's IdeaForm. Hit submit.

**3. Narrate while it runs (~90-120 sec typical runtime)**
Point out the LiveLog component streaming each agent's progress:
- CEO parses the idea
- CMO researches market size + competitors (mention: real web search via Tavily)
- CTO designs the MVP + generates and deploys a live landing page (mention: real Netlify URL, not a mockup)
- CFO grounds financials in CMO's actual market data (not invented independently)
- Investor agent fires real questions and pushes back with rebuttals

**4. Show the results (60-90 sec)**
- Landing page: click the live Netlify URL, show it's a real deployed site
- Investor score + Q&A: highlight a rebuttal/defense round — show the investor didn't just accept a vague answer
- Pitch deck: open/download the generated deck, flip through a couple slides (market sizing, financials, landing page screenshot slide)

**5. Close (15 sec)**
"Everything you just saw — the research, the code, the deck, the deployment — happened without a human writing a single line. That's the point: autonomous agents, not just an LLM wrapper."

## Contingency Plan — If Groq Quota Fails Mid-Demo
This has happened repeatedly during development (documented in `docs/architecture.md`). Don't panic on stage:
1. Say: "Looks like we've hit our free-tier API limit for today — let me show you a run from earlier."
2. Open the saved output (`data/batch_test_results.json` or a dedicated `demo_backup_output.json` — create one from today's best clean run and commit it specifically for this purpose).
3. Walk through the saved JSON / screenshots the same way as steps 3-4 above, narrating as if live.
4. Don't over-apologize — frame it as "this is exactly the kind of real-world constraint we documented and handled gracefully" (node-level error handling, retry logic) — turns a limitation into a demonstrated engineering strength.

## Known Limitations (mention if asked, don't volunteer unprompted)
- Free-tier Groq quota (200k tokens/day) limits repeated full runs — team distributes API keys across separate accounts to mitigate
- `investor_score` is LLM-judged, not a deterministic rubric — reasonable proxy, not a precise metric
- Local Ollama fallback for persona generation isn't always available depending on machine setup — Groq fallback handles this transparently
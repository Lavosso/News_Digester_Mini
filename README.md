# News Digester Mini
A news-gathering system for making a daily information digest.

## v0.1 
- [x] Source listing in JSON.
- [x] Data gathering through HTTP.
- [x] Timeout and error handling.
- [ ] Title/link/date extraction.
- [ ] Markdown output.

## Mental Model
Source list → **Executor (main)**

**Executor (main)** → Source → **Data gatherer (web)**

**Data Gatherer (web)** → Source data → **Data extractor (web)**

**Data extractor (web)** → Clear data →  **Markdown setuper (data)**

**Markdown setuper (data)** → Markdown-ready data → **Markdown writer (files)**

## 0.1 To-Do
- [x] (main) Executor
- [x] (web) Data gatherer
- [x] (data) Data extractor
- [ ] (data) Markdown setuper
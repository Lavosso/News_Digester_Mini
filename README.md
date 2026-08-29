# News Digester Mini
A news-gathering system for making a daily information digest.

## v0.1 
- [ ] Source listing in JSON.
- [ ] Data gathering through HTTP.
- [ ] Timeout and error handling.
- [ ] Answer cache.
- [ ] Title/link/date extraction.
- [ ] Markdown output.

## Mental Model
Source list → **Executor (main)**

**Executor (main)** → Source → **Data gatherer (web)**

**Data Gatherer (web)** → Source data → **Data extractor (data)**

**Data extractor (data)** → Clear data → **Data Cache (files)**

**Data Cache (files)** → Checked data → **JSON logger (files)**

**JSON extractor (files)** → Full daily json data → **Markdown setuper (data)**

**Markdown setuper (data)** → Markdown-ready data → **Markdown writer (files)**

## 0.1 To-Do
- [ ] (main) Executor
- [ ] (web) Data gatherer
- [ ] (data) Data extractor
- [ ] (data) Markdown setuper
- [ ] (files) Data cache
- [ ] (files) JSON logger
- [ ] (files) JSON extractor
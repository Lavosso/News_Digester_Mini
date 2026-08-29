# News Digester Mini
A news-gathering system for making a daily information digest.

## Features
By launching this script, a number of md files is created, in which one can find summaries of daily news
(both from the country of Poland and from the world.) The news are gathered from ONET.

## v0.1 
- [x] Source listing in JSON.
- [x] Data gathering through HTTP.
- [x] Timeout and error handling.
- [x] Title/link/date extraction.
- [x] Markdown output.

## Mental Model
Source list → **Executor (main)**

**Executor (main)** → Source → **Data gatherer (web)**

**Data Gatherer (web)** → Source data → **Data extractor (web)**

**Data extractor (web)** → Clear data → **Markdown writer (files)**

## 0.1 To-Do
- [x] (main) Executor
- [x] (main) Markdown writer
- [x] (web) Data gatherer
- [x] (web) Data extractor
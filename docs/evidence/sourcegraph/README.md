# Sourcegraph Query Evidence Directory

**Course Requirement:** A1 Handout Compliance (10 marks) — Semantic Code Navigation  
**Reference Document:** `docs/sourcegraph_setup.md`

Please save the 5 query screenshots in this directory with the following filenames:

1. `01_symbol_search.png`: Screenshot of `repo:^github\.com/pallets/flask$ type:symbol test_client`
2. `02_references_search.png`: Screenshot of `repo:^github\.com/pallets/flask$ test_client(`
3. `03_regex_defaults.png`: Screenshot of `repo:^github\.com/pallets/flask$ def .+\(.*timeout\s*=\s*\d+`
4. `04_diff_search.png`: Screenshot of `repo:^github\.com/pallets/flask$ type:diff timeout`
5. `05_lang_filtered.png`: Screenshot of `repo:^github\.com/pallets/flask$ lang:python config.from_object`

Each screenshot should clearly show:
- The Sourcegraph search query bar with the exact query text.
- The repository name (`pallets/flask`).
- The search result matches with line numbers and preview snippets.

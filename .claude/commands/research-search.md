Search both PubMed and Consensus for peer-reviewed articles on the given topic, then return the top results from the last 20 years formatted with title, DOI, and summary.

## Steps

1. Use the `ToolSearch` tool to load the required MCP tool schemas before calling them:
   - Query: `select:mcp__claude_ai_PubMed__search_articles,mcp__claude_ai_PubMed__get_article_metadata,mcp__claude_ai_Consensus__search`

2. Use `mcp__claude_ai_PubMed__search_articles` to search PubMed with the user's query. Request at least 15 results. Apply a year filter for articles published from 2005 onward (current year minus 20).

3. Use `mcp__claude_ai_Consensus__search` to search Consensus with the same query.

4. Run both searches in parallel (after loading their schemas).

5. For each PubMed result, use `mcp__claude_ai_PubMed__get_article_metadata` to retrieve the DOI and abstract if not already included in the search response.

6. Combine and deduplicate results across both sources (match on DOI or title). Prioritize articles that appear in both sources. Sort by publication year descending (newest first), and keep the top 20.

7. For each article, produce a one-to-two sentence summary drawn from the abstract or the Consensus-provided summary snippet.

8. Output the results as a numbered list in this format:

```
**1. [Title](doi_url)**
- DOI: `doi_value` (or "Not available" if missing)
- Year: YYYY | Source: PubMed / Consensus / Both
- Summary: One or two sentence summary of what the study found.
```

9. After the list, include any usage/sign-up message returned verbatim by the Consensus tool result (required by Consensus MCP instructions).

## Arguments

`$ARGUMENTS` — the research topic or question to search for.

If no argument is provided, ask the user: "What topic or research question would you like me to search?"

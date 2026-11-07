#!/usr/bin/env bash
# Run one Codex agent to write one blog post from its brief.
#
#   blog/run-codex.sh 01-semula-subscription-as-mock-llm
#
# Run one at a time. The agent may write blog/posts/<slug>.md (and images under assets/blog/),
# and may read the sibling product repositories. It leaves status: Draft.
set -euo pipefail
cd "$(dirname "$0")/.."
name="${1:?usage: blog/run-codex.sh <brief name without .md>}"
brief="blog/briefs/${name}.md"
[ -f "$brief" ] || { echo "no such brief: $brief" >&2; exit 1; }
mkdir -p blog/.runs
parent="$(dirname "$PWD")"
codex exec --sandbox workspace-write --ephemeral -C "$PWD" \
  -o "blog/.runs/${name}.report.txt" \
  "Write the blog post described in ${brief}. First read blog/AGENTS.md and follow it exactly. \
The product repositories are siblings of this one under ${parent}: read them, never modify them. \
Write only the post file named in the brief, with status Draft. Finish with the three lists that blog/AGENTS.md asks for."
echo
echo "report: blog/.runs/${name}.report.txt"
echo "preview: uv run scripts/build_blog.py --drafts --out /tmp/blog-preview"

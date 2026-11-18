# Example knowledge base

These files demonstrate document page headings, transcript timestamps and web-source metadata. All content is fictional and newly written for this repository. No private documents, real transcripts, personal information or credentials are included.

Examples live outside the active `knowledge/` directory so they cannot affect an existing course knowledge base. To use them in a fresh clone, run from the repository root:

```sh
cp examples/knowledge/documents/*.md knowledge/documents/
cp examples/knowledge/videos/*.md knowledge/videos/
cp examples/knowledge/web/*.md knowledge/web/
.venv/bin/python -m beru.knowledge
```

Rebuilding the index invalidates existing vector indexes; rebuild optional semantic/cloud indexes afterward if you use them. Do not rebuild an existing installation just to inspect these examples.

Try these source-grounded questions:

1. At the fictional Northstar Workshop, which label means a prototype is being tested? A. Amber; B. Blue; C. Green. **Expected: B.**
2. Does a Green label mean public release? A. Yes; B. No. **Expected: B.**
3. What must a completed review record? A. Only the problem; B. Only the prototype label; C. The next action and its owner. **Expected: C.**

Replace these demonstrations with your own source material for real use. Example answers are not part of the evidence files copied above.

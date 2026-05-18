# Hosting WikiMind (Streamlit)

Fastest path: **[Streamlit Community Cloud](https://streamlit.io/cloud)** (free, GitHub-connected).

## 1. Push the repo to GitHub

Ensure `app.py` is at the repo root and `requirements.txt` is committed.

## 2. Deploy on Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.
2. **New app** → pick this repository, branch, and main file **`app.py`**.
3. Under **Advanced settings** → **Secrets**, paste (use your real values):

```toml
OPENAI_API_KEY = "sk-..."
# Optional: managed Redis (e.g. Redis Cloud free tier). If omitted, cache/session Redis features disable gracefully.
REDIS_URL = "redis://default:PASSWORD@HOST:PORT"
```

4. Deploy. First build can take several minutes (`cognee` is heavy).

## 3. What works without Redis

If you skip `REDIS_URL`, the app still runs: **Ask**, **Wiki**, **Knowledge Graph**, and **Audit** work. **SemanticCache** and **MessageHistory** need a reachable Redis URL.

## 4. Alternative: Render / Railway / Fly

Use a **Web** service with:

- **Build:** `pip install -r requirements.txt`
- **Start:**  
  `streamlit run app.py --server.port=$PORT --server.address=0.0.0.0 --server.headless true`
- Set **environment variables** `OPENAI_API_KEY` and optionally `REDIS_URL` (same as local `.env`).

`app.py` copies **`st.secrets`** into `os.environ` for Streamlit Cloud only; on Render/Railway use env vars directly (no `st.secrets`).

## 5. Demo caveats

- Cognee/LanceDB use disk under the app directory; treat the cloud instance as **ephemeral** unless you add persistent storage.
- For a stable public demo, consider a **pinned** `requirements.txt` and a small smoke test after each deploy.

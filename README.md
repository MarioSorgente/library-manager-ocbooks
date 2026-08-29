# OCBooks

OCBooks is a Flask application for maintaining a personal book library.

## Deploying to Vercel

1. Import this repository into Vercel.
2. Attach a managed PostgreSQL database (Neon, Supabase, or another provider).
3. Add these environment variables in the Vercel project settings:
   - `DATABASE_URL`: the PostgreSQL connection string. `POSTGRES_URL` and
     `POSTGRES_PRISMA_URL` are also recognized.
   - `FLASK_SECRET_KEY`: a long, random value shared by every function instance.
4. Deploy. Vercel uses `api/index.py` as the Python Function and routes requests
   to the Flask application according to `vercel.json`.

Without a database variable, preview deployments use SQLite under `/tmp`. That
storage is ephemeral and is not suitable for production data.

## Running locally

Create a virtual environment, install the Python dependencies, and start Flask:

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
export FLASK_SECRET_KEY="development-only-secret"
python main.py
```

The app is then available at <http://localhost:5000>.

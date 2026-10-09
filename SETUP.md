# My Food Tracker v9 — free cloud + mobile + simple email profile

v9 keeps the v8 app and database, but removes passwords, signup and email verification.
A person simply enters an email address and that email becomes the profile key.

**Important:** this is NOT secure authentication. Anyone who types another person's email address can open that profile. Use it only for non-sensitive personal/family tracking.

## If you already deployed v8
You do **not** need a new Supabase project, GitHub account, or Streamlit app.

1. In your existing Supabase project, open **SQL Editor → New query**.
2. Open `supabase_v9_migration.sql` and run the whole script.
3. Replace the files in your existing GitHub repository with the v9 files from this ZIP.
4. Streamlit Community Cloud should redeploy automatically after the GitHub change. If it does not, use **Manage app → Reboot app**.
5. Open the same website. You will now see a simple email field instead of password login.

The migration attempts to preserve your existing v8 food logs, weight history and custom foods by converting each authenticated user's UUID to the email stored in Supabase Auth.

## If you are setting it up for the first time
1. Create a project at https://supabase.com/ and choose the free plan.
2. In **SQL Editor → New query**, run `supabase_schema.sql`.
3. Open **Project Settings → API** and copy the Project URL and publishable/anon key. Never use the service-role/secret key.
4. Create/sign in to GitHub at https://github.com/.
5. Upload `app.py`, `requirements.txt`, `supabase_schema.sql`, `.streamlit/config.toml`, `README.md` and `SETUP.md` to a repository.
6. Deploy that repository on Streamlit Community Cloud.
7. In Streamlit app settings → Secrets, add:

```toml
SUPABASE_URL = "https://YOUR-PROJECT.supabase.co"
SUPABASE_ANON_KEY = "YOUR_PUBLISHABLE_OR_ANON_KEY"
```

No Supabase Authentication configuration is required for v9.

## How users access the app

```text
Open website
    ↓
Enter email address
    ↓
Continue
    ↓
Today / History / Weight / Food list
```

Example:
- `hema@gmail.com` → one profile
- `friend@gmail.com` → another profile

No password, signup or email verification is required.

## Mobile
Open the same `*.streamlit.app` URL on the phone browser. You can add it to the home screen using the browser's **Add to Home Screen** option.

## Privacy and security
- Data is separated using the entered email address.
- This version intentionally does not use Supabase Auth or RLS.
- Anyone who knows/guesses another profile's email can access and modify that profile.
- Do not use this version for medical records, financial information, passwords or other sensitive data.
- Never put a Supabase service-role/secret key in GitHub or Streamlit secrets unless the app specifically requires it; this app only needs the publishable/anon key.
- Nutrition values are approximate and can vary by recipe and serving size.

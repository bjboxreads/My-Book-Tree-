# SpineVesper — Flet port

## What's here
- `data.py` — your original logic (CSV save/load, ISBN cleaning, series
  detection, Google Books / OpenLibrary metadata fetching, Goodreads
  import parsing). Ported almost line-for-line from your Streamlit
  `app.py`, no Streamlit dependency.
- `main.py` — a working Flet UI: Books list (search, filter by status,
  group by Author/Genre, favorite toggle, edit/delete), Add Book form,
  Import (CSV/Excel/txt with threaded metadata fetch).
- `requirements.txt`
- `build-apk.yml` — GitHub Actions workflow, builds the APK in the
  cloud. **Move this file into `.github/workflows/build-apk.yml`**
  in your repo (GitHub Actions only looks there).

## What's NOT ported yet
- The fancy HTML "Book Spire" tree view with the custom pill/CSS
  styling — replaced with a plainer expandable list for now
  (`ExpansionTile` grouped by Author/Genre). Functionally equivalent,
  visually simpler. Can be styled further once the app builds.
- The 10 color themes / theme picker.
- The data-editor-style bulk table edit (Edit/Delete tab) — replaced
  with tap-to-edit-one-book-at-a-time via a dialog.
- Star ratings widget on the Add form.
- The `?toggle_fav=` query-param favorite trick — not needed in Flet,
  favorite toggle is a normal button now (already implemented, simpler).

None of that is lost — it's just not rebuilt yet. The data underneath
(your CSV, your columns) is 100% compatible either way.

## How to actually run this

1. Replace the contents of your GitHub repo with these files (keep
   your repo's `.devcontainer` and `.streamlit` folders if you want,
   they just won't be used anymore).
2. Move `build-apk.yml` to `.github/workflows/build-apk.yml`.
3. Push to `main`.
4. Go to the **Actions** tab on GitHub → you'll see "Build Android
   APK" running. Takes a few minutes.
5. When it's green, click into the run → scroll to **Artifacts** →
   download `storyspire-apk`. That's your `.apk` file.
6. Install that APK on an Android phone to test it (you can sideload
   it directly, no Play Store needed for testing).
7. When ready for the Play Store, you'll need to build an **AAB**
   instead of APK for the actual store listing — same workflow file,
   just change `flet build apk` to `flet build aab`.

## Testing locally in Codespaces (optional, before pushing)
In your Codespace terminal:
```
pip install flet
flet run main.py
```
This opens a preview in the browser — good for checking the UI
before waiting on a full APK build.

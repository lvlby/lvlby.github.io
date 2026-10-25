# LvLBY — Project Handoff

Give this file plus the site files to any developer or AI assistant. It explains what the project is, what was built, what was decided, and what is still open.

## 1. What it is
LvLBY is a bilingual (Persian RTL / English) daily planner, delivered as a Progressive Web App. It is a single `index.html` with inline CSS and vanilla JavaScript (no framework, no build step). Data lives in the browser's localStorage. Optional Google sign-in syncs data through Firebase (Auth + Firestore, SDK 10.14.1 compat build, loaded from gstatic.com).

Owner context: a non-technical but detail-oriented owner in Iran. Most users are in Iran. The owner wants nothing paid. The UI language of conversation was Persian.

## 2. Files
| File | Purpose |
|---|---|
| `index.html` | The whole app |
| `privacy.html` | Bilingual privacy page (EN/FA toggle). No contact email by design |
| `sw.js` | Service worker. Cache name `lvlby-v20261025`. HTML is network-first, other same-origin GETs cache-first. Cross-origin requests are ignored. **Change the cache name on every release** |
| `manifest.webmanifest` | PWA manifest (`start_url: "./"`, standalone, theme `#101522`) |
| `icons/` | `icon-192.png`, `icon-512.png`, `apple-touch-icon.png` (owner-supplied "Lv" logo) |
| `README_upload.txt` | Short upload instructions |
| `توضیحات_تغییرات.md` | Persian changelog |

All paths are relative, so the site works under a sub-path such as GitHub Pages `/LvLBY-/`.

## 3. Hosting
- Original host: Cloudflare Pages (`lvlby.pages.dev`). **It is filtered in Iran** (confirmed by the owner), so it was abandoned.
- Current host: GitHub Pages, `https://r36140428-gif.github.io/LvLBY-/`. It works from outside Iran. The owner confirmed it works for them. Whether it works without a VPN for all Iranian users is not verified.
- Planned: rename GitHub username to `lvlby` and repository to `lvlby.github.io` for the URL `https://lvlby.github.io`. Not done yet.
- After any domain change, add the new domain in Firebase Console → Authentication → Settings → Authorized domains, or Google sign-in will fail. Not verified or done.
- Each origin has separate localStorage. Users moving to a new URL must use Export backup then Import backup.
- Repository is public. `.gitignore` uses the Node template.

## 4. Architecture notes (index.html)
- State: `data` (days, routine, schedule), `P` (profile/onboarding answers), `S` (settings). Saved to localStorage via `save()`, `saveP()`, `saveS()`.
- `ensureDay(date)`, `buildDay(date)`: build a day's tasks from routines, shift and templates. `renderToday()` calls `buildDay` every time. `staleDay()` forces a rebuild of cached days when rules change.
- Shifts: `activeShift(date)` returns morning, afternoon or off. For non-students (`notStudent()`, `P.student===false`) it always returns off, and school UI is hidden with `.stuonly`.
- Morning routine items shift by `morningDelta(shift)` for non-morning shifts. Four fixed tasks (`bed`, `brush-am`, `wash-am`, `water`) are excluded from the afternoon shift.
- Onboarding: object `ob`, text `OB[lang]`, `renderOb()`. After the questions, `pzApply(pzBuild())` configures routines silently, then the product tour starts (`TOUR`, `startTour()`).
- Custom UI instead of native dialogs: `uiConfirm()` (promise-based) and `enhanceSelect()`/`uiPick()` (bottom-sheet selects).
- Today view: `renderTodayHead()`, `emptyState()`, `doneCard()`, `attachSwipe()` (touch: swipe right completes, swipe left deletes custom tasks only, with confirm).
- Weekly summary: `renderWeekly()` fills `#weeklyCard` at the top of the Insights view (7-day percent, change vs previous week, bar chart, stats, message).
- Tab scrolling: `softScroll()` (custom eased scroll).
- Keyboard: N or Q focuses `#quickName`.
- Firebase is loaded asynchronously by an inline loader script in the head area (three scripts in sequence). After they load, it calls `setupFirebase()`. This keeps the app usable when gstatic.com is blocked. `setupFirebase()` is also called at app start and returns early if `firebase` is undefined.
- Language helper `L(en, fa)`, numerals via `fa()`.

## 5. Decisions made with the owner
- Profile section removed from Settings; first-visit wizard replaces it; edit via a coach card on Today.
- Plan is applied automatically after questions; no review screen.
- Tour always runs after onboarding.
- Design follows Todoist/Things/Linear principles: flat surfaces, plain task rows, round checkbox, single accent (`--accent:#a8e6c3`), bottom tab bar on mobile.
- No native `confirm()` or `<select>` UI.
- Privacy page has no contact email (owner had none to provide).

## 6. Testing status (important)
- Verified only with `node --check` syntax checks and a Node `vm` harness that stubs the DOM, to run logic functions. Layout, CSS, touch gestures, PWA install and real network behavior were **not** tested on a device by the assistant.
- The owner confirmed the GitHub Pages site opens, and earlier screenshots helped find real bugs.
- Not verified: Firestore Security Rules (make sure each user can only read/write their own document), Google sign-in on the new domain, service worker update behavior for returning visitors.

## 7. Known gaps and ideas
- Manual drag-to-reorder was not built: task order is derived from each task's `time`.
- `<input type="date">` still uses the native browser picker.
- Accessibility pass (ARIA, contrast audit, 44px targets) not done systematically.
- Task search not built. iOS notification limitations not documented to users.
- The Firebase config is public inside `index.html` (normal for web apps); real protection is the Firestore rules.
- `privacy.html` text should be re-read against the real data practices before wide release. It states: data local by default; Google sign-in saves to Google Firebase; no ads; no selling; export/erase in Settings.

## 8. Release checklist for any change
1. Edit `index.html` (check syntax of the inline `<script>` blocks).
2. Bump the cache name in `sw.js`.
3. Upload changed files to the repository root (icons go in `icons/`; the mobile web uploader cannot upload folders, so create the folder via a `icons/.gitkeep` file first).
4. Hard refresh or reopen the installed app.

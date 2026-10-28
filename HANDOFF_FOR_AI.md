# LvLBY - full handoff for another AI or developer (state: v20)

Read this first. It tells you what the project is, how it is built, what the owner wants, what was done, the traps already hit, and what is open. Be honest with the owner about anything you could not test.

## 1. The product
LvLBY is a bilingual (Persian RTL + English) daily planner shipped as a PWA: routines, school shifts, habits, streaks, XP, a pet, calendar, weekly summary, a guided first-run, and "Smart Add" (one sentence in natural language becomes a task or a repeating routine). Everything is ONE file: `UPLOAD-THESE/index.html` (inline CSS + vanilla JS, no framework, no build). Data is in localStorage; optional Google sign-in syncs to Firebase (Auth + Firestore, SDK 10.14.1 compat, loaded async from gstatic).

## 2. The owner (important)
- Non-technical, detail-oriented, writes mostly Persian (sometimes English). Wants zips that are "just upload".
- Wants honesty: say what was NOT tested or NOT done. Ask a short question when a request is unclear.
- Spends nothing: no paid domain/hosting. Most users are in IRAN (many are not on a VPN), a few friends abroad.
- Uploads from an Android phone through the GitHub web UI. The phone file picker greys out `.js` and `.webmanifest`; workaround: create/edit those files in GitHub's editor and paste the text. Folders cannot be uploaded; create `icons/` through a new file named `icons/.gitkeep`.

## 3. Hosting and accounts
- Live: GitHub Pages, repo `r36140428-gif/LvLBY-` -> `https://r36140428-gif.github.io/LvLBY-/`. Planned: rename user/repo to `lvlby` / `lvlby.github.io` (then `https://lvlby.github.io`). After any domain change: add the domain in Firebase Console -> Authentication -> Settings -> Authorized domains, and use Export/Import backup (localStorage is per origin).
- Old host `lvlby.pages.dev` (Cloudflare) is FILTERED in Iran - abandoned.
- Google Search Console: the tag `<meta name="google-site-verification" content="_7FF6-DqwLL2H4nPB4FP7Nh_jmNdA7ZfPe7kicY85B4">` is already in `<head>`. The owner pasted the same token in its DNS-TXT form (`google-site-verification=...`); on GitHub Pages without a custom domain only the meta-tag method works, and the property URL must be the site root.
- Firestore rules: `PASTE-IN-FIREBASE-RULES.txt`. They whitelist top-level keys, the keys of `data`, `settings` and `profile`. ADDING A NEW PROFILE/SETTINGS KEY REQUIRES UPDATING THE RULES or cloud sync fails. Fields added inside routine items (ev, wk, from, until) are nested in `data.routine` and are fine. The rules were never verified in the live Firebase console by the assistant.

## 4. Files
| Path | Role |
|---|---|
| `UPLOAD-THESE/index.html` | the whole app |
| `UPLOAD-THESE/privacy.html` | bilingual privacy page, no contact email on purpose |
| `UPLOAD-THESE/sw.js` | service worker; HTML network-first, other same-origin GET cache-first; **bump `CACHE` every release**; `ASSETS` must list only files that exist (a missing file makes `addAll` fail and the SW never installs) |
| `UPLOAD-THESE/manifest.webmanifest` | PWA manifest; separate `any` and `maskable` icons |
| `UPLOAD-THESE/icons/` | icon-192, icon-512, apple-touch-icon, icon-maskable-192/512 (owner's "Lv" logo; maskable = logo scaled to 72% on #101522) |
| `PASTE-IN-FIREBASE-RULES.txt` | Firestore rules |
| `CHANGES-v12.txt` | running changelog v12..v18 |
| `extras/tests.js` | original author's logic tests |
| `extras/test-scripts/` | Playwright scripts used for audits (paths point to the author's sandbox; edit `F`) |

## 5. Code map (names to search for in index.html)
- Language: `lang` ('en'|'fa'), `L(en,fa)`, `tr(key)` with dictionaries `I`, `ST`, `SS`, `OB`, `XT`, `SAT`, `NT`; `fa(n)` Persian digits; `dayLabel(date,opts)` (custom Persian order: weekday، day month year).
- State: `data` {days, routine, schedule, weeks, templates, exams, vac}, `P` profile, `S` settings; `save()/saveP()/saveS()`.
- Day building: `ensureDay`, `buildDay(date)`, `staleDay`, `activeShift`, `onDate(it,date)` (weekday filter + recurrence fields `ev` every N days, `wk` every N weeks, `from`, `until`), `morningDelta`, `AFT_SKIP`, `notStudent()`.
- Names: routine items created by the personal setup store a name in the language active at creation. `PZN` + `locName()` + `displayTaskName()` re-localize them at display time (only if the user did not rename them).
- Questions: `QS` (each has `since`; energy and dayType = 2, rest = 1), `ONB_VER=2`, `obHasAny()`, `obNeeded()`, `obPending()`, `obStart(edit,update)`, `renderOb()` stages: `welcome`, `q`, `building`, `ready`, `connect`; `obAfterQuestions()`, `obFinish()`, `pzBuild()/pzApply()`, `welcomeGate()`, `renderStartCard()`.
  Rules: nobody answered -> all questions; answered before -> only questions with `since > P.ov` or required and still empty. New question later: add to `QS`, set its `since`, bump `ONB_VER`; if it stores a NEW profile key, update the Firestore rules first.
- Flow after the last question: "Building your routine" (6-9 s random, bar moves in 5 steps with pauses; the routine is already computed and saved) -> "ready" -> tour (`TOUR`, `startTour`, `endTour`; only for first-time completion, not for update-only) -> then the Google connect card (so a blocked Google can never block the tour).
- Smart Add parser: object `SA` (`SA.parse(text,ctx,opts)`, `SA.recur`, `SA.recurN`, `SA.dur`, `SA.numAt`, `SA.unit`), commit in `smartCommit`. Understands dates, times, deadlines, every day/week/weekday, every N days, every N weeks (+weekday), "for/till N days|weeks|months" (alone = daily for that period), English and Persian (also number words, "یک روز در میان").
- Firebase: `setupFirebase()` (guarded by `window.__fbDone`), `authChanged`, Firestore with `experimentalForceLongPolling`; on `unavailable`/"client is offline" it keeps local data, shows a calm message and retries (6 s, 12 s ... 60 s) and on the `online` event.
- UI helpers: `uiConfirm`, `enhanceSelect/uiPick`, `softScroll`, swipe on tasks (`attachSwipe`), `renderTodayHead`, `emptyState`, `doneCard`, `renderWeekly`, `fixFaBits` (Persian date label over the native date input, Persian digits in task times, language button text, footer link).

## 6. Persian rules learned the hard way
- The source contains LITERAL zero-width non-joiners (U+200C) inside Persian strings. When patching with Python use the real character (`'\u200c'`), not the text `\u200c`.
- Do not use a middle dot next to digits in Persian (it looks like a zero); use an em dash or a comma.
- Use ezafe with the hamza form: برنامهٔ امروز، همهٔ کارها، صفحهٔ اصلی. Persian percent: the code uses `%`.
- Anything built with `L(...)` and stored in data is frozen in the language of that moment - always store both languages or an id and translate at display.
- Native `<input type=date>` shows English digits; a Persian label overlays it in fa mode (the picker itself is the browser's).

## 7. How the work was verified
- Headless Chromium via Playwright at 390x844, file:// URL, network blocked except file. Scripts: `extras/test-scripts/`. They: open each tab in en and fa, flag Latin in fa / Persian in en / "undefined|NaN|[object", collect console errors, walk the onboarding, simulate returning users (old profile, missing answers), simulate a Firestore "unavailable" error with a stubbed `firebase`, and sample the progress bar width over time.
- NOT done: real phones, real Iranian networks, real Firebase sign-in, the live Firestore rules, screen readers, iOS Safari, notification delivery, install flow on iOS.
- The owner's real-phone screenshots found bugs automation missed (stale cached days, English routine names in fa mode). Ask for screenshots.

## 8. Version history (short)
v11 (from another AI) -> v12 welcome popup + start card (the old code that opened the questions was accidentally nested inside the notifications button), offline-cloud retry, Persian fixes -> v12b question wording + icons -> v13 Smart Add repeats -> v14 tour step + tour right after questions -> v15 "building" screen -> v16 versioned questions + Persian proofreading -> v17 6-9 s stop-and-go bar -> v18 routine names localized -> v19 more colour (per-tab accents, gradients), header overflow fix at 360 px, bottom tab bar and report rows fixed.

## 9. Open items / ideas
- Rename GitHub user/repo, Firebase authorized domain, verify the live Firestore rules.
- Habits tab does not show the interval (ev/wk/until) of repeating items; items appear on the right days though.
- Manual drag-to-reorder not built (order comes from each task's time). Tour step "repeats" does not scroll to the Smart Add box.
- Remaining Persian screens were proofread by reading the rendered text of tabs, settings, tour and questions; small toasts/error strings were not each read.
- Accessibility pass, task search, iOS notification caveats.

## 10. Release checklist
1. Patch `index.html` with a script that asserts each replacement matches exactly once.
2. Syntax-check every inline `<script>` (`node --check`), run the audit and flow scripts, look at screenshots.
3. Bump `CACHE` in `sw.js`; keep `ASSETS` in sync with real files.
4. Owner uploads `index.html` + `sw.js` (+ any new file) to the repo root; hard refresh.
5. Tell the owner plainly what was and was not tested.

## v20 additions
backupNudge, renderInstallBar, shareCardBlob/doShareCard, TPL templates (search '/* ---- v20'). og:image URL is hard-coded to r36140428-gif.github.io/LvLBY- : update after the rename. Template item names are stored in the language active when applied (frozen).

## v21
XP toggle removed (S.xp forced true). ICS now opens a confirm dialog (openIcsDialog) with routine/tasks/exams toggles (exams only if P.student), lead select, Edit-routine button. SW install uses allSettled so one missing asset no longer breaks caching. Added inline SVG favicon fallback. Home-screen icon showing a gray 'G' = icons/ folder missing on the live site.

## v22
Holidays: HF (fixed solar) + HL[1405] (lunar, cross-checked from several Iranian calendar sites, may shift 1 day; 1406+ lunar NOT included) at top of main script (must stay before first render: TDZ). holName(d) used in renderCal (class hol, also Fridays in Shamsi mode) and Today dateLabel. Nightly review: NR pools, composeNight, renderNight (shows after 20:00 or when >=3 tasks all done; cached in localStorage lvlby_rv, last-variant memory lvlby_rvlast). No new Firestore keys.

## v24
Friend challenge (v23) was REMOVED on request; Firebase rules are back to users/{uid} only. Login/sync unchanged (known issue: Google login and Firestore are filtered in Iran; user will revisit).

## v25
Share card redesigned (glass card, progress ring to next milestone, 7-day strip, stats). Friend challenge stays removed.

## v26
Framer-style: about.html rebuilt (bilingual toggle, bento, motion, reduced-motion safe); app skin = CSS block after '/* v26 skin' (visual only); About link in Settings; fixed empty install bar flashing before first render (v20-v25 bug). Time inputs in Habits are narrow (86px) on 390px screens - pre-existing.

## v27
Dark theme forced once for everyone (localStorage lvlby_dark26), user can change later. Smart Add button label set at init; undo bar hidden from focus when not shown. Audit script covered: 5 viewports, en/fa, 10h/21h, all tabs/settings, smart add, export/import, offline SW, a11y names, overflow, bad text.

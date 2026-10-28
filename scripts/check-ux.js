#!/usr/bin/env node
/**
 * Lightweight regression checks for the LvLBY UX-brief changes.
 * Static site: no bundler, no test runner. This script asserts the invariants
 * the brief cares about (navigation wiring, sync-status clarity, a11y hooks)
 * and that the shipped scripts still parse. Exits non-zero on failure.
 *
 * Run: node scripts/check-ux.js
 */
const fs = require('fs');
const path = require('path');
const os = require('os');
const { execFileSync } = require('child_process');

const root = path.resolve(__dirname, '..');
const html = fs.readFileSync(path.join(root, 'index.html'), 'utf8');
const sw = fs.readFileSync(path.join(root, 'sw.js'), 'utf8');

let failures = 0;
const fail = (msg) => { failures++; console.log('FAIL  ' + msg); };
const pass = (msg) => console.log('ok    ' + msg);
const check = (cond, msg) => (cond ? pass(msg) : fail(msg));

/* ---------- 1. no duplicate element ids (breaks getElementById targets) ---------- */
const ids = [...html.matchAll(/\sid="([^"]+)"/g)].map((m) => m[1]);
const dupes = [...new Set(ids.filter((id, i) => ids.indexOf(id) !== i))];
check(dupes.length === 0, 'no duplicate element ids' + (dupes.length ? ' -> ' + dupes.join(', ') : ''));

/* ---------- 2. every nav data-view resolves to a real view section ---------- */
const views = [...html.matchAll(/<section class="view[^"]*" id="view-([^"]+)"/g)].map((m) => m[1]);
const tabs = [...html.matchAll(/<button class="tab[^"]*" data-view="([^"]+)"/g)].map((m) => m[1]);
const subtabs = [...html.matchAll(/<button class="subtab[^"]*" data-view="([^"]+)"/g)].map((m) => m[1]);
check(views.length >= 6, 'all six views still present (' + views.join(',') + ')');
check(tabs.length === 4, 'primary navigation reduced to 4 destinations (' + tabs.join(',') + ')');
check(tabs.every((v) => views.includes(v)), 'every primary tab points at an existing view');
check(subtabs.length >= 3, 'sub-navigation present (' + subtabs.join(',') + ')');
check([...tabs, ...subtabs].every((v) => views.includes(v)), 'every sub-tab points at an existing view');
const routedViews = [...new Set([...tabs, ...subtabs])].sort().join(',');
check(routedViews === [...views].sort().join(','), 'every view is reachable from the navigation (' + routedViews + ')');

/* ---------- 3. view router ---------- */
check(/function showView\(v\)/.test(html), 'showView(view) router exists');
check(/window\.showView\s*=\s*showView/.test(html), 'router is exposed for other modules');
const mapBlock = (html.match(/const VIEW_TAB=\{([^}]*)\}/) || [])[1] || '';
const mapped = [...mapBlock.matchAll(/(\w+):'(\w+)'/g)];
check(mapped.length >= 6, 'VIEW_TAB maps every view to a primary tab');
check(mapped.every(([, view]) => views.includes(view)), 'VIEW_TAB keys are real views');
check(mapped.every(([, , tab]) => tabs.includes(tab)), 'VIEW_TAB targets are real tabs');
check(!/querySelectorAll\('\.tab'\)\.forEach\(x=>x\.classList\.toggle\('active',x===b\)\)/.test(html),
  'old ad-hoc tab handler removed');
check(!/querySelector\('\.tab\[data-view="schedule"\]'\)/.test(html),
  'no code still labels the removed schedule tab');
check(!/querySelector\('\.tab\[data-view="pet"\]'\)/.test(html),
  'no code still clicks the removed pet tab');

/* ---------- 4. sync status clarity ---------- */
const statusEl = (html.match(/<div id="accountStatus"[^>]*>/) || [''])[0];
check(/role="status"/.test(statusEl), 'sync status bar is an ARIA status region');
check(/aria-live="polite"/.test(statusEl), 'sync status bar is announced politely');
check(/<span id="statusText">/.test(html), 'status text has its own node (dot can stay decorative)');
check(/id="statusRetry"/.test(html), 'manual "retry sync" control exists');
check(/function lastSyncText\(\)/.test(html), 'last-successful-sync timestamp is rendered');
check(/function markSynced\(\)/.test(html), 'successful syncs record a timestamp');
check(/markSynced\(\);/.test((html.match(/cloudState='synced';retryN=0;/) || [''])[0] + ';') ||
  /cloudState='synced';retryN=0;markSynced\(\)/.test(html), 'push success marks the sync time');
check(/classList\.add\(tone\)|classList\.remove\('ok','warn','bad'\)/.test(html), 'status bar shifts tone by sync state');
check(/statusRetryBtn\.onclick/.test(html), 'retry button is wired to the sync path');

/* ---------- 5. accessibility hooks ---------- */
check(/<nav class="tabs" aria-label=/.test(html), 'main navigation has an accessible name');
check(/class="sr-only" role="status" aria-live="polite"/.test(html), 'screen-reader live region exists');
check(/function announce\(msg\)/.test(html), 'announce() helper exists');
check(/announce\(\(e\.title\|\|''\)/.test(html), 'task completion is announced, not just visual');
check(/role="status" aria-live="polite" aria-atomic="true"/.test(html), 'toasts are announced');
check(/\.btn:focus-visible/.test(html), 'visible focus ring is styled');
check(/role="group" aria-label="Plan sections"/.test(html), 'Plan sub-navigation is a labelled group');
check(/aria-pressed/.test(html), 'sub-tabs expose their pressed state');

/* ---------- 6. optional onboarding ---------- */
check(/function setObLater\(\)/.test(html), 'onboarding can be dismissed permanently');
check(/lvlby-ob-later/.test(html), 'dismissal is persisted');
check(/Show me around/.test(html), 'onboarding offers the tour instead of forcing it');
check(/id="setTour"/.test(html), 'tour stays replayable from Settings');

/* ---------- 7. data safety ---------- */
check(/confirm\(tr\('uncheckConfirm'\)\)/.test(html), '"uncheck all" asks before clearing the day');
check(/LS=\{[^}]*lastsync:'lvlby-lastsync'/.test(html), 'sync timestamp uses its own storage key');
check(/bak:'lvlby-device-backup'/.test(html), 'device backup key unchanged (existing backups still load)');
check(/data:'lvlby-data'/.test(html), 'main data key unchanged (no data migration)');

/* ---------- 8. i18n parity for keys added by this change ---------- */
for (const key of ['tabPlan', 'tabProgress', 'restoreCopy', 'confirmRestore', 'uncheckConfirm']) {
  const en = new RegExp('I\\.en\\.' + key + '=').test(html);
  const fa = new RegExp('I\\.fa\\.' + key + '=').test(html);
  check(en && fa, 'i18n key ' + key + ' exists in both en and fa');
}

/* ---------- 9. every inline script still parses ---------- */
const scripts = [...html.matchAll(/<script(?![^>]*\bsrc=)[^>]*>([\s\S]*?)<\/script>/g)].map((m) => m[1]);
check(scripts.length > 0, 'inline scripts found (' + scripts.length + ')');
scripts.forEach((code, i) => {
  const file = path.join(os.tmpdir(), 'lvlby-inline-' + i + '.js');
  fs.writeFileSync(file, code);
  try {
    execFileSync(process.execPath, ['--check', file], { stdio: 'pipe' });
    pass('inline script #' + i + ' parses (' + code.length + ' bytes)');
  } catch (e) {
    fail('inline script #' + i + ' has a syntax error: ' + String(e.stderr || e.message).split('\n').slice(0, 4).join(' '));
  }
});
try {
  execFileSync(process.execPath, ['--check', path.join(root, 'sw.js')], { stdio: 'pipe' });
  pass('service worker parses');
} catch (e) {
  fail('service worker syntax error: ' + String(e.stderr || e.message).split('\n')[0]);
}

/* ---------- 10. service worker cache + precached assets ---------- */
const cache = (sw.match(/const CACHE='([^']+)'/) || [])[1] || '';
check(cache && cache !== 'lvlby-v17-bar', 'service worker cache name bumped (' + cache + ')');
const assets = (sw.match(/const ASSETS=\[([\s\S]*?)\]/) || [])[1] || '';
const assetPaths = [...assets.matchAll(/'([^']+)'/g)].map((m) => m[1]).filter((p) => p !== './');
const missingAssets = assetPaths.filter((p) => !fs.existsSync(path.join(root, p)));
check(missingAssets.length === 0, 'all precached assets exist' + (missingAssets.length ? ' -> missing ' + missingAssets.join(', ') : ''));

console.log('\n' + (failures ? failures + ' check(s) failed' : 'all checks passed'));
process.exit(failures ? 1 : 0);

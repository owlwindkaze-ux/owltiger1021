/* どの画面からでも、いつでも 戻れるようにする小さな部品（SPEC 2.6-z56）。
 *
 * **なぜ要るか**
 * 持ち主から「**各画面からの戻るボタンがない**」。調べたら そのとおりだった。
 * 「☰ メニュー」は どの画面にもあるが、**いちばん上にあって、
 * 下へスクロールすると消える**。固定しているのは `moshi/` だけだった。
 *
 *   文型一覧   66,901px  …… スマホで85画面ぶん 上に戻らないと メニューに行けない
 *   聴解       62,153px
 *   漢字一覧   11,218px
 *
 * 13画面のうち12画面で、**下まで行くと 戻る手段が 画面から消えていた。**
 *
 * **置き場所は 実行時に よける。**
 * 上に固定タブのある画面（漢字・文型・読解）、下に固定バーのある画面
 * （100日コース・N2）があるので、決め打ちにすると必ずどれかに重なる。
 * **その場で測って、下の固定物の上に出す。**
 *
 * **行き先は その画面が元から持っているリンクを使う。**
 * 「☰ メニュー」なら入口へ、「☰ 職員用」なら職員用へ。
 * 画面ごとの親を勝手に変えない。
 *
 * 各画面に1行入れるだけ：
 *   <script src="back.js" defer></script>        … 入口と同じ階層の画面
 *   <script src="../back.js" defer></script>     … フォルダの中の画面
 */
(function () {
  'use strict';
  if (window.__backBtn) return;
  window.__backBtn = 1;

  /** その画面が元から持っている「戻る」リンクを探す */
  function findHome() {
    var as = document.querySelectorAll('a[href]');
    for (var i = 0; i < as.length; i++) {
      var a = as[i];
      var t = (a.textContent || '').replace(/\s+/g, ' ').trim();
      var h = a.getAttribute('href') || '';
      if (!h || h.charAt(0) === '#') continue;
      /* ☰ や ← で始まる、ページの親へ戻るリンク */
      if (/^[☰←]/.test(t) && /(index\.html|\.\.\/|^\.\.$)/.test(h)) {
        return { href: h, text: t };
      }
    }
    /* 見つからなければ 入口へ。フォルダの中かどうかで 道を変える */
    var deep = location.pathname.replace(/\/[^/]*$/, '/').split('/')
                 .filter(Boolean).length;
    return { href: (deep > 1 ? '../' : '') + 'index.html', text: '☰ メニュー' };
  }

  /** 下にある固定のものの高さ（100日コースやN2のバー）を測る */
  function bottomGuard() {
    var g = 0, all = document.body.getElementsByTagName('*');
    for (var i = 0; i < all.length; i++) {
      var e = all[i];
      if (e === btn) continue;
      var s;
      try { s = getComputedStyle(e); } catch (x) { continue; }
      if (s.position !== 'fixed') continue;
      var r = e.getBoundingClientRect();
      if (!r.width || !r.height) continue;
      /* 画面の下にくっついているものだけ */
      if (r.bottom >= innerHeight - 2 && r.top > innerHeight * 0.4) {
        g = Math.max(g, r.height);
      }
    }
    return g;
  }

  var home = findHome();
  var btn = document.createElement('a');
  btn.href = home.href;
  btn.id = 'backBtn';
  btn.textContent = home.text.length > 12 ? '☰ もどる' : home.text;
  btn.setAttribute('aria-label', 'もどる ／ Kembali');
  btn.style.cssText = [
    'position:fixed', 'left:12px', 'z-index:9998',
    'display:none', 'align-items:center', 'gap:6px',
    'background:rgba(22,33,43,.92)', 'color:#fff', 'text-decoration:none',
    'font-size:13px', 'font-weight:700', 'line-height:1',
    'padding:11px 15px', 'border-radius:999px',
    'box-shadow:0 2px 10px rgba(0,0,0,.3)',
    '-webkit-tap-highlight-color:transparent'
  ].join(';') + ';';

  function place() {
    btn.style.bottom = (14 + bottomGuard()) + 'px';
  }

  var on = false;
  function tick() {
    /* 上のほうでは 画面の見出しに「☰ メニュー」が出ているので 要らない */
    var want = (window.pageYOffset || document.documentElement.scrollTop) > 200;
    if (want === on) return;
    on = want;
    if (want) { place(); btn.style.display = 'inline-flex'; }
    else btn.style.display = 'none';
  }

  function start() {
    if (!document.body) return;
    document.body.appendChild(btn);
    addEventListener('scroll', tick, { passive: true });
    addEventListener('resize', function () { place(); }, { passive: true });
    tick();
  }
  if (document.readyState === 'loading')
    document.addEventListener('DOMContentLoaded', start);
  else start();
})();

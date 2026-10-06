// myfirstaigent: 지금 탭이 보이게 · 복사 버튼 · 영상 누르면 재생
(function () {
  var on = document.querySelector('.tab.on');
  if (on) on.parentNode.scrollLeft = on.offsetLeft - on.parentNode.clientWidth / 2 + on.clientWidth / 2;

  var toast = document.getElementById('toast');
  function say(m) {
    if (!toast) return;
    toast.textContent = m; toast.classList.add('on');
    clearTimeout(say.t); say.t = setTimeout(function () { toast.classList.remove('on'); }, 1600);
  }
  function fallback(text) {
    var ta = document.createElement('textarea');
    ta.value = text; ta.setAttribute('readonly', '');
    ta.style.position = 'fixed'; ta.style.top = '0'; ta.style.opacity = '0';
    document.body.appendChild(ta); ta.select();
    var ok = false;
    try { ok = document.execCommand('copy'); } catch (e) {}
    document.body.removeChild(ta);
    return ok;
  }
  function copy(text, btn) {
    function done() {
      var prev = btn.getAttribute('data-label') || btn.textContent;
      btn.setAttribute('data-label', prev);
      btn.classList.add('copied'); btn.textContent = '복사됨';
      say('복사했어요! 입력창에 Ctrl+V');
      setTimeout(function () { btn.classList.remove('copied'); btn.textContent = prev; }, 1400);
    }
    function fail() { if (fallback(text)) done(); else say('복사가 막혔어요. 글을 끌어 선택해 Ctrl+C'); }
    if (navigator.clipboard && window.isSecureContext) navigator.clipboard.writeText(text).then(done, fail);
    else fail();
  }
  document.addEventListener('click', function (e) {
    var btn = e.target.closest('.prompt-copy, [data-copy]');
    if (!btn) return;
    var text = btn.getAttribute('data-copy');
    if (!text) {
      var row = btn.closest('.prompt-row');
      text = row ? row.querySelector('.ptext').textContent.trim() : '';
    }
    if (text) copy(text, btn);
  });

  document.querySelectorAll('.yt-lazy').forEach(function (b) {
    b.addEventListener('click', function () {
      var f = document.createElement('iframe');
      f.src = b.getAttribute('data-src');
      f.title = b.getAttribute('aria-label') || '영상';
      f.allow = 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share';
      f.referrerPolicy = 'strict-origin-when-cross-origin';
      f.allowFullscreen = true;
      var box = document.createElement('div');
      box.className = b.className.replace('yt-lazy', '').trim();
      box.appendChild(f);
      b.parentNode.replaceChild(box, b);
    });
  });
})();

// 주소 · QR 크게 보기
(function () {
  var box = document.getElementById('addr');
  if (!box) return;
  function open() { box.hidden = false; }
  function close() { box.hidden = true; }
  document.querySelectorAll('.addr-open').forEach(function (b) { b.addEventListener('click', open); });
  box.querySelector('.addr-x').addEventListener('click', close);
  box.addEventListener('click', function (e) { if (e.target === box) close(); });
  addEventListener('keydown', function (e) { if (e.key === 'Escape') close(); });
})();

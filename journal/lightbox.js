const pictures = document.querySelectorAll('.body img');
if (pictures.length) {
  const dialog = document.createElement('dialog');
  dialog.setAttribute('aria-label', '이미지 확대');
  const close = document.createElement('button'); close.textContent = '닫기';
  const full = document.createElement('img');
  dialog.append(close, full); document.body.append(dialog);
  close.addEventListener('click', () => dialog.close());
  dialog.addEventListener('click', e => { if (e.target === dialog) dialog.close(); });
  pictures.forEach(pic => {
    pic.tabIndex = 0; pic.setAttribute('role', 'button');
    pic.setAttribute('aria-label', (pic.alt || '본문 이미지') + ' 확대');
    const open = e => { e.preventDefault(); full.src = pic.src; full.alt = pic.alt; full.referrerPolicy = 'no-referrer'; dialog.showModal(); };
    pic.addEventListener('click', open);
    pic.addEventListener('keydown', e => { if (e.key === 'Enter' || e.key === ' ') open(e); });
  });
}

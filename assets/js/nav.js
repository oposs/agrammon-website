// Mobile menu: the button in the header bar opens/closes the main nav.
(function () {
  var bar = document.querySelector('header.bar');
  var btn = bar && bar.querySelector('.menu-btn');
  if (!btn) return;

  function setOpen(open) {
    bar.classList.toggle('open', open);
    btn.setAttribute('aria-expanded', open ? 'true' : 'false');
  }

  btn.addEventListener('click', function () {
    setOpen(!bar.classList.contains('open'));
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && bar.classList.contains('open')) {
      setOpen(false);
      btn.focus();
    }
  });
})();

const choices = document.querySelectorAll('[data-lang]');
function setLanguage(language) {
  const selected = language === 'zh' ? 'zh' : 'en';
  document.querySelectorAll('[data-language]').forEach(section => {
    section.hidden = section.dataset.language !== selected;
  });
  document.documentElement.lang = selected === 'zh' ? 'zh-CN' : 'en';
  choices.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.lang === selected)));
  try { localStorage.setItem('yan-site-language', selected); } catch {}
}
choices.forEach(button => button.addEventListener('click', () => setLanguage(button.dataset.lang)));
let preference = 'en';
try { preference = localStorage.getItem('yan-site-language') || 'en'; } catch {}
setLanguage(preference);

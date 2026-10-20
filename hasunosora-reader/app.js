const $ = (selector) => document.querySelector(selector);
const list = $('#story-list');
const content = $('#story-content');
const jump = $('#page-jump');
const sidebar = $('#sidebar');
let catalog = [];
let selected = null;
let readingMode = ['original', 'translation', 'parallel'].includes(localStorage.getItem('readingMode'))
  ? localStorage.getItem('readingMode') : 'parallel';

function setMode(mode) {
  readingMode = mode;
  localStorage.setItem('readingMode', mode);
  content.className = `story-content mode-${mode}`;
  document.querySelectorAll('[data-mode]').forEach(button => {
    button.setAttribute('aria-pressed', String(button.dataset.mode === mode));
  });
}

function closeLibrary() {
  sidebar.classList.remove('open');
  $('#mobile-library').setAttribute('aria-expanded', 'false');
  $('#mobile-backdrop').hidden = true;
}

function createPage(page) {
  const section = document.createElement('section');
  section.className = 'page-block';
  section.id = `page-${page.number}`;
  section.dataset.page = String(page.number);

  const heading = document.createElement('div');
  heading.className = 'page-heading';
  const pageNumber = document.createElement('span');
  pageNumber.textContent = `PAGE ${String(page.number).padStart(2, '0')}`;
  heading.append(pageNumber);
  section.append(heading);

  const grid = document.createElement('div');
  grid.className = 'page-grid';
  const original = document.createElement('div');
  original.className = 'original-column';
  const originalLabel = document.createElement('div');
  originalLabel.className = 'column-caption';
  originalLabel.innerHTML = '<span class="dot"></span> JAPANESE · 원문';
  const originalText = document.createElement('div');
  originalText.className = 'original-text';
  originalText.lang = 'ja';
  for (const block of page.originalParagraphs) {
    const element = document.createElement(block === '***' ? 'hr' : 'p');
    if (block !== '***') element.textContent = block;
    originalText.append(element);
  }
  original.append(originalLabel, originalText);

  const translated = document.createElement('div');
  translated.className = 'translated-column';
  const translatedLabel = document.createElement('div');
  translatedLabel.className = 'column-caption';
  translatedLabel.innerHTML = '<span class="dot"></span> KOREAN · 번역문';
  const prose = document.createElement('div');
  prose.className = 'translation-text';
  prose.lang = 'ko';
  for (const block of page.paragraphs) {
    const element = document.createElement(block === '***' ? 'hr' : 'p');
    if (block !== '***') element.textContent = block;
    prose.append(element);
  }
  translated.append(translatedLabel, prose);
  grid.append(original, translated);
  section.append(grid);
  return section;
}

async function openStory(entry, scroll = true) {
  selected = entry.id;
  list.querySelectorAll('button').forEach(button => {
    const active = button.dataset.story === entry.id;
    button.classList.toggle('active', active);
    button.setAttribute('aria-current', active ? 'true' : 'false');
  });
  try {
    const response = await fetch(entry.data);
    if (!response.ok) throw new Error('작품을 불러오지 못했습니다.');
    const story = await response.json();
    $('#intro-title').textContent = story.title;
    $('#story-title').textContent = story.title;
    $('#story-subtitle').textContent = `${entry.pages} · ${entry.status}`;
    $('#story-counter').textContent = `${String(catalog.indexOf(entry) + 1).padStart(2, '0')} / ${String(catalog.length).padStart(2, '0')}`;
    $('#page-total').textContent = `/ ${story.pageCount}쪽`;
    content.replaceChildren(...story.pages.map(page => createPage(page)));
    jump.replaceChildren(...story.pages.map(page => {
      const option = document.createElement('option');
      option.value = `page-${page.number}`;
      option.textContent = `${page.number}쪽`;
      return option;
    }));
    setMode(readingMode);
    const hashPage = Number(location.hash.replace('#page-', ''));
    if (story.pages.some(page => page.number === hashPage)) {
      jump.value = `page-${hashPage}`;
      requestAnimationFrame(() => document.getElementById(`page-${hashPage}`).scrollIntoView());
    } else if (scroll) {
      $('#reader-toolbar').scrollIntoView({behavior: 'smooth', block: 'start'});
    }
  } catch (error) {
    const message = document.createElement('p');
    message.className = 'error-card';
    message.textContent = `소설을 표시하지 못했습니다: ${error.message}`;
    content.replaceChildren(message);
  }
  closeLibrary();
}

function renderCatalog() {
  list.replaceChildren(...catalog.map((entry, index) => {
    const button = document.createElement('button');
    button.className = 'story-link';
    button.type = 'button';
    button.dataset.story = entry.id;
    const number = document.createElement('span');
    number.className = 'story-num';
    number.textContent = String(index + 1).padStart(2, '0');
    const info = document.createElement('span');
    const title = document.createElement('strong');
    title.textContent = entry.title;
    const details = document.createElement('small');
    details.textContent = `${entry.pages} · ${entry.status}`;
    info.append(title, details);
    button.append(number, info);
    button.addEventListener('click', () => openStory(entry));
    return button;
  }));
}

document.querySelectorAll('[data-mode]').forEach(button => button.addEventListener('click', () => setMode(button.dataset.mode)));
jump.addEventListener('change', () => {
  const page = document.getElementById(jump.value);
  if (page) { history.replaceState(null, '', `#${jump.value}`); page.scrollIntoView({behavior: 'smooth'}); }
});
$('#back-to-top').addEventListener('click', () => window.scrollTo({top: 0, behavior: 'smooth'}));
$('#mobile-library').addEventListener('click', () => {
  const open = sidebar.classList.toggle('open');
  $('#mobile-library').setAttribute('aria-expanded', String(open));
  $('#mobile-backdrop').hidden = !open;
});
$('#mobile-backdrop').addEventListener('click', closeLibrary);
document.addEventListener('keydown', event => { if (event.key === 'Escape') closeLibrary(); });

async function init() {
  try {
    const response = await fetch('data/library.json');
    if (!response.ok) throw new Error('목록을 불러오지 못했습니다.');
    catalog = (await response.json()).stories;
    renderCatalog();
    if (catalog.length) await openStory(catalog[0], false);
  } catch (error) {
    const message = document.createElement('p');
    message.className = 'error-card';
    message.textContent = `소설 목록을 표시하지 못했습니다: ${error.message}`;
    content.replaceChildren(message);
  }
}
init();

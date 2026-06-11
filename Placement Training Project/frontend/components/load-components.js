// Simple loader to include sidebar and navbar HTML
async function loadComponent(selector, path){
  const el = document.querySelector(selector);
  if(!el) return;
  try{
    const res = await fetch(path);
    const html = await res.text();
    el.innerHTML = html;
  }catch(e){
    console.error('Failed to load component', path, e);
  }
}

document.addEventListener('DOMContentLoaded', ()=>{
  loadComponent('#navbar-placeholder', 'components/navbar.html');
  loadComponent('#sidebar-placeholder', 'components/sidebar.html');
});
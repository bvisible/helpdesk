import{d as C,A as f,c as g,a4 as q,b0 as E,e as L,k as R}from"./index-f6c03390.js";const H=["srcdoc"],M=C({__name:"EmailContent",props:{content:{type:String,required:!0}},setup(b){const y=b,u=f(null),c=f(y.content),w=g(()=>{const e=document.querySelectorAll('link[rel="stylesheet"]');for(const o of e){const t=o.getAttribute("href");if(t?.includes("/assets/helpdesk/desk/")&&t.endsWith(".css"))return t}return"/assets/helpdesk/desk/index.css"}),l=new DOMParser().parseFromString(c.value,"text/html"),v=l.querySelectorAll("div.gmail_quote"),k=l.querySelectorAll("div#appendonsend"),x=l.querySelectorAll("p.reply-to-content");v.length?c.value=d(l,"div.gmail_quote",!0):k.length?c.value=d(l,"div#appendonsend"):x.length&&(c.value=d(l,"p.reply-to-content"));function d(e,o,t=!1){function s(r){const a=r.querySelectorAll(o);if(a.length===0)return;const n=a[0];A(n,t),s(r)}return s(e),e.body.innerHTML}function A(e,o){if(!e)return;const t=Math.random().toString(36).substring(2,7),s=l.createElement("div");s.classList.add("replied-content");const r=l.createElement("label");r.classList.add("collapse"),r.setAttribute("for",t),r.innerHTML="...",s.appendChild(r);const a=l.createElement("input");if(a.setAttribute("id",t),a.setAttribute("class","replyCollapser"),a.setAttribute("type","checkbox"),s.appendChild(a),o){const n=e.previousElementSibling;n&&n.tagName==="BR"&&n.remove();const i=e.cloneNode(!0);i.classList.remove("gmail_quote"),s.appendChild(i)}else{const n=Array.from(e.parentElement?.children||[]),i=n.indexOf(e),h=n.slice(i+1);if(h.length===0)return;const _=h.map(p=>p.cloneNode(!0)),m=l.createElement("div");m.append(..._),s.append(m);for(let p=i+1;p<n.length;p++)e.parentElement?.removeChild(n[p])}e.parentElement?.replaceChild(s,e)}const S=g(()=>`
  <!DOCTYPE html>
  <html>
  <head>
    <link rel="stylesheet" href="${w.value}" />
    <base target="_blank" />
    <style>
      :root {
        --bg-surface-gray-3: #ededed;
        --bg-surface-gray-4: #e2e2e2;
      }
      [data-theme='dark'] {
        --bg-surface-gray-3: #343434;
        --bg-surface-gray-4: #424242;
      }
      .replied-content .collapse {
        margin: 10px 0 10px 0;
        visibility: visible;
        cursor: pointer;
        display: flex;
        font-size: larger;
        font-weight: 700;
        height: 12px;
        line-height: 0.1;
        background: #e8eaed;
        width: 23px;
        justify-content: center;
        border-radius: 5px;
      }
      .replied-content .collapse:hover {
        background: #dadce0;
      }
      .replied-content .collapse + input {
        display: none;
      }
      .replied-content .collapse + input + div {
        display: none;
      }
      .replied-content .collapse + input:checked + div {
        display: block;
      }
      .email-content {
        word-break: break-word;
      }
      .email-content :is(:where(table):not(:where([class~='not-prose'], [class~='not-prose'] *))) {
        table-layout: auto;
      }
      .email-content :where(table):not(:where([class~='not-prose'], [class~='not-prose'] *)) {
        width: unset;
        table-layout: auto;
        text-align: unset;
        margin-top: unset;
        margin-bottom: unset;
        font-size: unset;
        line-height: unset;
      }
      .email-content :where(tbody tr):not(:where([class~='not-prose'], [class~='not-prose'] *)) {
        border-bottom-width: 0;
        border-bottom-color: transparent;
      }
      .email-content :is(:where(td):not(:where([class~='not-prose'], [class~='not-prose'] *))) {
        position: unset;
        border-width: 0;
        border-color: transparent;
        padding: 0;
      }
      .email-content :where(tbody td):not(:where([class~='not-prose'], [class~='not-prose'] *)) {
        vertical-align: revert;
      }
      .email-content :is(:where(img):not(:where([class~='not-prose'], [class~='not-prose'] *))) {
        border-width: 0;
      }
      .email-content :where(img):not(:where([class~='not-prose'], [class~='not-prose'] *)) {
        margin: 0;
      }
      .email-content :where(blockquote p:first-of-type):not(:where([class~='not-prose'], [class~='not-prose'] *))::before {
        content: none;
      }
      .email-content :where(blockquote p:last-of-type):not(:where([class~='not-prose'], [class~='not-prose'] *))::after {
        content: none;
      }
    </style>
  </head>
  <body>
    <div class="email-content prose-f">${c.value}</div>
  </body>
  </html>
  `);return q(u,e=>{e&&(e.onload=()=>{const o=e.contentWindow?.document.querySelector(".email-content");if(!o)return;const t=o.closest("html");if(!t)return;let s=document.documentElement.getAttribute("data-theme");t.setAttribute("data-theme",s);const r=E(c.value);r&&o.classList.add(r),e.style.height=t.offsetHeight+1+"px";const a=o.querySelectorAll(".replyCollapser");a.length&&a.forEach(n=>{n.addEventListener("change",()=>{e.style.height=t.offsetHeight+1+"px"})})})}),(e,o)=>(L(),R("iframe",{ref_key:"iframeRef",ref:u,srcdoc:S.value,class:"prose-f block h-10 max-h-[500px] w-full"},null,8,H))}});export{M as _};
//# sourceMappingURL=EmailContent.vue_vue_type_script_setup_true_lang-7e4e626a.js.map

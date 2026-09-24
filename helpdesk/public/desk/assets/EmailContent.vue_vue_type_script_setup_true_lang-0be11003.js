import{d as q,B as m,bd as L,c as y,q as g,Y as b,aO as K,e as R,s as D}from"./index-ca9c61e0.js";const H=["srcdoc"],F=q({__name:"EmailContent",props:{content:{type:String,required:!0}},setup(v){const k=v,p=m(null),c=m(L(k.content)),w=y(()=>{const e=document.querySelectorAll('link[rel="stylesheet"]');for(const n of e){const o=n.getAttribute("href");if(o?.includes("/assets/helpdesk/desk/")&&o.endsWith(".css"))return o}return"/assets/helpdesk/desk/index.css"}),s=new DOMParser().parseFromString(c.value,"text/html"),x=s.querySelectorAll("div.gmail_quote"),E=s.querySelectorAll("div#appendonsend"),A=s.querySelectorAll("p.reply-to-content");x.length?c.value=u(s,"div.gmail_quote",!0):E.length?c.value=u(s,"div#appendonsend"):A.length&&(c.value=u(s,"p.reply-to-content"));function u(e,n,o=!1){function l(r){const t=r.querySelectorAll(n);if(t.length===0)return;const a=t[0];C(a,o),l(r)}return l(e),e.body.innerHTML}function C(e,n){if(!e)return;const o=Math.random().toString(36).substring(2,7),l=s.createElement("div");l.classList.add("replied-content");const r=s.createElement("label");r.classList.add("collapse"),r.setAttribute("for",o),r.innerHTML="...",l.appendChild(r);const t=s.createElement("input");if(t.setAttribute("id",o),t.setAttribute("class","replyCollapser"),t.setAttribute("type","checkbox"),l.appendChild(t),n){const a=e.previousElementSibling;a&&a.tagName==="BR"&&a.remove();const i=e.cloneNode(!0);i.classList.remove("gmail_quote"),l.appendChild(i)}else{const a=Array.from(e.parentElement?.children||[]),i=a.indexOf(e),h=a.slice(i+1);if(h.length===0)return;const _=h.map(d=>d.cloneNode(!0)),f=s.createElement("div");f.append(..._),l.append(f);for(let d=i+1;d<a.length;d++)e.parentElement?.removeChild(a[d])}e.parentElement?.replaceChild(l,e)}const S=y(()=>`
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
  `);return g(p,e=>{e&&(e.onload=()=>{const n=e.contentWindow?.document.querySelector(".email-content");if(!n)return;const o=n.closest("html");if(!o)return;o.setAttribute("data-theme",b.value);const l=K(c.value);l&&n.classList.add(l),e.style.height=o.offsetHeight+1+"px",e.contentDocument?.addEventListener("pointerdown",()=>{document.dispatchEvent(new PointerEvent("pointerdown",{bubbles:!0}))}),e.contentDocument?.addEventListener("keydown",t=>{document.dispatchEvent(new KeyboardEvent("keydown",{key:t.key,code:t.code,ctrlKey:t.ctrlKey,metaKey:t.metaKey,shiftKey:t.shiftKey,altKey:t.altKey,bubbles:!0}))});const r=n.querySelectorAll(".replyCollapser");r.length&&r.forEach(t=>{t.addEventListener("change",()=>{e.style.height=o.offsetHeight+1+"px"})})})}),g(b,e=>{const n=p.value?.contentDocument?.documentElement;n&&n.setAttribute("data-theme",e)}),(e,n)=>(R(),D("iframe",{ref_key:"iframeRef",ref:p,srcdoc:S.value,class:"prose-f block h-10 max-h-[500px] w-full"},null,8,H))}});export{F as _};
//# sourceMappingURL=EmailContent.vue_vue_type_script_setup_true_lang-0be11003.js.map

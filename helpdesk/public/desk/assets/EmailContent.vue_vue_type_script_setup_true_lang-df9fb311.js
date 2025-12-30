import{d as L,A as y,c as w,a4 as R,aZ as H,e as F,k as I}from"./index-b4c863a6.js";const M=["srcdoc"],N=L({__name:"EmailContent",props:{content:{type:String,required:!0}},setup(v){const k=v,u=y(null),i=y(k.content),x=w(()=>{const e=document.querySelectorAll('link[rel="stylesheet"]');for(const o of e){const t=o.getAttribute("href");if(t!=null&&t.includes("/assets/helpdesk/desk/")&&t.endsWith(".css"))return t}return"/assets/helpdesk/desk/index.css"}),s=new DOMParser().parseFromString(i.value,"text/html"),S=s.querySelectorAll("div.gmail_quote"),_=s.querySelectorAll("div#appendonsend"),A=s.querySelectorAll("p.reply-to-content");S.length?i.value=h(s,"div.gmail_quote",!0):_.length?i.value=h(s,"div#appendonsend"):A.length&&(i.value=h(s,"p.reply-to-content"));function h(e,o,t=!1){function n(l){const r=l.querySelectorAll(o);if(r.length===0)return;const d=r[0];C(d,t),n(l)}return n(e),e.body.innerHTML}function C(e,o){var d,m,f;if(!e)return;const t=Math.random().toString(36).substring(2,7),n=s.createElement("div");n.classList.add("replied-content");const l=s.createElement("label");l.classList.add("collapse"),l.setAttribute("for",t),l.innerHTML="...",n.appendChild(l);const r=s.createElement("input");if(r.setAttribute("id",t),r.setAttribute("class","replyCollapser"),r.setAttribute("type","checkbox"),n.appendChild(r),o){const a=e.previousElementSibling;a&&a.tagName==="BR"&&a.remove();const c=e.cloneNode(!0);c.classList.remove("gmail_quote"),n.appendChild(c)}else{const a=Array.from(((d=e.parentElement)==null?void 0:d.children)||[]),c=a.indexOf(e),g=a.slice(c+1);if(g.length===0)return;const E=g.map(p=>p.cloneNode(!0)),b=s.createElement("div");b.append(...E),n.append(b);for(let p=c+1;p<a.length;p++)(m=e.parentElement)==null||m.removeChild(a[p])}(f=e.parentElement)==null||f.replaceChild(n,e)}const q=w(()=>`
  <!DOCTYPE html>
  <html>
  <head>
    <link rel="stylesheet" href="${x.value}" />
    <base target="_blank" />
    <style>
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
    <div class="email-content prose-f">${i.value}</div>
  </body>
  </html>
  `);return R(u,e=>{e&&(e.onload=()=>{var l;const o=(l=e.contentWindow)==null?void 0:l.document.querySelector(".email-content");if(!o)return;const t=o.closest("html");if(!t)return;o.classList.add(H(i.value)),e.style.height=t.offsetHeight+1+"px";const n=o.querySelectorAll(".replyCollapser");n.length&&n.forEach(r=>{r.addEventListener("change",()=>{e.style.height=t.offsetHeight+1+"px"})})})}),(e,o)=>(F(),I("iframe",{ref_key:"iframeRef",ref:u,srcdoc:q.value,class:"prose-f block h-10 max-h-[500px] w-full"},null,8,M))}});export{N as _};
//# sourceMappingURL=EmailContent.vue_vue_type_script_setup_true_lang-df9fb311.js.map

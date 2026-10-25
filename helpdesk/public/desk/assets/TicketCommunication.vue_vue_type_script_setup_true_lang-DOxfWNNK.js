import{d as T,y as S,w as q,c as C,h as _,a7 as x,a8 as I,o as b,a9 as z,a as f,f as g,u as p,A as B,T as M,aa as N,ab as P,l as O,t as j,ac as V,F as W,r as Y,x as G}from"./index-BojOVcTS.js";import{I as J}from"./dot-BrKa_Dhn.js";import{a as Q}from"./TypingIndicator.vue_vue_type_style_index_0_scoped_7f2c0ea9_lang-BdTebS6Y.js";import"./config-D7_NiEpW.js";import{_ as U}from"./globe-DGM3r3-9.js";import{s as L}from"./index-BGfANbQ4.js";const X=["srcdoc"],Z=T({__name:"EmailContent",props:{content:{type:String,required:!0}},setup(i){const y=i,d=S(null),c=S(y.content),v=_(()=>x.value==="dark"?z(c.value):c.value),w=_(()=>{const e=document.querySelectorAll('link[rel="stylesheet"]');for(const n of e){const o=n.getAttribute("href");if(o?.includes("/assets/helpdesk/desk/")&&o.endsWith(".css"))return o}return"/assets/helpdesk/desk/index.css"}),s=new DOMParser().parseFromString(c.value,"text/html"),K=s.querySelectorAll("div.gmail_quote"),D=s.querySelectorAll("div#appendonsend"),F=s.querySelectorAll("p.reply-to-content");if(s.body.children.length===0){const e=s.body.innerHTML.replace(/\n\n/g,`
`);c.value=`<div class="whitespace-pre-wrap">${e}</div>`}else K.length?c.value=k(s,"div.gmail_quote",!0):D.length?c.value=k(s,"div#appendonsend"):F.length&&(c.value=k(s,"p.reply-to-content"));function k(e,n,o=!1){function a(l){const t=l.querySelectorAll(n);if(t.length===0)return;const r=t[0];$(r,o),a(l)}return a(e),e.body.innerHTML}function $(e,n){if(!e)return;const o=Math.random().toString(36).substring(2,7),a=s.createElement("div");a.classList.add("replied-content");const l=s.createElement("label");l.classList.add("collapse"),l.setAttribute("for",o),l.innerHTML="...",a.appendChild(l);const t=s.createElement("input");if(t.setAttribute("id",o),t.setAttribute("class","replyCollapser"),t.setAttribute("type","checkbox"),a.appendChild(t),n){const r=e.previousElementSibling;r&&r.tagName==="BR"&&r.remove();const u=e.cloneNode(!0);u.classList.remove("gmail_quote"),a.appendChild(u)}else{const r=Array.from(e.parentElement?.children||[]),u=r.indexOf(e),A=r.slice(u+1);if(A.length===0)return;const R=A.map(m=>m.cloneNode(!0)),E=s.createElement("div");E.append(...R),a.append(E);for(let m=u+1;m<r.length;m++)e.parentElement?.removeChild(r[m])}e.parentElement?.replaceChild(a,e)}const H=_(()=>`
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
        color: #383838;
        background: #e8eaed;
        width: 23px;
        justify-content: center;
        border-radius: 5px;
      }
      .replied-content .collapse:hover {
        background: #dadce0;
      }
      [data-theme='dark'] .replied-content .collapse {
        color: #e2e2e2;
        background: #424242;
      }
      [data-theme='dark'] .replied-content .collapse:hover {
        background: #525252;
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
    <div class="email-content prose-f">${v.value}</div>
  </body>
  </html>
  `);return q(d,e=>{e&&(e.onload=()=>{const n=e.contentWindow?.document.querySelector(".email-content");if(!n)return;const o=n.closest("html");if(!o)return;o.setAttribute("data-theme",x.value);const a=I(c.value);a&&n.classList.add(a),e.style.height=o.offsetHeight+1+"px",e.contentDocument?.addEventListener("pointerdown",()=>{document.dispatchEvent(new PointerEvent("pointerdown",{bubbles:!0}))}),e.contentDocument?.addEventListener("keydown",t=>{document.dispatchEvent(new KeyboardEvent("keydown",{key:t.key,code:t.code,ctrlKey:t.ctrlKey,metaKey:t.metaKey,shiftKey:t.shiftKey,altKey:t.altKey,bubbles:!0}))});const l=n.querySelectorAll(".replyCollapser");l.length&&l.forEach(t=>{t.addEventListener("change",()=>{e.style.height=o.offsetHeight+1+"px"})})})}),q(x,e=>{const n=d.value?.contentDocument?.documentElement;n&&n.setAttribute("data-theme",e)}),(e,n)=>(b(),C("iframe",{ref_key:"iframeRef",ref:d,srcdoc:H.value,class:"prose-f block h-10 max-h-[500px] w-full"},null,8,X))}}),ee={class:"border flex-1 px-3 pt-2.5 mb-4 border-transparent bg-surface-base rounded-5 shadow text-base leading-6 transition-all duration-300 ease-in-out"},te={class:"mb-4 flex items-center justify-between text-base"},ne={class:"flex items-center gap-0.5"},oe={class:"text-ink-gray-5"},se={class:"flex flex-wrap gap-2 mb-2"},pe=T({__name:"TicketCommunication",props:{content:{},date:{},user:{},cc:{default:()=>""},bcc:{default:()=>""},attachments:{default:()=>[]}},setup(i){function y(d){return L(d,{allowedTags:L.defaults.allowedTags.concat(["img","video"]),allowedAttributes:{"*":["style","align","valign","width","height","bgcolor"],a:["href"],video:["src","controls"],img:["src"],table:["border","cellpadding","cellspacing","data-type"],td:["colspan","rowspan"],th:["colspan","rowspan"]}})}return(d,c)=>{const v=J,w=Z;return b(),C("div",ee,[f("div",te,[f("div",ne,[g(p(U),B(i.user,{size:"lg",expand:"",strong:"","hide-avatar":!0}),null,16),g(v,{class:"text-ink-gray-4 size-4"}),g(p(M),{text:p(N)(i.date,p(P))},{default:O(()=>[f("span",oe,j(p(V)(i.date)),1)]),_:1},8,["text"])])]),g(w,{content:y(i.content)},null,8,["content"]),f("div",se,[(b(!0),C(W,null,Y(i.attachments,h=>(b(),G(p(Q),{key:h.file_url,label:h.file_name,url:h.file_url},null,8,["label","url"]))),128))])])}}});export{pe as _};

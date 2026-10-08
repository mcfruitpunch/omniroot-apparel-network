"use strict";
const state = { me: null, catalog: null, profile: null, requests: [], designs: [] };
const $ = (q, root=document) => root.querySelector(q);
const $$ = (q, root=document) => [...root.querySelectorAll(q)];
const statusBox = $("#status");

function notify(message, error=false) {
  statusBox.textContent = message;
  statusBox.classList.toggle("error", error);
}
function text(tag, content, className) {
  const el = document.createElement(tag);
  el.textContent = content;
  if (className) el.className = className;
  return el;
}
function detail(error) {
  if (typeof error === "string") return error;
  if (error && typeof error === "object") {
    if (Array.isArray(error)) return error.map(item => item.msg || String(item)).join("; ");
    if (error.missing_measurements) return "Required measurements missing: " + error.missing_measurements.join(", ");
    return JSON.stringify(error);
  }
  return "Request could not be completed";
}
async function api(path, options={}) {
  const headers = { "Accept": "application/json", ...(options.headers || {}) };
  if (options.body !== undefined) headers["Content-Type"] = "application/json";
  if (state.me && !["GET", "HEAD"].includes(options.method || "GET")) headers["X-CSRF-Token"] = state.me.csrf_token;
  const response = await fetch("/api" + path, {credentials:"same-origin", ...options, headers});
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(detail(payload.detail || ("HTTP " + response.status)));
  return payload;
}
function show(view, options={}) {
  if (!state.me && ["fit","requests","designer"].includes(view)) {
    notify("Sign in or create an account before using this area.");
    view = "account";
  } else if (!options.keepStatus) notify("");
  $$(".view").forEach(el => { el.hidden = el.id !== view; });
  $$("[data-view]").forEach(el => {
    if (el.closest("nav")) {
      if (el.dataset.view === view) el.setAttribute("aria-current", "page");
      else el.removeAttribute("aria-current");
    }
  });
  if (view === "requests") loadRequests();
  if (view === "designer") loadDesigns();
  if (view === "fit") loadFit();
  if (view === "account") renderAccount();
  window.scrollTo({top:0,behavior:"instant"});
}
function renderAccount() {
  $("#signed-out").hidden = !!state.me;
  $("#signed-in").hidden = !state.me;
  if (state.me) $("#account-email").textContent = state.me.email;
}
function option(id, label) {
  const element = document.createElement("option");
  element.value = id;
  element.textContent = label;
  return element;
}
function renderCatalog() {
  const root = $("#garments");
  root.replaceChildren();
  state.catalog.garments.forEach((garment, index) => {
    const card = text("article", "", "catalog-card");
    const artwork = text("div", "", "garment-img" + (index === 1 ? " trouser" : ""));
    artwork.append(text("div", "RESEARCH DESIGN", "small-tag"), text("div", "", "garment-shape"));
    const body = text("div", "", "catalog-body");
    body.append(text("h3", garment.name), text("p", garment.description));
    const label = text("label", "Choose example fabric");
    const select = document.createElement("select");
    select.setAttribute("aria-label", "Fabric for " + garment.name);
    garment.fabric_ids.forEach(id => {
      const fabric = state.catalog.fabrics.find(item => item.id === id);
      if (fabric) select.append(option(fabric.id, fabric.name + " · Unverified sample"));
    });
    label.append(select);
    const required = text("p", "Required for this concept: " + garment.required_measurements.map(x => x.replace("_cm", "").replaceAll("_"," ")).join(", "), "subtle");
    const button = text("button", "Request a feasibility review →", "primary");
    button.type = "button";
    button.addEventListener("click", async () => {
      if (!state.me) return show("account", {keepStatus:true});
      button.disabled = true;
      try {
        const result = await api("/requests", { method:"POST", body:JSON.stringify({garment_id:garment.id,fabric_id:select.value}) });
        notify("Request " + result.id.slice(0,8) + " recorded. No purchase or production has been scheduled.");
        show("requests", {keepStatus:true});
      } catch (error) {
        notify(error.message, true);
        if (error.message.includes("measurements")) show("fit", {keepStatus:true});
      } finally { button.disabled = false; }
    });
    body.append(label, required, button);
    card.append(artwork, body);
    root.append(card);
  });
}
async function loadFit() {
  try {
    const result = await api("/fit-profile");
    state.profile = result.profile;
    const form = $("#fit-form");
    for (const key of ["chest_cm","waist_cm","hip_cm","inseam_cm"]) form.elements[key].value = result.profile?.measurements?.[key] ?? "";
    form.elements.method.value = result.profile?.method || "self_reported";
    form.elements.preference.value = result.profile?.preference || "regular";
    $("#fit-meta").textContent = result.profile ? "Saved revision " + result.profile.revision + " · This profile is private to your account." : "No profile saved yet.";
  } catch(e) { notify(e.message, true); }
}
async function loadRequests() {
  try {
    const data = await api("/requests");
    state.requests = data.requests;
    const root = $("#request-list"); root.replaceChildren();
    for (const req of data.requests) {
      const garment = state.catalog.garments.find(g=>g.id===req.garment_id);
      const fabric = state.catalog.fabrics.find(f=>f.id===req.fabric_id);
      const card = text("article", "", "list-card");
      const left = text("div", "");
      left.append(text("h3", garment?.name || req.garment_id),
        text("p", (fabric?.name || req.fabric_id) + " · " + new Date(req.created_at*1000).toLocaleDateString()));
      const right = text("div", "");
      right.append(text("span", req.status.replaceAll("_"," "), "pill"));
      if (req.status === "awaiting_human_review") {
        const cancel = text("button", "Withdraw request", "secondary");
        cancel.type = "button";
        cancel.addEventListener("click", async () => {
          try { await api("/requests/" + encodeURIComponent(req.id) + "/withdraw", {method:"POST"}); await loadRequests(); notify("Request withdrawn."); }
          catch(e) { notify(e.message, true); }
        });
        right.append(document.createTextNode(" "), cancel);
      }
      card.append(left,right); root.append(card);
    }
  } catch(e) { notify(e.message, true); }
}
async function loadDesigns() {
  try {
    const data = await api("/designs");
    const root = $("#design-list"); root.replaceChildren();
    data.designs.forEach(item => {
      const card = text("article", "", "list-card");
      const left = text("div", "");
      left.append(text("h3",item.name),text("p",item.description));
      card.append(left, text("span",item.status.replaceAll("_"," "),"pill"));
      root.append(card);
    });
  } catch(e) { notify(e.message,true); }
}
async function signIn(form, endpoint) {
  const data = new FormData(form);
  try {
    state.me = await api(endpoint, { method:"POST", body:JSON.stringify({email:data.get("email"),password:data.get("password")}) });
    form.reset();
    renderAccount();
    notify("Welcome to your OmniRoot Apparel account.");
    show("fit", {keepStatus:true});
  } catch(e) { notify(e.message, true); }
}
function initEvents() {
  $$("[data-view]").forEach(button => button.addEventListener("click", () => show(button.dataset.view)));
  $("#register-form").addEventListener("submit", e => { e.preventDefault(); signIn(e.currentTarget,"/auth/register"); });
  $("#login-form").addEventListener("submit", e => { e.preventDefault(); signIn(e.currentTarget,"/auth/login"); });
  $("#fit-form").addEventListener("submit", async e => {
    e.preventDefault();
    const form = e.currentTarget;
    const measurements = {};
    for (const key of ["chest_cm","waist_cm","hip_cm","inseam_cm"]) {
      if (form.elements[key].value !== "") measurements[key] = Number(form.elements[key].value);
    }
    try {
      await api("/fit-profile",{method:"PUT",body:JSON.stringify({measurements,method:form.elements.method.value,preference:form.elements.preference.value})});
      await loadFit(); notify("Your private Fit Passport was updated.");
    } catch(error) {notify(error.message,true);}
  });
  $("#delete-fit").addEventListener("click", async () => {
    if (!confirm("Delete your Fit Passport measurements?")) return;
    try { await api("/fit-profile",{method:"DELETE"}); await loadFit(); notify("Profile deleted."); }
    catch(e){notify(e.message,true);}
  });
  $("#designer-form").addEventListener("submit", async e => {
    e.preventDefault(); const form = e.currentTarget; const data = new FormData(form);
    try {
      await api("/designs",{method:"POST",body:JSON.stringify({name:data.get("name"),description:data.get("description"),rights_confirmed:!!data.get("rights_confirmed")})});
      form.reset(); await loadDesigns(); notify("Design concept submitted for a future technical review.");
    } catch(error) {notify(error.message,true);}
  });
  $("#logout").addEventListener("click", async () => {
    try { await api("/auth/logout",{method:"POST"}); state.me = null; state.profile = null; renderAccount(); notify("Signed out."); show("shop",{keepStatus:true}); }
    catch(e) {notify(e.message,true);}
  });
  $("#export-data").addEventListener("click", async () => {
    try {
      const payload = await api("/export");
      const file = new Blob([JSON.stringify(payload,null,2)],{type:"application/json"});
      const url = URL.createObjectURL(file);
      const link = document.createElement("a"); link.href=url; link.download="omniroot-account-export.json"; link.click();
      URL.revokeObjectURL(url);
      notify("Your data export has been prepared.");
    } catch(e){notify(e.message,true);}
  });
  $("#delete-account-form").addEventListener("submit", async e => {
    e.preventDefault();
    if (!confirm("Permanently delete your account and its saved records? This cannot be undone.")) return;
    try {
      await api("/account",{method:"DELETE",body:JSON.stringify({password:e.currentTarget.elements.password.value})});
      state.me=null; state.profile=null; renderAccount(); e.currentTarget.reset();
      notify("Account deleted from the application database.");
      show("shop",{keepStatus:true});
    } catch(error){notify(error.message,true);}
  });
}
async function main() {
  initEvents();
  try {
    state.catalog = await api("/catalog");
    renderCatalog();
    try { state.me = await api("/me"); } catch(e) {state.me = null;}
    renderAccount();
    show("shop");
  } catch(e) {
    notify("The platform API is unavailable. Start the Python server before using this site. " + e.message,true);
  }
}
main();

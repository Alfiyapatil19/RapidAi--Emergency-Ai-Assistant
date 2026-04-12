/**
 * RapidAid - API Helper
 * Wraps all fetch calls to the Flask backend.
 */

const API = {

  async post(url, body) {
    const res = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    return res.json();
  },

  async get(url) {
    const res = await fetch(url);
    return res.json();
  },

  async del(url) {
    const res = await fetch(url, { method: "DELETE" });
    return res.json();
  },

  // ─── AUTH ──────────────────────────────────────────────
  login:    (email, password) => API.post("/auth/login",    { email, password }),
  register: (name, email, password) => API.post("/auth/register", { name, email, password }),
  logout:   ()                => API.post("/auth/logout",   {}),
  me:       ()                => API.get("/auth/me"),

  // ─── FIRST AID ─────────────────────────────────────────
  getFirstAid: (lang, type) => API.get(`/firstaid/${lang}/${type}`),

  // ─── CONTACTS ──────────────────────────────────────────
  getContacts:    ()                        => API.get("/contacts/"),
  addContact:     (name, relation, phone)   => API.post("/contacts/add", { name, relation, phone }),
  deleteContact:  (id)                      => API.del(`/contacts/delete/${id}`),

  // ─── HISTORY ───────────────────────────────────────────
  getHistory:   () => API.get("/history/"),
  clearHistory: () => API.del("/history/clear"),

  // ─── PANIC ─────────────────────────────────────────────
  panic: () => API.post("/panic", {}),

  // ─── AI GUIDE ──────────────────────────────────────────
  aiGuide: (emergency, lang, context = "") =>
    API.post("/ai/guide", { emergency, lang, context }),
};

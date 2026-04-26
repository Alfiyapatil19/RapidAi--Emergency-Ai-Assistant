/**
 * RapidAid — Main Application JS
 * - Real Claude AI first aid guidance
 * - Real SMS panic notifications via Fast2SMS
 * - AI chat for follow-up questions
 */

// ── STATE ─────────────────────────────────────────────────
const state = {
  user:        window.RAPIDAID_USER || null,
  lang:        "en",
  contacts:    [],
  history:     [],
  currentType: "burns",
  aiAvailable: false,
};

// ── FIRST AID BUILT-IN DATA (fallback when AI unavailable) ─
const FA_DATA = {
  en: {
    burns:    { title:"Burns First Aid",        warning:"Seek immediate medical help for large, deep, or facial burns.", steps:[{t:"Cool the burn",d:"Hold under cool running water 10–20 minutes."},{t:"Remove constrictions",d:"Remove rings/watches before swelling starts."},{t:"Do NOT use ice or butter",d:"Never apply ice, butter, or toothpaste."},{t:"Cover the burn",d:"Cover loosely with a sterile dressing."},{t:"Manage pain",d:"Take paracetamol or ibuprofen if needed."},{t:"Call 108 if severe",d:"Call for burns larger than a palm or on face/hands."}]},
    bleeding: { title:"Bleeding First Aid",     warning:"If bleeding doesn't stop in 10 minutes, call 108 immediately.", steps:[{t:"Apply direct pressure",d:"Press firmly with a clean cloth on the wound."},{t:"Maintain pressure",d:"Keep pressing 10+ minutes without lifting."},{t:"Elevate the area",d:"Raise injured part above heart level."},{t:"Secure the dressing",d:"Bandage when bleeding slows."},{t:"Watch for shock",d:"Pale/cold/confused? Lay flat and raise legs."},{t:"Seek medical help",d:"Deep or non-stopping wounds need professional care."}]},
    fracture: { title:"Fracture First Aid",     warning:"Do not realign the bone. Call 108 for spine/hip fractures.", steps:[{t:"Stop bleeding",d:"Apply gentle pressure around open fractures."},{t:"Immobilize the injury",d:"Splint with padding and rigid support — do not move."},{t:"Apply ice pack",d:"Wrap ice in cloth, apply to reduce swelling."},{t:"Treat for shock",d:"Keep patient warm and calm."},{t:"No food or water",d:"Patient may need surgery."},{t:"Call 108",d:"For spine, hip, or pelvis fractures."}]},
    choking:  { title:"Choking First Aid",      warning:"If person becomes unconscious, start CPR and call 108.", steps:[{t:"Encourage coughing",d:"If they can speak/cough, encourage forceful coughing."},{t:"5 back blows",d:"Lean forward, 5 firm blows between shoulder blades."},{t:"5 abdominal thrusts",d:"Fist above navel, pull sharply inward and upward x5."},{t:"Alternate & repeat",d:"5 back blows + 5 thrusts until object expelled."},{t:"For infants",d:"5 back blows + 5 chest thrusts (not abdominal)."},{t:"Call 108",d:"If choking continues or person loses consciousness."}]},
    heart:    { title:"Heart Attack First Aid", warning:"Call 108 immediately — every second counts.", steps:[{t:"Call 108 now",d:"Don't drive yourself. Say 'possible heart attack'."},{t:"Help them sit/lie",d:"Loosen tight clothing around neck and chest."},{t:"Give aspirin",d:"325mg aspirin chewed if not allergic and conscious."},{t:"Monitor breathing",d:"Stay with person; prepare for CPR if needed."},{t:"Start CPR",d:"No pulse: 30 compressions + 2 rescue breaths. Repeat."},{t:"Use AED",d:"Defibrillators are in many public places — use if available."}]},
    drowning: { title:"Drowning First Aid",     warning:"Call 108 immediately. Drowning can be silent.", steps:[{t:"Your safety first",d:"Don't jump in unless trained. Throw rope or ring."},{t:"Get to safety",d:"Bring to land. Support head and neck at all times."},{t:"Call 108",d:"Call even if person seems okay."},{t:"Check breathing",d:"If unresponsive, check breathing. Don't waste time draining water."},{t:"Rescue breathing",d:"5 initial rescue breaths if not breathing."},{t:"Continue CPR",d:"30 compressions + 2 breaths until help arrives."}]},
  },
  hi: {
    burns:    { title:"जलन के लिए प्राथमिक उपचार",        warning:"बड़ी जलन के लिए तुरंत चिकित्सा लें।",  steps:[{t:"ठंडा पानी",d:"10-20 मिनट ठंडे पानी में रखें।"},{t:"वस्तुएं हटाएं",d:"अंगूठी/घड़ी हटाएं।"},{t:"बर्फ न लगाएं",d:"बर्फ या मक्खन न लगाएं।"},{t:"ढकें",d:"साफ पट्टी से ढकें।"},{t:"दर्द प्रबंधन",d:"पेरासिटामॉल लें।"},{t:"108 कॉल करें",d:"बड़ी जलन पर 108 कॉल करें।"}]},
    bleeding: { title:"रक्तस्राव के लिए प्राथमिक उपचार",  warning:"10 मिनट में न रुके तो 108 कॉल करें।", steps:[{t:"दबाव डालें",d:"साफ कपड़े से मजबूती से दबाएं।"},{t:"दबाव बनाए रखें",d:"10 मिनट तक न हटाएं।"},{t:"हिस्सा उठाएं",d:"हृदय से ऊंचा रखें।"},{t:"पट्टी",d:"बैंडेज से सुरक्षित करें।"},{t:"सदमा",d:"पीला हो तो लेटाएं।"},{t:"डॉक्टर",d:"गहरे घाव पर डॉक्टर।"}]},
    fracture: { title:"फ्रैक्चर के लिए प्राथमिक उपचार",  warning:"हड्डी सीधी न करें।",                  steps:[{t:"रक्तस्राव",d:"खुले में दबाएं।"},{t:"स्थिर करें",d:"स्प्लिंट लगाएं।"},{t:"बर्फ",d:"कपड़े में लपेटकर।"},{t:"सदमा",d:"गर्म रखें।"},{t:"खाना नहीं",d:"सर्जरी हो सकती है।"},{t:"108",d:"रीढ़ फ्रैक्चर पर 108।"}]},
    choking:  { title:"गले में अटकने पर",                   warning:"बेहोश हो तो CPR और 108।",             steps:[{t:"खांसें",d:"बोल सकते हैं तो जोर से खांसें।"},{t:"थपकी",d:"कंधों के बीच 5 थपकी।"},{t:"हेम्लिच",d:"नाभि के ऊपर 5 बार दबाएं।"},{t:"दोहराएं",d:"5+5 दोहराएं।"},{t:"शिशु",d:"छाती दबाव करें।"},{t:"108",d:"जारी रहे तो 108।"}]},
    heart:    { title:"दिल के दौरे के लिए",                  warning:"तुरंत 108 कॉल करें।",                 steps:[{t:"108 कॉल",d:"तुरंत कॉल करें।"},{t:"आरामदायक",d:"कपड़े ढीले करें।"},{t:"एस्पिरिन",d:"325mg चबाकर दें।"},{t:"सांस",d:"सांस रुके तो CPR।"},{t:"CPR",d:"30+2 दोहराएं।"},{t:"AED",d:"उपलब्ध हो तो प्रयोग करें।"}]},
    drowning: { title:"डूबने पर प्राथमिक उपचार",            warning:"तुरंत 108 कॉल करें।",                 steps:[{t:"सुरक्षा",d:"प्रशिक्षित न हों तो न कूदें।"},{t:"बाहर लाएं",d:"जमीन पर लाएं।"},{t:"108",d:"तुरंत कॉल करें।"},{t:"होश",d:"सांस जांचें।"},{t:"सांस दें",d:"5 बचाव सांसें।"},{t:"CPR",d:"मदत आने तक।"}]},
  },
  mr: {
    burns:    { title:"जळण्यासाठी प्रथमोपचार",   warning:"मोठ्या जळण्यासाठी ताबडतोब मदत घ्या।", steps:[{t:"थंड पाणी",d:"10-20 मिनिटे ठेवा।"},{t:"वस्तू काढा",d:"अंगठी काढा।"},{t:"बर्फ नको",d:"बर्फ लावू नका।"},{t:"झाका",d:"स्वच्छ कापडाने।"},{t:"वेदना",d:"पॅरासिटामॉल घ्या।"},{t:"108",d:"मोठ्या जळण्यावर 108।"}]},
    bleeding: { title:"रक्तस्रावासाठी प्रथमोपचार", warning:"10 मिनिटांत थांबला नाही तर 108।",    steps:[{t:"दाब द्या",d:"घट्ट दाब द्या।"},{t:"ठेवा",d:"10 मिनिटे ठेवा।"},{t:"वर करा",d:"हृदयापेक्षा वर।"},{t:"पट्टी",d:"बँडेज करा।"},{t:"धक्का",d:"झोपवा।"},{t:"डॉक्टर",d:"खोल जखमांसाठी।"}]},
    fracture: { title:"फ्रॅक्चरसाठी प्रथमोपचार",  warning:"हाड सरळ करू नका।",                  steps:[{t:"रक्तस्राव",d:"दाब द्या।"},{t:"स्थिर",d:"स्प्लिंट करा।"},{t:"बर्फ",d:"कापडात गुंडाळा।"},{t:"धक्का",d:"उबदार ठेवा।"},{t:"काही नको",d:"शस्त्रक्रिया लागू शकते।"},{t:"108",d:"मणका फ्रॅक्चरवर।"}]},
    choking:  { title:"श्वास अडकल्यास",             warning:"बेशुद्ध झाल्यास CPR आणि 108।",       steps:[{t:"खोकणे",d:"जोरात खोकण्यास सांगा।"},{t:"थाप",d:"5 वेळा जोरात।"},{t:"हेम्लिच",d:"5 वेळा खेचा।"},{t:"आळीपाळीने",d:"5+5 करा।"},{t:"लहान मुले",d:"छातीचे दाब।"},{t:"108",d:"अडकत राहिल्यास।"}]},
    heart:    { title:"हृदयविकाराच्या झटक्यासाठी", warning:"ताबडतोब 108 वर कॉल करा।",            steps:[{t:"108 कॉल",d:"ताबडतोब।"},{t:"आरामदायक",d:"कपडे सैल करा।"},{t:"अॅस्पिरिन",d:"325mg चावून।"},{t:"श्वास",d:"थांबला तर CPR।"},{t:"CPR",d:"30+2 करत राहा।"},{t:"AED",d:"असल्यास वापरा।"}]},
    drowning: { title:"बुडण्यासाठी प्रथमोपचार",    warning:"ताबडतोब 108 वर कॉल करा।",            steps:[{t:"सुरक्षा",d:"पाण्यात उडी मारू नका।"},{t:"बाहेर",d:"जमिनीवर आणा।"},{t:"108",d:"ताबडतोब।"},{t:"शुद्धी",d:"श्वास तपासा।"},{t:"श्वास",d:"5 वेळा द्या।"},{t:"CPR",d:"मदत येईपर्यंत।"}]},
  },
};

// ── INIT ──────────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", async () => {
  if (state.user) renderUserLoggedIn(state.user);
  else showAuthButtons();
  await checkAIStatus();
  loadFirstAid("burns");
});

// ── CHECK AI STATUS ───────────────────────────────────────
async function checkAIStatus() {
  try {
    const data = await API.get("/ai/status");
    state.aiAvailable = data.available;
    // Update AI badge in UI
    const badge = document.querySelector(".ai-badge");
    if (badge) {
      if (state.aiAvailable) {
        badge.innerHTML = `<span class="ai-dot"></span>AI-Assisted (Gemini)`;
        badge.style.background = "rgba(34,214,122,0.1)";
        badge.style.color = "var(--green)";
      } else {
        badge.innerHTML = `<span class="ai-dot" style="background:#888;"></span>Built-in Data`;
        badge.style.background = "rgba(150,150,150,0.1)";
        badge.style.color = "#888";
      }
    }
  } catch {}
}

// ── NAVIGATION ────────────────────────────────────────────
const PAGE_TITLES = { dashboard:"Dashboard", firstaid:"First Aid Guide", contacts:"Emergency Contacts", history:"Aid History" };

function navTo(name) {
  if ((name === "contacts" || name === "history") && !state.user) {
    openModal("modal-login");
    showToast("🔒 Login required for this feature");
    return;
  }
  document.querySelectorAll(".page").forEach(p => p.classList.remove("active"));
  document.getElementById("page-" + name).classList.add("active");
  document.querySelectorAll(".nav-link").forEach(n => n.classList.remove("active"));
  const nl = document.getElementById("nav-" + name);
  if (nl) nl.classList.add("active");
  document.getElementById("topbar-title").textContent = PAGE_TITLES[name] || name;
  if (name === "contacts") renderContacts();
  if (name === "history")  renderHistory();
  if (window.innerWidth <= 700) closeSidebar();
}

function toggleSidebar() {
  const sb = document.getElementById("sidebar");
  const ov = document.getElementById("sidebar-overlay");
  const open = sb.classList.toggle("open");
  ov.classList.toggle("open", open);
}
function closeSidebar() {
  document.getElementById("sidebar").classList.remove("open");
  document.getElementById("sidebar-overlay").classList.remove("open");
}

// ── FIRST AID ─────────────────────────────────────────────
function openFirstAid(type) {
  navTo("firstaid");
  selectType(document.querySelector(`.ttab[data-type="${type}"]`), type);
}

function selectType(btn, type) {
  document.querySelectorAll(".ttab").forEach(b => b.classList.remove("active"));
  if (btn) btn.classList.add("active");
  state.currentType = type;
  loadFirstAid(type);
}

async function loadFirstAid(type) {
  document.getElementById("fa-title").textContent    = type.charAt(0).toUpperCase() + type.slice(1) + " First Aid";
  document.getElementById("fa-loading").style.display = "flex";
  document.getElementById("fa-warning").style.display = "none";
  document.getElementById("fa-steps").innerHTML = "";
  if (document.getElementById("fa-image-container")) {
    document.getElementById("fa-image-container").style.display = "none";
  }

  if (state.user) {
    addToHistory({ type, icon: getIcon(type), action:"Viewed first aid", lang:state.lang, time:"Just now" });
  }

  // ── TRY REAL CLAUDE AI FIRST ──────────────────────────
  if (state.aiAvailable) {
    try {
      const aiData = await API.post("/ai/guide", { emergency: type, lang: state.lang });
      if (aiData.success && aiData.steps && aiData.steps.length > 0) {
        document.getElementById("fa-loading").style.display = "none";
        document.getElementById("fa-title").textContent = aiData.title || type + " First Aid";
        renderSteps(aiData.steps.map(s => ({ t: s.title, d: s.detail })));
        
        // Handle Image
        const imgCont = document.getElementById("fa-image-container");
        const imgDoc = document.getElementById("fa-image");
        if (aiData.image_base64) {
          imgDoc.src = aiData.image_base64;
          imgCont.style.display = "flex";
        } else {
          imgCont.style.display = "none";
        }

        document.getElementById("fa-warning-text").textContent = aiData.warning;
        document.getElementById("fa-warning").style.display = "flex";
        showToast("✨ AI guidance loaded");
        return;
      }
    } catch (e) {
      console.warn("AI fetch failed, using built-in data:", e);
    }
  }

  // ── FALLBACK: Built-in data ───────────────────────────
  setTimeout(() => {
    const data = FA_DATA[state.lang]?.[type] || FA_DATA["en"][type];
    if (!data) return;
    document.getElementById("fa-loading").style.display = "none";
    document.getElementById("fa-title").textContent = data.title;
    renderSteps(data.steps);
    document.getElementById("fa-warning-text").textContent = data.warning;
    document.getElementById("fa-warning").style.display = "flex";
  }, 600);

  // Also try backend static data
  try {
    const backendData = await API.get(`/firstaid/${state.lang}/${type}`);
    if (backendData.success) {
      document.getElementById("fa-loading").style.display = "none";
      document.getElementById("fa-title").textContent = backendData.data.title;
      document.getElementById("fa-steps").innerHTML = "";
      renderSteps(backendData.data.steps.map(s => ({ t: s.title, d: s.detail })));
      document.getElementById("fa-warning-text").textContent = backendData.data.warning;
      document.getElementById("fa-warning").style.display = "flex";
    }
  } catch {}
}

function renderSteps(steps) {
  const list = document.getElementById("fa-steps");
  list.innerHTML = "";
  steps.forEach((step, i) => {
    const li = document.createElement("li");
    li.className = "fa-step-item";
    li.style.animationDelay = (i * 0.06) + "s";
    li.innerHTML = `
      <div class="fa-step-num">${i + 1}</div>
      <div class="fa-step-body">
        <div class="fa-step-title">${esc(step.t || step.title)}</div>
        <div class="fa-step-detail">${esc(step.d || step.detail)}</div>
      </div>`;
    list.appendChild(li);
  });
}

// ── AI CHAT ───────────────────────────────────────────────
function toggleAIChat() {
  const w = document.getElementById("chatbot-window");
  if (w) w.classList.toggle("open");
  // scroll to bottom inside
  const box = document.getElementById("ai-chat-box");
  if (box) box.scrollTop = box.scrollHeight;
}

function handleChatKey(e) {
  if (e.key === "Enter") {
    e.preventDefault();
    sendAIChat();
  }
}

async function sendAIChat() {
  const input = document.getElementById("ai-chat-input");
  const msg   = input?.value?.trim();
  if (!msg) return;

  if (!state.aiAvailable) {
    showToast("⚠️ AI not configured — add HF_TOKEN to .env");
    return;
  }

  input.value = "";
  appendChatMessage("user", msg);
  appendChatMessage("ai", "...", true);

  try {
    const data = await API.post("/ai/chat", {
      message: msg, emergency: state.currentType, lang: state.lang
    });
    removeTypingIndicator();
    if (data.success) {
      appendChatMessage("ai", data.response || "Here's the image you requested:", false, data.image_base64);
    } else appendChatMessage("ai", "Sorry, I couldn't process that. Please call 108 for emergencies.");
  } catch {
    removeTypingIndicator();
    appendChatMessage("ai", "Connection error. Please call 108 for emergencies.");
  }
}

function appendChatMessage(role, text, typing=false, image_base64=null) {
  const box = document.getElementById("ai-chat-box");
  if (!box) return;
  const div = document.createElement("div");
  div.className = `chat-msg ${role}${typing ? " typing" : ""}`;
  div.textContent = text;
  
  if (image_base64) {
    const img = document.createElement("img");
    img.src = image_base64;
    div.appendChild(img);
  }
  
  box.appendChild(div);
  box.scrollTop = box.scrollHeight;
}
function removeTypingIndicator() {
  const t = document.querySelector(".chat-msg.typing");
  if (t) t.remove();
}

// ── EMERGENCY CALL ────────────────────────────────────────
function makeCall(num) {
  window.location.href = "tel:" + num;
  showToast("📞 Calling " + num + "…");
}

// ── PANIC MODE ────────────────────────────────────────────
// ── SIREN ENGINE ──────────────────────────────────────────
let audioCtx = null;
let sirenOsc = null;
let sirenInterval = null;

window.startSiren = function(durationMs = 30000) {
  try {
    if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    if (audioCtx.state === "suspended") audioCtx.resume();
    window.stopSiren();
    const osc = audioCtx.createOscillator();
    const gain = audioCtx.createGain();
    osc.type = 'square';
    gain.gain.value = 0.4;
    osc.connect(gain);
    gain.connect(audioCtx.destination);
    osc.start();
    sirenOsc = osc;
    let high = true;
    sirenInterval = setInterval(() => {
      if(osc) osc.frequency.setValueAtTime(high ? 960 : 700, audioCtx.currentTime);
      high = !high;
    }, 450);
    setTimeout(() => window.stopSiren(), durationMs);
  } catch (e) { console.error("Siren failed", e); }
};

window.stopSiren = function() {
  if (sirenOsc) { try { sirenOsc.stop(); } catch(e){} sirenOsc.disconnect(); sirenOsc = null; }
  if (sirenInterval) { clearInterval(sirenInterval); sirenInterval = null; }
};

function triggerPanic() {
  const desc = document.getElementById("panic-mdesc");
  if (!state.user) {
    desc.textContent = "You are not logged in. Login to alert your saved contacts via SMS.";
  } else if (state.contacts.length === 0) {
    desc.textContent = "No contacts saved yet! Add emergency contacts first. Emergency call will still be suggested.";
  } else {
    const names = state.contacts.map(c => c.name).join(", ");
    desc.textContent = `Real SMS alerts will be sent to: ${names}. Also call an ambulance?`;
  }
  openModal("modal-panic");
}

async function confirmPanic() {
  window.startSiren(45000); // 45 sec blast
  closeModal("modal-panic");
  showToast("🚨 Siren blasting! Sending alerts…");

  // Try to get GPS location
  let locationStr = "";
  try {
    const pos = await new Promise((res, rej) => navigator.geolocation.getCurrentPosition(res, rej, { timeout: 3000 }));
    locationStr = `https://maps.google.com/?q=${pos.coords.latitude},${pos.coords.longitude}`;
  } catch {}

  if (state.user) {
    try {
      const data = await API.post("/panic", { location: locationStr });
      if (data.success) {
        if (data.simulated) {
          showToast(`📲 Simulated: ${data.count} contacts would be alerted. Add FAST2SMS_API_KEY for real SMS.`);
        } else {
          showToast(`✅ Real SMS sent to ${data.count} contact(s)!`);
        }
        addToHistory({ type:"PANIC_MODE", icon:"🚨", action:"Panic triggered — SMS sent", lang:state.lang, time:"Just now" });
      } else {
        showToast("⚠️ " + (data.message || "SMS failed"));
      }
    } catch {
      showToast("❌ Could not send alerts — calling 108 directly");
    }
  }

  // Always suggest calling 108
  setTimeout(() => {
    if (confirm("Also call 108 Ambulance now?")) makeCall("108");
  }, 500);
}

async function alertOnly() {
  window.startSiren(45000); // 45 sec blast
  closeModal("modal-panic");
  if (!state.user) { showToast("⚠️ Login to alert contacts"); return; }
  
  // Try to get GPS location
  let locationStr = "";
  try {
    const pos = await new Promise((res, rej) => navigator.geolocation.getCurrentPosition(res, rej, { timeout: 3000 }));
    locationStr = `https://maps.google.com/?q=${pos.coords.latitude},${pos.coords.longitude}`;
  } catch {}

  try {
    const data = await API.post("/panic", { location: locationStr });
    if (data.simulated) showToast(`📲 Simulation: ${data.count} contacts would be alerted`);
    else if (data.success) showToast(`✅ SMS sent to ${data.count} contact(s)!`);
    else showToast("⚠️ " + (data.message || "SMS failed"));
  } catch { showToast("❌ Could not send alerts"); }
}

// ── AUTH ──────────────────────────────────────────────────
async function doLogin() {
  const email = document.getElementById("login-email").value.trim();
  const pass  = document.getElementById("login-pass").value;
  const errEl = document.getElementById("login-err");
  errEl.style.display = "none";
  if (!email || !pass) { showErr(errEl,"Please fill all fields."); return; }
  const btn = event.target;
  btn.disabled = true; btn.textContent = "Logging in…";
  try {
    const data = await API.login(email, pass);
    if (data.success) { loginSuccess(data.name); }
    else { showErr(errEl, data.message); btn.disabled=false; btn.textContent="Login"; }
  } catch(e) { showErr(errEl, "Server error: " + e.message); btn.disabled=false; btn.textContent="Login"; }
}

async function doSignup() {
  const name  = document.getElementById("signup-name").value.trim();
  const email = document.getElementById("signup-email").value.trim();
  const pass  = document.getElementById("signup-pass").value;
  const errEl = document.getElementById("signup-err");
  errEl.style.display = "none";
  if (!name||!email||!pass) { showErr(errEl,"All fields required."); return; }
  if (pass.length < 6)      { showErr(errEl,"Password min. 6 chars."); return; }
  const btn = event.target;
  btn.disabled = true; btn.textContent = "Creating…";
  try {
    const data = await API.register(name, email, pass);
    if (data.success) { loginSuccess(data.name); }
    else { showErr(errEl, data.message); btn.disabled=false; btn.textContent="Create Account"; }
  } catch(e) { showErr(errEl, "Server error: " + e.message); btn.disabled=false; btn.textContent="Create Account"; }
}

function demoLogin() {
  state.contacts = [
    { id:1, name:"Priya Sharma", relation:"Family",  phone:"+91 98765 43210" },
    { id:2, name:"Amit Patel",   relation:"Friend",  phone:"+91 87654 32109" },
  ];
  loginSuccess("Demo User");
}

function loginSuccess(name) {
  state.user = name;
  renderUserLoggedIn(name);
  closeModal("modal-login");
  showToast("✅ Welcome, " + name.split(" ")[0] + "!");
  updateContactsBadge();
}

function renderUserLoggedIn(name) {
  const chip = `<div class="user-chip" onclick="doLogout()" title="Click to logout"><div class="user-avatar">${name[0].toUpperCase()}</div>${name.split(" ")[0]} <span style="color:var(--red); margin-left:6px; font-size:11px; font-weight:700; text-transform:uppercase;">Logout</span></div>`;
  const el1 = document.getElementById("auth-topbar");
  const el2 = document.getElementById("auth-sidebar");
  if (el1) el1.innerHTML = chip;
  if (el2) el2.innerHTML = chip;
  const cn = document.getElementById("contacts-auth-notice");
  if (cn) cn.style.display = "none";
}

function showAuthButtons() {
  const btn = `<button class="btn-sidebar-login" onclick="openModal('modal-login')"><svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4M10 17l5-5-5-5M15 12H3"/></svg>Login / Register</button>`;
  const el = document.getElementById("auth-sidebar");
  if (el) el.innerHTML = btn;
}

async function doLogout() {
  try { await API.logout(); } catch {}
  state.user = null; state.contacts = []; state.history = [];
  showAuthButtons();
  const el = document.getElementById("auth-topbar");
  if (el) el.innerHTML = "";
  updateContactsBadge();
  showToast("👋 Logged out");
  navTo("dashboard");
}

// ── CONTACTS ─────────────────────────────────────────────
async function renderContacts() {
  if (!state.user) {
    const n = document.getElementById("contacts-auth-notice");
    if (n) n.style.display = "flex";
    return;
  }
  try {
    const data = await API.getContacts();
    if (data.success) { state.contacts = data.contacts || []; }
    else { console.error("Error fetching contacts:", data.message); }
  } catch(e) { console.error("Server fetch failed:", e); }
  drawContacts();
}

function drawContacts() {
  const area = document.getElementById("contacts-area");
  const cnt  = state.contacts.length;
  const pill = document.getElementById("count-pill");
  if (pill) pill.textContent = cnt;
  updateContactsBadge();
  if (!area) return;
  if (cnt === 0) {
    area.innerHTML = `<div class="empty-state"><div class="es-icon">👥</div><div class="es-title">No contacts saved</div><div class="es-sub">Add your first emergency contact using the form.</div></div>`;
    return;
  }
  area.innerHTML = state.contacts.map(c => `
    <div class="contact-item">
      <div class="c-avatar">${c.name[0].toUpperCase()}</div>
      <div class="c-info">
        <div class="c-name">${esc(c.name)}</div>
        <div class="c-rel">${esc(c.relation || "Contact")}</div>
        <div class="c-phone">${esc(c.phone)}</div>
      </div>
      <button class="btn-remove-c" onclick="removeContact(${c.id})">Remove</button>
    </div>`).join("");
}

async function addContact() {
  const name  = document.getElementById("c-name").value.trim();
  const rel   = document.getElementById("c-rel").value;
  const phone = document.getElementById("c-phone").value.trim();
  if (!name||!phone) { showToast("⚠️ Name and phone are required"); return; }
  
  const btn = document.getElementById("btn-add-contact");
  const originalText = btn.innerHTML;
  btn.innerHTML = "<span>Adding...</span>";
  btn.disabled = true;

  if (state.user === "Demo User") {
    setTimeout(() => {
      state.contacts.push({ id: Date.now(), name, relation: rel, phone });
      document.getElementById("c-name").value  = "";
      document.getElementById("c-phone").value = "";
      drawContacts();
      showToast("✅ Contact added (Demo)!");
      btn.innerHTML = originalText;
      btn.disabled = false;
    }, 500);
    return;
  }

  try {
    const data = await API.addContact(name, rel, phone);
    if (data.success) {
      state.contacts.push({ id: data.id || Date.now(), name, relation: rel, phone });
      document.getElementById("c-name").value  = "";
      document.getElementById("c-phone").value = "";
      drawContacts();
      showToast("✅ Contact added!");
    } else {
      showToast("⚠️ " + data.message);
    }
  } catch(e) {
    showToast("❌ Server error: " + e.message);
  } finally {
    btn.innerHTML = originalText;
    btn.disabled = false;
  }
}

async function removeContact(id) {
  if (state.user === "Demo User") {
    state.contacts = state.contacts.filter(c => c.id !== id);
    drawContacts();
    showToast("🗑️ Contact removed (Demo)");
    return;
  }

  try { 
    const data = await API.deleteContact(id); 
    if (data.success) {
      state.contacts = state.contacts.filter(c => c.id !== id);
      drawContacts();
      showToast("🗑️ Contact removed");
    } else {
      showToast("⚠️ Could not remove: " + data.message);
    }
  } catch(e) {
    showToast("❌ Server error: failed to remove contact.");
  }
}

function updateContactsBadge() {
  const b = document.getElementById("contacts-badge");
  if (!b) return;
  if (state.contacts.length > 0) { b.textContent = state.contacts.length; b.style.display = "inline"; }
  else b.style.display = "none";
}

// ── HISTORY ───────────────────────────────────────────────
function addToHistory(entry) {
  state.history.unshift(entry);
  if (state.history.length > 50) state.history.pop();
}

async function renderHistory() {
  if (!state.user) return;
  try {
    const data = await API.getHistory();
    if (data.success) { state.history = data.history || []; }
  } catch(e) { console.error("History fetch failed", e); }
  drawHistory();
}

function drawHistory() {
  const area = document.getElementById("history-area");
  const btn  = document.getElementById("clear-hist-btn");
  if (!area) return;
  if (!state.history || state.history.length === 0) {
    area.innerHTML = `<div class="empty-state"><div class="es-icon">📋</div><div class="es-title">No history yet</div><div class="es-sub">Sessions appear here after you view first aid instructions.</div></div>`;
    if (btn) btn.style.display = "none";
    return;
  }
  if (btn) btn.style.display = "inline-block";
  const LANG_LABELS = { en:"English", hi:"हिन्दी", mr:"मराठी" };
  area.innerHTML = `
    <div class="history-table-header">
      <div></div><div>Emergency</div><div>Time</div><div>Language</div><div>Status</div>
    </div>` +
    state.history.map(h => {
      const icon  = h.icon || getIcon(h.type);
      const isPanic = h.type === "PANIC_MODE";
      const label = isPanic ? "Panic Mode" : (h.type || "");
      const badgeCls = isPanic ? "h-badge panic" : "h-badge viewed";
      const time   = h.time || formatTime(h.created_at);
      const lang   = LANG_LABELS[h.lang] || "English";
      return `<div class="history-row">
        <div class="h-icon">${icon}</div>
        <div><div class="h-type">${esc(label)}</div><div class="h-sub">${esc(h.action || "Viewed")}</div></div>
        <div class="h-time">${esc(time)}</div>
        <div class="h-lang">${lang}</div>
        <div><span class="${badgeCls}">${isPanic ? "Panic" : "Viewed"}</span></div>
      </div>`;
    }).join("");
}

async function clearHistory() {
  try { 
    const data = await API.clearHistory(); 
    if (data.success) {
      state.history = [];
      drawHistory();
      showToast("🗑️ History cleared");
    } else {
      showToast("⚠️ Could not clear: " + data.message);
    }
  } catch(e) {  showToast("❌ Server error: failed to clear history."); }
}

// ── LANGUAGE ─────────────────────────────────────────────
function setLang(lang) {
  state.lang = lang;
  const t = TRANSLATIONS[lang];
  document.querySelectorAll("[data-key]").forEach(el => {
    const key = el.getAttribute("data-key");
    if (t[key]) el.textContent = t[key];
  });
  if (state.currentType) loadFirstAid(state.currentType);
  showToast("🌐 Language updated");
}

// ── MODALS ────────────────────────────────────────────────
function openModal(id)  { document.getElementById(id).classList.add("open"); }
function closeModal(id) { document.getElementById(id).classList.remove("open"); }
function overlayClose(e, el) { if (e.target === el) el.classList.remove("open"); }
function switchTab(tab) {
  document.getElementById("form-login").style.display  = tab==="login"  ? "block":"none";
  document.getElementById("form-signup").style.display = tab==="signup" ? "block":"none";
  document.getElementById("mtab-login").classList.toggle("active",  tab==="login");
  document.getElementById("mtab-signup").classList.toggle("active", tab==="signup");
  ["login-err","signup-err"].forEach(id => { document.getElementById(id).style.display="none"; });
}

// ── TOAST ─────────────────────────────────────────────────
let _toastT;
function showToast(msg) {
  const t = document.getElementById("toast");
  t.textContent = msg; t.classList.add("show");
  clearTimeout(_toastT);
  _toastT = setTimeout(() => t.classList.remove("show"), 3200);
}

// ── UTILS ─────────────────────────────────────────────────
function showErr(el, msg) { el.textContent = msg; el.style.display = "block"; }
function esc(s) {
  if (!s) return "";
  const d = document.createElement("div"); d.textContent = s; return d.innerHTML;
}
function formatTime(iso) {
  if (!iso) return "Recently";
  try {
    const diff = Math.floor((Date.now() - new Date(iso)) / 1000);
    if (diff < 60)    return "Just now";
    if (diff < 3600)  return Math.floor(diff/60) + " min ago";
    if (diff < 86400) return Math.floor(diff/3600) + " hr ago";
    return Math.floor(diff/86400) + " days ago";
  } catch { return "Recently"; }
}
function getIcon(type) {
  return { burns:"🔥", bleeding:"🩸", fracture:"🦴", choking:"😮‍💨", heart:"❤️", drowning:"🌊", PANIC_MODE:"🚨" }[type] || "🆘";
}

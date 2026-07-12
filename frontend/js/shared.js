const BACKEND_URL = "http://127.0.0.1:5000";
const ROLE_NAV = {
  "Fleet Manager": [
    { key: "dashboard", icon: "fa-gauge", label: "Dashboard", href: "dashboard.html" },
    { key: "vehicles", icon: "fa-van-shuttle", label: "Fleet", href: "vehicles.html" },
    { key: "maintenance", icon: "fa-screwdriver-wrench", label: "Maintenance", href: "maintenance.html" },
    { key: "settings", icon: "fa-gear", label: "Settings", href: "settings.html" },
  ],
  "Dispatcher": [
    { key: "dashboard", icon: "fa-gauge", label: "Dashboard", href: "dashboard.html" },
    { key: "trips", icon: "fa-route", label: "Trips", href: "trips.html" },
    { key: "vehicles", icon: "fa-van-shuttle", label: "Fleet", href: "vehicles.html" },
    { key: "settings", icon: "fa-gear", label: "Settings", href: "settings.html" },
  ],
  "Safety Officer": [
    { key: "dashboard", icon: "fa-gauge", label: "Dashboard", href: "dashboard.html" },
    { key: "drivers", icon: "fa-id-card", label: "Drivers", href: "drivers.html" },
    { key: "settings", icon: "fa-gear", label: "Settings", href: "settings.html" },
  ],
  "Financial Analyst": [
    { key: "dashboard", icon: "fa-gauge", label: "Dashboard", href: "dashboard.html" },
    { key: "expenses", icon: "fa-gas-pump", label: "Fuel & Expenses", href: "expenses.html" },
    { key: "reports", icon: "fa-chart-line", label: "Analytics", href: "reports.html" },
    { key: "settings", icon: "fa-gear", label: "Settings", href: "settings.html" },
  ],
};

const ALL_ROLES = Object.keys(ROLE_NAV);

function currentRole() {
  return localStorage.getItem("role") || "Dispatcher";
}

function currentUserName() {
  return localStorage.getItem("name") || "Guest User";
}

function pageAllowedForRole(pageKey, role) {
  const nav = ROLE_NAV[role] || [];
  return nav.some(item => item.key === pageKey);
}

function mountShell(pageKey) {
  const token = localStorage.getItem("token");
  if (!token) {
    window.location.href = "index.html";
    return false;
  }

  const role = currentRole();

  if (!pageAllowedForRole(pageKey, role)) {
    document.body.innerHTML = `
      <div class="access-denied">
        <i class="fa-solid fa-lock"></i>
        <h2>Access Restricted</h2>
        <p>Your role (<strong>${role}</strong>) doesn't have permission to view this page.</p>
        <a href="dashboard.html" class="btn btn-primary" style="margin-top:16px; text-decoration:none;">
          Back to Dashboard
        </a>
      </div>`;
    return false;
  }

  const nav = ROLE_NAV[role];
  const navHtml = nav.map(item => `
    <a href="${item.href}" class="${item.key === pageKey ? "active" : ""}" style="text-decoration:none;">
      <li class="${item.key === pageKey ? "active" : ""}"><i class="fa-solid ${item.icon}"></i> ${item.label}</li>
    </a>`).join("");

  document.body.insertAdjacentHTML("afterbegin", `
    <nav class="sidebar">
      <div class="sidebar-brand">
        <img src="assets/logo.png" alt="transiQ">
        transiQ
      </div>
      <ul class="nav-links" style="list-style:none; padding:12px 0;">
        ${navHtml}
      </ul>
      <div class="sidebar-footer">transiQ &copy; 2026</div>
    </nav>
    <div class="main">
      <div class="topbar">
        <div class="search-box">
          <i class="fa-solid fa-magnifying-glass"></i>
          <input type="text" placeholder="Search...">
        </div>
        <div class="user-block">
          <span class="user-name">${currentUserName()}</span>
          <span class="role-badge">${role}</span>
          <button class="logout-btn" onclick="logout()">Logout</button>
        </div>
      </div>
      <div class="content" id="page-content"></div>
    </div>
    <div class="toast" id="app-toast"></div>
  `);

  return true;
}

function logout() {
  localStorage.clear();
  window.location.href = "index.html";
}

function showToast(message, type = "success") {
  const el = document.getElementById("app-toast");
  if (!el) return;
  el.textContent = message;
  el.className = `toast show ${type}`;
  setTimeout(() => el.classList.remove("show"), 2500);
}

async function apiGet(path) {
  const token = localStorage.getItem("token");
  const res = await fetch(`${BACKEND_URL}${path}`, {
    headers: { "Authorization": `Bearer ${token}` },
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.error || `Request failed (${res.status})`);
  }
  return res.json();
}

async function apiSend(path, method, body) {
  const token = localStorage.getItem("token");
  const res = await fetch(`${BACKEND_URL}${path}`, {
    method,
    headers: { "Content-Type": "application/json", "Authorization": `Bearer ${token}` },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.error || `Request failed (${res.status})`);
  }
  return res.json();
}

function statusClass(status) {
  return status.replace(/\s+/g, "");
}
// ============================================================
// roles.js — shared RBAC config + auth guard + nav renderer
// Include this on every protected page:
//   <script src="roles.js"></script>
// ============================================================

const LOGIN_PAGE = "login.html";
const DASHBOARD_PAGE = "dashboard.html";

const ROLE_CONFIG = {
  "Fleet Manager": {
    nav: [
      { icon: "fa-gauge", label: "Dashboard", href: "dashboard.html" },
      { icon: "fa-van-shuttle", label: "Fleet", href: "vehicles.html" },
      { icon: "fa-screwdriver-wrench", label: "Maintenance", href: "maintenance.html" },
      { icon: "fa-gear", label: "Settings", href: "settings.html" },
    ],
    kpis: ["activeVehicles", "availableVehicles", "inMaintenance", "utilization"],
    panels: ["vehicleStatus", "maintenanceAlerts"],
  },
  "Dispatcher": {
    nav: [
      { icon: "fa-gauge", label: "Dashboard", href: "dashboard.html" },
      { icon: "fa-route", label: "Trips", href: "trips.html" },
      { icon: "fa-van-shuttle", label: "Fleet", href: "vehicles.html" },
      { icon: "fa-gear", label: "Settings", href: "settings.html" },
    ],
    kpis: ["activeTrips", "pendingTrips", "availableVehicles", "driversOnDuty"],
    panels: ["recentTrips", "vehicleStatus"],
  },
  "Safety Officer": {
    nav: [
      { icon: "fa-gauge", label: "Dashboard", href: "dashboard.html" },
      { icon: "fa-id-card", label: "Drivers", href: "drivers.html" },
      { icon: "fa-shield-halved", label: "Compliance", href: "reports.html" },
      { icon: "fa-gear", label: "Settings", href: "settings.html" },
    ],
    kpis: ["driversOnDuty", "suspendedDrivers", "expiringLicenses", "avgSafetyScore"],
    panels: ["licenseExpiry", "driverStatus"],
  },
  "Financial Analyst": {
    nav: [
      { icon: "fa-gauge", label: "Dashboard", href: "dashboard.html" },
      { icon: "fa-gas-pump", label: "Fuel & Expenses", href: "expenses.html" },
      { icon: "fa-chart-line", label: "Analytics", href: "reports.html" },
      { icon: "fa-gear", label: "Settings", href: "settings.html" },
    ],
    kpis: ["operationalCost", "fuelCost", "maintenanceCost", "fleetUtilization"],
    panels: ["costBreakdown", "topExpenseVehicles"],
  },
};

// ------------------------------------------------------------
// Session helpers
// ------------------------------------------------------------
function getSession() {
  const role = localStorage.getItem("role");
  const name = localStorage.getItem("name");
  const token = localStorage.getItem("token");
  if (!role || !token || !ROLE_CONFIG[role]) return null;
  return { role, name: name || "User", token };
}

function setSession({ role, name, token }) {
  localStorage.setItem("role", role);
  localStorage.setItem("name", name);
  localStorage.setItem("token", token);
}

function clearSession() {
  localStorage.removeItem("role");
  localStorage.removeItem("name");
  localStorage.removeItem("token");
}

function logout() {
  clearSession();
  window.location.href = LOGIN_PAGE;
}

// Current file name, e.g. "vehicles.html"
function currentPage() {
  const path = window.location.pathname.split("/").pop();
  return path && path.length ? path : "dashboard.html";
}

// ------------------------------------------------------------
// Guards — call both at the top of every protected page's script
// ------------------------------------------------------------

// 1) Must be logged in at all
function requireAuth() {
  const session = getSession();
  if (!session) {
    window.location.href = LOGIN_PAGE;
    return null;
  }
  return session;
}

// 2) Must have this specific page in their role's nav (RBAC)
function requireAccess(session) {
  if (!session) return false;
  const config = ROLE_CONFIG[session.role];
  const allowed = config.nav.some(item => item.href === currentPage());
  if (!allowed) {
    alert(`Access denied: your role (${session.role}) does not have permission to view this page.`);
    window.location.href = DASHBOARD_PAGE;
    return false;
  }
  return true;
}

// Convenience: call once at top of page. Returns session or null (and redirects).
function protectPage() {
  const session = requireAuth();
  if (!session) return null;
  if (!requireAccess(session)) return null;
  return session;
}

// ------------------------------------------------------------
// Sidebar + topbar rendering (shared look across every page)
// ------------------------------------------------------------
function renderSidebar(session) {
  const el = document.getElementById("nav-links");
  if (!el) return;
  const config = ROLE_CONFIG[session.role];
  const active = currentPage();
  el.innerHTML = config.nav.map(item => `
    <li class="${item.href === active ? "active" : ""}" onclick="window.location.href='${item.href}'">
      <i class="fa-solid ${item.icon}"></i> ${item.label}
    </li>
  `).join("") + `
    <li onclick="logout()" style="margin-top:auto; border-top:1px solid #24262c;">
      <i class="fa-solid fa-arrow-right-from-bracket"></i> Log out
    </li>
  `;
}

function renderTopbar(session) {
  const nameEl = document.getElementById("user-name");
  const roleEl = document.getElementById("role-badge");
  if (nameEl) nameEl.textContent = session.name;
  if (roleEl) roleEl.textContent = session.role;
}
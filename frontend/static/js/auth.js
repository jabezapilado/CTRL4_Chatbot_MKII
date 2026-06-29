function getLoginUrl() {
    return "/login";
}

function requireAuth() {
    const user = sessionStorage.getItem("hau_user");

    if (!user) {
        window.location.replace("/login");
        return null;
    }

    return JSON.parse(user);
}

function logout() {
    sessionStorage.clear();
    localStorage.removeItem("hau_escalation_event");
    localStorage.removeItem("hau_escalation_staff_msg");
    localStorage.removeItem("hau_escalation_user_msg");

    window.location.replace("/login");
}

window.getLoginUrl = getLoginUrl;
window.requireAuth = requireAuth;
window.logout = logout;
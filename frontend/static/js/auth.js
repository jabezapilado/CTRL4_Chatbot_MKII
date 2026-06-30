function getLoginUrl() {
    return "/login?reason=session-required";
}

function requireAuth() {
    const user = sessionStorage.getItem("hau_user");

    return user ? JSON.parse(user) : null;
}

function logout() {
    fetch(`${window.location.origin}/auth/logout`, { method: "POST" })
        .catch(() => {})
        .finally(() => {
            sessionStorage.clear();
            localStorage.removeItem("hau_escalation_event");
            localStorage.removeItem("hau_escalation_staff_msg");
            localStorage.removeItem("hau_escalation_user_msg");
            window.location.replace("/login?reason=logged-out");
        });
}

window.getLoginUrl = getLoginUrl;
window.requireAuth = requireAuth;
window.logout = logout;
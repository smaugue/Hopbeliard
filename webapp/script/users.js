const DROITS = {
    PATIENT_LECTURE: 1,
    PATIENT_EDITION: 2,
    VEHICULE_RESA: 4,
    VEHICULE_GESTION: 8,
    VIDEO: 16,
    USERS_GESTION: 32,
    ADMIN: 256,
};

var page = 1;

/* ---------- Liste ---------- */

function droitsToText(level) {
    const noms = Object.entries(DROITS)
        .filter(([, v]) => (level & v) === v)
        .map(([n]) => n);
    return noms.length ? noms.join(", ") : "Aucun";
}

function cell(text) {
    const td = document.createElement("td");
    td.textContent = text ?? "";
    return td;
}

async function loadUsers() {
    const payload = {
        page: page,
    };
    const res = await fetch("/api/get_users", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
    });
    const data = await res.json();

    if (!data.ok) return;

    const body = document.getElementById("usersBody");
    body.innerHTML = "";

    if (data.users.length === 0) {
        page -=1;
        pb = document.getElementById("Preced");
        sb = document.getElementById("Suite");
        pb.value = (parseInt(pb.value) == 0) ? 0 : (parseInt(pb.value) - 1);
        sb.value = (parseInt(sb.value) == 2) ? 2 : (parseInt(sb.value) - 1);
        return loadUsers();
    }
    data.users.forEach(u => {
        const tr = document.createElement("tr");
        tr.append(
            cell(u.id),
            cell(u.login),
            cell(u.name),
            cell(u.lastname),
            cell(u.active ? "Oui" : "Non"),
            cell(droitsToText(u.access_level)),
            cell().appendChild(disableUserButton(u.login, u.active)),
            cell().appendChild(resetPasswordButton(u.login)),
            cell().appendChild(deleteUserButton(u.login))
        );
        body.append(tr);
    });

    document.getElementById("usersSection").hidden = false;
}

/* ---------- Remove User Logic ---------- */

function deleteUserButton(login) {
    var button1 = document.createElement("button");
    button1.value = login;
    button1.textContent = "Delete User";
    button1.addEventListener('click', async () => deleteUser(button1.value));
    return button1;
}

async function deleteUser(login) {
    const payload = {
        login: login.trim(),
    };

    try {
        const res = await fetch("/api/delete_user", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });
        const data = await res.json();
        if (!data.ok) {
            showAddMsg(data.error || "Erreur", true);
            return;
        }
    } catch {
        showAddMsg("Erreur réseau ou réponse invalide", true);
    }
    loadUsers();
}

/* ---------- Disabeled User Logic ---------- */

function disableUserButton(login, active) {
    var button1 = document.createElement("button");
    button1.dataset.login = login.trim();
    button1.dataset.access = Boolean(active ? false: true);
    button1.textContent = active ? "Disable User" : "Enable User";
    button1.addEventListener('click', async () => disableUser(button1.dataset));
    return button1;
}

async function disableUser(value) {
    const payload = {
        login: value.login.trim(),
        access_status: value.access,
    };

    try {
        const res = await fetch("/api/user_access_status", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });
        const data = await res.json();
        if (!data.ok) {
            showAddMsg(data.error || "Erreur", true);
            return;
        }
    } catch {
        showAddMsg("Erreur réseau ou réponse invalide", true);
    }
    loadUsers();
}

/* ---------- Reset Password Logic ---------- */

function resetPasswordButton(login) {
    var button1 = document.createElement("button");
    button1.value = login;
    button1.textContent = "ResetPassword";
    button1.addEventListener('click', async () => resetPassword(button1.value));
    return button1;
}

async function resetPassword(login) {
    const payload = {
        login: login.trim(),
    };

    try {
        const res = await fetch("/api/reset_user_password", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });
        const data = await res.json();
        if (!data.ok) {
            showAddMsg(data.error || "Erreur", true);
            return;
        }
        showNewPassword(login, data.psswd);
    } catch {
        showAddMsg("Erreur réseau ou réponse invalide", true);
    }
}

/* ---------- Mot de passe provisoire ---------- */

function showNewPassword(login, psswd) {
    document.getElementById("newUserLogin").textContent = login;
    document.getElementById("newUserPsswd").textContent = psswd;
    document.getElementById("newUserPassword").hidden = false;
}

function hideNewPassword() {
    document.getElementById("newUserPsswd").textContent = "";
    document.getElementById("newUserPassword").hidden = true;
}

async function copyPassword() {
    const psswd = document.getElementById("newUserPsswd").textContent;
    const btn = document.getElementById("copyPsswdBtn");
    try {
        await navigator.clipboard.writeText(psswd);
        btn.textContent = "Copié ✔";
    } catch {
        btn.textContent = "Copie impossible";
    }
    setTimeout(() => (btn.textContent = "Copier"), 2000);
}

/* ---------- Ajout ---------- */

function buildDroitsCheckboxes() {
    const fieldset = document.getElementById("addUserDroits");
    for (const [name, value] of Object.entries(DROITS)) {
        const label = document.createElement("label");
        const cb = document.createElement("input");
        cb.type = "checkbox";
        cb.value = value;
        label.append(cb, " " + name);
        fieldset.append(label);
    }
}

function droitsFromForm(form) {
    // OU binaire de toutes les cases cochées
    return [...form.querySelectorAll("#addUserDroits input:checked")]
        .reduce((acc, cb) => acc | Number(cb.value), 0);
}

function showAddMsg(text, isError = false) {
    const p = document.getElementById("addUserMsg");
    p.textContent = text;
    p.style.color = isError ? "red" : "green";
}

async function addUser(ev) {
    ev.preventDefault();
    const form = ev.target;
    hideNewPassword();

    const payload = {
        login: form.login.value.trim(),
        name: form.name.value.trim(),
        lastname: form.lastname.value.trim(),
        access_level: droitsFromForm(form),
    };

    try {
        const res = await fetch("/api/add_user", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });
        const data = await res.json();
        if (!data.ok) {
            showAddMsg(data.error || "Erreur", true);
            return;
        }
        showAddMsg(`${payload.login} ajouté`);
        showNewPassword(payload.login, data.psswd);
        form.reset();
        loadUsers();
    } catch {
        showAddMsg("Erreur réseau ou réponse invalide", true);
    }
}

function backPage() {
    pb = document.getElementById("Preced");
    sb = document.getElementById("Suite");
    page = pb.value;
    loadUsers();
    pb.value = (parseInt(pb.value) == 0) ? 0 : (parseInt(pb.value) - 1);
    sb.value = (parseInt(sb.value) == 2) ? 2 : (parseInt(sb.value) - 1);
}

function upPage() {
    pb = document.getElementById("Preced");
    sb = document.getElementById("Suite");
    page = sb.value;
    loadUsers();
    pb.value = (parseInt(pb.value) == 0) ? 0 : (parseInt(pb.value) + 1);
    sb.value = (parseInt(sb.value) == 2) ? 2 : (parseInt(sb.value) + 1);
}


/* ---------- Init ---------- */

buildDroitsCheckboxes();
document.getElementById("addUserForm").addEventListener("submit", addUser);
document.getElementById("copyPsswdBtn").addEventListener("click", copyPassword);
document.getElementById("Preced").addEventListener('click', backPage);
document.getElementById("Suite").addEventListener('click', upPage);
loadUsers();
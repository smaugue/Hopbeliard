var patient_id = null;
var patient_page = 1;
var pec_page = 1;

function cell(text) {
    const td = document.createElement("td");
    td.textContent = text ?? "";
    return td;
}

async function loadUsers(b) {
    br = (b===true) ? true : false;
    let data;

    const payload = {
        page: patient_page,
    };

    try {
        const res = await fetch("/api/get_patients", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
    });
        data = await res.json();
    } catch {
        return;
    }
    if (!data.ok) return;

    if (data.users.length === 0 && br) {
        patient_page -=1;
        pb = document.getElementById("PatientPreced");
        sb = document.getElementById("PatientSuite");
        pb.value = (parseInt(pb.value) == 0) ? 0 : (parseInt(pb.value) - 1);
        sb.value = (parseInt(sb.value) == 2) ? 2 : (parseInt(sb.value) - 1);
        return loadUsers(b=true);
    }

    const body = document.getElementById("usersBody");
    body.innerHTML = "";

    data.users.forEach(u => {
        const tr = document.createElement("tr");
        tr.append(
            cell(u.id),
            cell(u.name),
            cell(u.lastname),
            cell(u.comm),
            cell().appendChild(selectPatient(u.id))
        );
        body.append(tr);
    });

    document.getElementById("usersSection").hidden = false;
}

async function loadPEC(id, b) {

    br = (b===true) ? true : false;

    const payload = {
        id: id.trim(),
        page: pec_page,
    };

    const res = await fetch("/api/get_prise_en_charge", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
    });
    const data = await res.json();

    if (!data.ok) return;

    if (data.pec.length === 0 && br) {
        patient_page =- 1;
        pb = document.getElementById("PecPreced");
        sb = document.getElementById("PecSuite");
        pb.value = (parseInt(pb.value) == 0) ? 0 : (parseInt(pb.value) - 1);
        sb.value = (parseInt(sb.value) == 2) ? 2 : (parseInt(sb.value) - 1);
        return loadPEC(patient_id, b=true);
    }

    const body = document.getElementById("pecBody");
    body.innerHTML = "";

    if (!data.pec) {
        showAddMsg("Aucune donnée");
        return;
    }

    data.pec.forEach(u => {
        const tr = document.createElement("tr");
        tr.append(
            cell(u.id),
            cell(u.timestamp),
            cell(u.objet),
            cell(u.comm),
        );
        body.append(tr);
    });
}

/* ---------- Remove User Logic ---------- */

function selectPatient(id) {
    var button1 = document.createElement("button");
    button1.value = id;
    button1.textContent = "Select";
    button1.addEventListener('click', async () => getDataPatient(button1.value));
    return button1;
}

async function getDataPatient(id) {
    patient_id = id;
    pb = document.getElementById("PecPreced");
    sb = document.getElementById("PecSuite");
    pec_page = 1;
    pb.value = 0;
    sb.value = 2;
    loadPEC(patient_id)
}

function showAddMsg(text, isError = false) {
    const p = document.getElementById("addUserMsg");
    p.textContent = text;
    p.style.color = isError ? "red" : "green";
}

async function addPatient(ev) {
    ev.preventDefault();
    const form = ev.target;

    const payload = {
        name: form.name.value.trim(),
        lastname: form.lastname.value.trim(),
        comm: form.comm.value.trim(),
    };

    try {
        const res = await fetch("/api/add_patient", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });
        const data = await res.json();
        if (!data.ok) {
            showAddMsg(data.error || "Erreur", true);
            return;
        }
        form.reset();
        loadUsers();
    } catch {
        showAddMsg("Erreur réseau ou réponse invalide", true);
    }
}

async function addAdmition(ev) {
    ev.preventDefault();
    const form = ev.target;

    console.log(patient_id);

    const payload = {
        id: patient_id,
        objet: form.objet.value.trim(),
        comm: form.comm.value.trim(),
    };

    try {
        const res = await fetch("/api/add_admition", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });
        const data = await res.json();
        if (!data.ok) {
            showAddMsg(data.error || "Erreur", true);
            return;
        }
        form.reset();
        loadPEC(patient_id);
    } catch {
        showAddMsg("Erreur réseau ou réponse invalide", true);
    }
}

function patientBackPage() {
    pb = document.getElementById("PatientPreced");
    sb = document.getElementById("PatientSuite");
    patient_page = pb.value;
    loadUsers();
    pb.value = (parseInt(pb.value) == 0) ? 0 : (parseInt(pb.value) - 1);
    sb.value = (parseInt(sb.value) == 2) ? 2 : (parseInt(sb.value) - 1);
}

function patientUpPage() {
    pb = document.getElementById("PatientPreced");
    sb = document.getElementById("PatientSuite");
    patient_page = sb.value;
    loadUsers();
    pb.value = (parseInt(pb.value) == 0) ? 0 : (parseInt(pb.value) + 1);
    sb.value = (parseInt(sb.value) == 2) ? 2 : (parseInt(sb.value) + 1);
}

function pecBackPage() {
    pb = document.getElementById("PecPreced");
    sb = document.getElementById("PecSuite");
    pec_page = pb.value;
    loadPEC(patient_id);
    pb.value = (parseInt(pb.value) == 0) ? 0 : (parseInt(pb.value) - 1);
    sb.value = (parseInt(sb.value) == 2) ? 2 : (parseInt(sb.value) - 1);
}

function pecUpPage() {
    pb = document.getElementById("PecPreced");
    sb = document.getElementById("PecSuite");
    pec_page = sb.value;
    loadPEC(patient_id);
    pb.value = (parseInt(pb.value) == 0) ? 0 : (parseInt(pb.value) + 1);
    sb.value = (parseInt(sb.value) == 2) ? 2 : (parseInt(sb.value) + 1);
}

/* ---------- Init ---------- */
document.getElementById("addPatientForm").addEventListener("submit", addPatient);
document.getElementById("admitionForm").addEventListener("submit", addAdmition);

document.getElementById("PatientPreced").addEventListener('click', patientBackPage);
document.getElementById("PatientSuite").addEventListener('click', patientUpPage);

document.getElementById("PecPreced").addEventListener('click', pecBackPage);
document.getElementById("PecSuite").addEventListener('click', pecUpPage);

loadUsers();
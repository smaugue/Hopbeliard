
document.getElementById("resetPasswordButton").addEventListener("click", async () => {
    const p = document.getElementById("password").value;
    const np = document.getElementById("new_password").value;
    const npc = document.getElementById("new_password_rep").value;
    if (np === npc) {
        const res = await changerMotDePasse(p, np);
        if (res) window.location.href = "/api/logout";
        else alert(res.error)
    } else alert("Mots de passe différent")
});

async function changerMotDePasse(ancien, nouveau) {
    const enc = new TextEncoder();
    const hex = buf => [...new Uint8Array(buf)].map(b => b.toString(16).padStart(2, "0")).join("");
    const sha256 = async txt => hex(await crypto.subtle.digest("SHA-256", enc.encode(txt)));
    const hmac = async (cleHex, msg) => {
        const cle = await crypto.subtle.importKey(
            "raw", new Uint8Array(cleHex.match(/../g).map(h => parseInt(h, 16))),
            { name: "HMAC", hash: "SHA-256" }, false, ["sign"]);
        return hex(await crypto.subtle.sign("HMAC", cle, enc.encode(msg)));
    };

    // Étape 1 : récupération du challenge
    let r = await fetch("/api/change_password", {
        method: "POST", headers: { "Content-Type": "application/json" }, body: "{}"
    });
    const { sel, challenge, nouveau_sel, error } = await r.json();
    if (!r.ok) throw new Error(error);

    // Étape 2 : preuve de l'ancien mot de passe + envoi du nouveau hash
    const reponse = await hmac(await sha256(ancien + sel), challenge);
    const nouveauHash = await sha256(nouveau + nouveau_sel);

    r = await fetch("/api/change_password", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ reponse, nouveau: nouveauHash })
    });
    const res = await r.json();
    if (!res.ok) throw new Error(res.error);
    return true;
}
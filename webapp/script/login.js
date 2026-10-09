async function login(username, password) {
    const enc = new TextEncoder();
    const toHex = buf => [...new Uint8Array(buf)].map(b => b.toString(16).padStart(2, "0")).join("");
    const post = body => fetch("/api/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body)
    }).then(r => r.json());

    // 1. Demande du challenge
    const { sel, challenge } = await post({ login: username });

    // 2. H = SHA256(mdp + sel), identique à ce qui est stocké en base
    const h = await crypto.subtle.digest("SHA-256", enc.encode(password + sel));

    // 3. reponse = HMAC-SHA256(clé = H, message = challenge)
    const key = await crypto.subtle.importKey("raw", h, { name: "HMAC", hash: "SHA-256" }, false, ["sign"]);
    const reponse = toHex(await crypto.subtle.sign("HMAC", key, enc.encode(challenge)));

    // 4. Envoi de la réponse
    return post({ login: username, reponse });
}

document.getElementById("registerButton").addEventListener("click", async () => {
    const res = await login(
        document.getElementById("playerName").value,
        document.getElementById("password").value
    );
    if (res.ok) window.location.href = "/";
    else alert(res.error);
});
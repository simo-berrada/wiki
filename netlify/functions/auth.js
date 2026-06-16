// Step 1 of the GitHub login: send the user to GitHub to authorize.
// This runs on the SAME Netlify site that hosts the editor, so the login
// never crosses to another website (which is what corporate browsers block).
const crypto = require("crypto");

exports.handler = async (event) => {
  const clientId = process.env.OAUTH_CLIENT_ID;
  if (!clientId) {
    return { statusCode: 500, body: "Missing OAUTH_CLIENT_ID environment variable." };
  }

  const proto = event.headers["x-forwarded-proto"] || "https";
  const host = event.headers.host;
  const redirectUri = `${proto}://${host}/.netlify/functions/callback`;

  // Random state to protect against cross-site request forgery; we stash it in
  // a short-lived cookie and verify it in the callback.
  const state = crypto.randomBytes(16).toString("hex");

  const params = new URLSearchParams({
    client_id: clientId,
    redirect_uri: redirectUri,
    scope: "repo",
    state,
    allow_signup: "false",
  });

  return {
    statusCode: 302,
    headers: {
      Location: `https://github.com/login/oauth/authorize?${params.toString()}`,
      "Set-Cookie": `oauth_state=${state}; HttpOnly; Secure; SameSite=Lax; Path=/; Max-Age=600`,
      "Cache-Control": "no-store",
    },
    body: "",
  };
};

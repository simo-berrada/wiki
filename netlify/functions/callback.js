// Step 2 of the GitHub login: GitHub sends the user back here with a code.
// We swap the code for an access token, then hand it to the editor window.
// Because this page is served from the same site as the editor, the hand-off
// works even in locked-down corporate browsers.
const https = require("https");

function exchangeCodeForToken(payload) {
  return new Promise((resolve, reject) => {
    const body = JSON.stringify(payload);
    const request = https.request(
      {
        hostname: "github.com",
        path: "/login/oauth/access_token",
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json",
          "Content-Length": Buffer.byteLength(body),
          "User-Agent": "woah-wiki-oauth",
        },
      },
      (response) => {
        let data = "";
        response.on("data", (chunk) => (data += chunk));
        response.on("end", () => {
          try {
            resolve(JSON.parse(data));
          } catch (error) {
            reject(error);
          }
        });
      }
    );
    request.on("error", reject);
    request.write(body);
    request.end();
  });
}

// The exact handshake Decap CMS listens for: the popup announces itself, the
// editor replies, and then the popup posts the result back to the editor.
function handshakePage(status, content) {
  const safeContent = JSON.stringify(content).replace(/</g, "\\u003c");
  return `<!doctype html>
<html lang="en">
  <head><meta charset="utf-8"><title>Completing sign-in…</title></head>
  <body>
    <p>Completing sign-in… you can close this window if it does not close itself.</p>
    <script>
      (function () {
        var status = ${JSON.stringify(status)};
        var content = ${safeContent};
        var message = "authorization:github:" + status + ":" + JSON.stringify(content);
        function send(event) {
          if (!window.opener) return;
          window.opener.postMessage(message, event.origin);
          window.removeEventListener("message", send, false);
        }
        window.addEventListener("message", send, false);
        if (window.opener) {
          window.opener.postMessage("authorizing:github", "*");
        }
      })();
    </script>
  </body>
</html>`;
}

function readCookie(header, name) {
  if (!header) return null;
  const match = header.match(new RegExp("(?:^|; )" + name + "=([^;]+)"));
  return match ? match[1] : null;
}

exports.handler = async (event) => {
  const query = event.queryStringParameters || {};
  const code = query.code;
  const returnedState = query.state;
  const cookieState = readCookie(event.headers.cookie, "oauth_state");
  const clearCookie = "oauth_state=; HttpOnly; Secure; SameSite=Lax; Path=/; Max-Age=0";

  const respond = (status, content) => ({
    statusCode: 200,
    headers: {
      "Content-Type": "text/html; charset=utf-8",
      "Set-Cookie": clearCookie,
      "Cache-Control": "no-store",
    },
    body: handshakePage(status, content),
  });

  if (!code) {
    return respond("error", { message: "No code returned from GitHub." });
  }
  if (!cookieState || cookieState !== returnedState) {
    return respond("error", { message: "Login session expired. Please try again." });
  }

  try {
    const data = await exchangeCodeForToken({
      client_id: process.env.OAUTH_CLIENT_ID,
      client_secret: process.env.OAUTH_CLIENT_SECRET,
      code,
    });
    if (data.error || !data.access_token) {
      return respond("error", {
        message: data.error_description || data.error || "No access token returned.",
      });
    }
    return respond("success", { token: data.access_token, provider: "github" });
  } catch (error) {
    return respond("error", { message: "Could not reach GitHub to finish sign-in." });
  }
};

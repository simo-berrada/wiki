// Adds a persistent "Edit" button to the MkDocs Material header.
// It links to the wiki's own /admin/ editor (Decap CMS), which prompts a
// GitHub login. Only repository collaborators can actually save changes.
(function () {
  function siteRoot() {
    // The header logo link points at the site root (honours the /wiki/ base
    // path on GitHub Pages and the localhost root in preview).
    var logo = document.querySelector(".md-header__inner .md-logo");
    if (logo && logo.getAttribute("href")) {
      var href = logo.href;
      return href.endsWith("/") ? href : href + "/";
    }
    return "/";
  }

  function addEditButton() {
    var header = document.querySelector(".md-header__inner");
    if (!header || header.querySelector(".wiki-edit-button")) {
      return;
    }

    var link = document.createElement("a");
    link.className = "wiki-edit-button md-button";
    link.href = siteRoot() + "admin/";
    link.textContent = "Edit";
    link.title = "Edit this wiki (sign in with GitHub)";

    var search = header.querySelector(".md-search");
    if (search) {
      header.insertBefore(link, search);
    } else {
      header.appendChild(link);
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", addEditButton);
  } else {
    addEditButton();
  }
})();

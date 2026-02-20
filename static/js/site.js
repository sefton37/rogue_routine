(function () {
  "use strict";

  // Digest card: Read more / Show less toggle
  document.addEventListener("click", function (e) {
    if (!e.target.classList.contains("digest-read-more")) return;
    var btn = e.target;
    var content = btn.previousElementSibling;
    if (content) {
      content.classList.toggle("collapsed");
      btn.textContent = content.classList.contains("collapsed") ? "Read more" : "Show less";
    }
  });

  // Reader page: hide static article fallback when JS is available
  var staticArticles = document.getElementById("static-articles");
  if (staticArticles) {
    staticArticles.hidden = true;
  }
})();

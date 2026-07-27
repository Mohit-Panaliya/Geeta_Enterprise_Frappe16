import { readFileSync, writeFileSync } from "fs"
import { resolve } from "path"

// Read built index.html
const builtHtml = readFileSync(
  resolve("../oil_distribution/public/frontend/index.html"),
  "utf-8"
)

// Inject Frappe template variables, PWA manifest & service worker
const wwwTemplate = builtHtml
  .replace(
    "</title>",
    `</title>
  <script>
    window.csrf_token = "{{ csrf_token }}"
    window.boot = {{ boot | tojson }}
  </script>
  <link rel="manifest" href="/assets/oil_distribution/frontend/manifest.json" />
  <meta name="theme-color" content="#3b82f6" />
  <meta name="apple-mobile-web-app-capable" content="yes" />
  <meta name="apple-mobile-web-app-status-bar-style" content="default" />`
  )
  .replace(
    "</body>",
    `<script>
  if ('serviceWorker' in navigator) {
    window.addEventListener('load', function () {
      navigator.serviceWorker.register('/assets/oil_distribution/frontend/service-worker.js');
    });
  }
</script>
</body>`
  )

writeFileSync(
  resolve("../oil_distribution/www/oil-ops.html"),
  wwwTemplate
)

console.log("✓ www/oil-ops.html updated")

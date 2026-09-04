import { io } from "socket.io-client";
//// Neoffice — removed here: upstream's
//// `import { socketio_port } from "../../../../sites/common_site_config.json"`.
//// See the marker in initSocket() below for why (build-time value, no bench on
//// the CI runner). Restore nothing at the merge — keep our window fallback.

// extend window object
declare global {
  interface Window {
    site_name: string;
    //// Neoffice — added: the port is read off the window now, see initSocket().
    socketio_port?: string;
  }
}

export function initSocket() {
  //// Neoffice — the port now comes from the window, not from a static import.
  //// Upstream read it from sites/common_site_config.json, four levels up; vite
  //// resolves that at build time, so the value baked into the bundle is the
  //// BUILDER's, and on a commit-the-build fork the builder is a GitHub runner
  //// with no bench at all. Kept synchronous on purpose: `export const socket =
  //// initSocket()` runs at module load, so there is no room for an await here.
  // Default Frappe socketio port (matches the value bench writes to
  // sites/common_site_config.json in production). The legacy static
  // import of that file broke production builds — the bundle externalised
  // the path and 404'd at runtime. We now read window.socketio_port if
  // injected by the host page, otherwise fall back to 9000.
  const socketio_port = window.socketio_port || "9000";

  let host = window.location.hostname;
  let siteName = window.site_name || host;
  let port = window.location.port ? `:${socketio_port}` : "";
  let protocol = port ? "http" : "https";
  let url = `${protocol}://${host}${port}/${siteName}`;

  const socket = io(url, {
    withCredentials: true,
    reconnectionAttempts: 5,
  });

  return socket;
}

export const socket = initSocket();

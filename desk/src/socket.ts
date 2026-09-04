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
    //// Typed `number | string`: get_boot() ships it as the integer bench keeps
    //// in common_site_config.json, and it is only ever interpolated into a URL.
    socketio_port?: number | string;
  }
}

export function initSocket() {
  //// Neoffice — the port now comes from the window, not from a static import.
  //// Upstream read it from sites/common_site_config.json, four levels up; vite
  //// resolves that at build time, so the value baked into the bundle is the
  //// BUILDER's, and on a commit-the-build fork the builder is a GitHub runner
  //// with no bench at all. Kept synchronous on purpose: `export const socket =
  //// initSocket()` runs at module load, so there is no room for an await here.
  //// Neoffice — window.socketio_port is now genuinely set. The contract was
  //// dangling: this line has always read the window, but nothing wrote that
  //// key, so the "9000" literal was the only value the SPA ever used. The
  //// port is now shipped by helpdesk/www/helpdesk/index.py get_boot(), which
  //// the served page emits as `window["socketio_port"]` and which
  //// desk/src/main.js re-reads onto `window` in dev — see the marker there.
  //// The literal stays as a last resort (an old cached page, a host that does
  //// not inject it) and matches the value bench writes to
  //// sites/common_site_config.json.
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

import { io } from "socket.io-client";

// extend window object
declare global {
  interface Window {
    site_name: string;
    socketio_port?: string;
  }
}

export function initSocket() {
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

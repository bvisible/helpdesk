import { useTelemetry } from "frappe-ui/frappe";
//// Neoffice — upstream's static import of frappe's posthog.js is left out.
//// It reaches three directories up into a SIBLING app of the bench: on the CI
//// runner that compiles our SPA (commit-the-build) that path does not exist, and
//// in production vite externalises it into a URL that 404s. Posthog is loaded by
//// the host page when there is one; without it, telemetry is a no-op. Upstream
//// develop drops this import itself later on (checked 2026-09-04): at that merge,
//// take upstream's file whole.
const APP = "helpdesk";

interface CaptureOptions {
  data: {
    [key: string]: string | number | boolean | object;
  };
}

export function capture(event: string, options: CaptureOptions = { data: {} }) {
  const { capture: _capture } = useTelemetry();
  _capture(event, options.data);
}

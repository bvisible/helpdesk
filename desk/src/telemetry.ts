import { ref } from "vue";
import { createResource } from "frappe-ui";
//// Neoffice — upstream's static import of frappe's posthog.js was removed here.
//// It reaches three directories up into a SIBLING app of the bench; on a CI
//// runner (commit-the-build) that path does not exist, and in production vite
//// externalises it into a URL that 404s. At the merge, keep our removal.

// NOTE: the legacy `import '../../../frappe/frappe/public/js/lib/posthog.js'`
// was removed because the externalised path 404s in production (and CI).
// Posthog is loaded by the host page when desk is mounted; when absent,
// telemetry is a no-op.

const APP = "helpdesk";
const SITENAME = window.location.hostname;

// extend window object to add posthog
// eslint-disable-next-line @typescript-eslint/no-explicit-any
declare global {
  interface Window {
    posthog: any;
  }
}
type PosthogSettings = {
  posthog_project_id: string;
  posthog_host: string;
  enable_telemetry: boolean;
  telemetry_site_age: number;
};

const telemetry = ref({
  enabled: false,
  project_id: "",
  host: "",
});

let posthog: typeof window.posthog = window.posthog;

let posthogSettings = createResource({
  url: "helpdesk.api.telemetry.get_posthog_settings",
  cache: "posthog_settings",
  onSuccess: (ps: PosthogSettings) => init(ps),
});

function isTelemetryEnabled() {
  if (!posthogSettings.data) return false;

  return (
    posthogSettings.data.enable_telemetry &&
    posthogSettings.data.posthog_project_id &&
    posthogSettings.data.posthog_host
  );
}

export async function init(ps: PosthogSettings) {
  if (!isTelemetryEnabled()) return;
  posthog.init(ps.posthog_project_id, {
    api_host: ps.posthog_host,
    autocapture: false,
    person_profiles: "identified_only",
    disable_session_recording: true,
    advanced_disable_decide: true,
    loaded: (ph: typeof posthog) => {
      window.posthog = ph;
      ph.identify(SITENAME);
    },
  });
}

interface CaptureOptions {
  data: {
    user?: string;
    [key: string]: string | number | boolean | object;
  };
}

export function capture(
  event: string,
  options: CaptureOptions = { data: { user: "" } }
) {
  if (!isTelemetryEnabled()) return;
  window.posthog?.capture?.(`${APP}_${event}`, options);
}

export function recordSession() {
  if (!telemetry.value.enabled) return;
  if (window.posthog && window.posthog.__loaded) {
    window.posthog.startSessionRecording();
  }
}

export function stopSession() {
  if (!telemetry.value.enabled) return;
  if (
    window.posthog &&
    window.posthog.__loaded &&
    window.posthog.sessionRecordingStarted()
  ) {
    window.posthog.stopSessionRecording();
  }
}

export function posthogPlugin(app: any) {
  app.config.globalProperties.posthog = window.posthog;
  if (!window.posthog?.length) posthogSettings.fetch();
}

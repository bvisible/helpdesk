//// Neoffice — added import: upstream wrote every validation message of this file in plain
//// English; they are shown under the Twilio / Exotel fields, never compared, so each one is
//// wrapped in __() (same pass as 71a5669d9). They run when a form is validated, not at import.
import { __ } from "@/translation";

export const isDocDirty = (doc: any, originalDoc: any) => {
  if (!doc || !originalDoc) return false;
  return JSON.stringify(doc) !== JSON.stringify(originalDoc);
};

export const validateTwilio = (twilio, telephonyAgent, twilioErrors) => {
  if (telephonyAgent.default_medium === "Twilio" && !twilio.enabled) {
    twilioErrors.value.default_medium =
      __("Enable Twilio to set it as default medium"); //// Neoffice — __(), see the import
  } else {
    twilioErrors.value.default_medium = "";
  }

  if (!twilio.enabled) {
    return;
  }

  if (!twilio.account_sid) {
    twilioErrors.value.accountSid = __("Account SID is required"); //// Neoffice — __(), see the import
  } else {
    twilioErrors.value.accountSid = "";
  }

  if (!twilio.auth_token) {
    twilioErrors.value.authToken = __("Auth Token is required"); //// Neoffice — __(), see the import
  } else {
    twilioErrors.value.authToken = "";
  }

  if (!telephonyAgent.twilio_number) {
    twilioErrors.value.number = __("Number is required"); //// Neoffice — __(), see the import
  } else if (!validatePhone(telephonyAgent.twilio_number)) {
    twilioErrors.value.number = __("Please enter a valid phone number"); //// Neoffice — __(), see the import
  } else {
    twilioErrors.value.number = "";
  }
};

export const validateExotel = (exotel, telephonyAgent, exotelErrors) => {
  if (telephonyAgent.default_medium === "Exotel" && !exotel.enabled) {
    exotelErrors.value.default_medium =
      __("Enable Exotel to set it as default medium"); //// Neoffice — __(), see the import
  } else {
    exotelErrors.value.default_medium = "";
  }

  if (!exotel.enabled) {
    return;
  }

  if (!exotel.account_sid) {
    exotelErrors.value.accountSid = __("Account SID is required"); //// Neoffice — __(), see the import
  } else {
    exotelErrors.value.accountSid = "";
  }

  if (!exotel.webhook_verify_token) {
    exotelErrors.value.webhookVerifyToken = __("Webhook Verify Token is required"); //// Neoffice — __(), see the import
  } else {
    exotelErrors.value.webhookVerifyToken = "";
  }

  if (!exotel.subdomain) {
    exotelErrors.value.subdomain = __("Subdomain is required"); //// Neoffice — __(), see the import
  } else {
    exotelErrors.value.subdomain = "";
  }

  if (!exotel.api_key) {
    exotelErrors.value.apiKey = __("API Key is required"); //// Neoffice — __(), see the import
  } else {
    exotelErrors.value.apiKey = "";
  }

  if (!exotel.api_token) {
    exotelErrors.value.apiToken = __("API Token is required"); //// Neoffice — __(), see the import
  } else {
    exotelErrors.value.apiToken = "";
  }

  if (!telephonyAgent.exotel_number) {
    exotelErrors.value.number = __("Number is required"); //// Neoffice — __(), see the import
  } else if (!validatePhone(telephonyAgent.exotel_number)) {
    exotelErrors.value.number = __("Please enter a valid phone number"); //// Neoffice — __(), see the import
  } else {
    exotelErrors.value.number = "";
  }

  if (!telephonyAgent.mobile_no) {
    exotelErrors.value.mobileNo = __("Personal number is required"); //// Neoffice — __(), see the import
  } else if (!validatePhone(telephonyAgent.mobile_no)) {
    exotelErrors.value.mobileNo = __("Please enter a valid phone number"); //// Neoffice — __(), see the import
  } else {
    exotelErrors.value.mobileNo = "";
  }
};

const validatePhone = (number: string) => {
  return /^\+?\d{8,15}$/.test(number);
};

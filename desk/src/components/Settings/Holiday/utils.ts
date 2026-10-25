//// Neoffice — added: __() import, getRepetitionText below built English fragments
//// ("Every first and second week") that no catalogue could translate.
import { __ } from "@/translation";

//// Neoffice — rewritten around whole messages: the ordinals are looked up one by one
//// (each its own msgid), the sentence is ONE message with a hole ("Every {0} week"),
//// and "and" is its own msgid. The result is the same English text as upstream's.
export const getRepetitionText = (repetition: any) => {
  if (repetition.all) return __("Every week");

  //// Neoffice — i18n of the v1.31.0 merge: __() wrap or label/value split (upstream shows this string in English on every non-English site)
  const ordinals: string[] = [];
  if (repetition.first) ordinals.push(__("first"));
  if (repetition.second) ordinals.push(__("second"));
  if (repetition.third) ordinals.push(__("third"));
  if (repetition.fourth) ordinals.push(__("fourth"));
  if (repetition.fifth) ordinals.push(__("fifth"));

  //// Neoffice — i18n of the v1.31.0 merge: __() wrap or label/value split (upstream shows this string in English on every non-English site)
  if (ordinals.length === 0) return "";

  //// Neoffice — i18n of the v1.31.0 merge: __() wrap or label/value split (upstream shows this string in English on every non-English site)
  const last = ordinals.pop() as string;
  const list = ordinals.length ? `${ordinals.join(", ")} ${__("and")} ${last}` : last;
  return __("Every {0} week", list);
};

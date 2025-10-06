// plutil.runtime.ts
import * as math from "mathjs";
import _ from "lodash";
import * as mathhelper from "./mathHelpers";
import { imageUrl } from "./imageHandling";
/**
 * Safer / clearer param replacement:
 *  - Supports {{ params.foo.bar }}, {{ param_labels.x }}, {{ correct_answers.y }}
 *  - Leaves unknown tokens intact (easier debugging)
 */
export const replace_params = (x: string, data: any): string => {
  if (typeof x !== "string" || !x.includes("{{")) return x;

  // Match {{ ... }} tokens including dotted paths
  const TOKEN = /{{\s*([^}]+?)\s*}}/g;

  return x.replace(TOKEN, (_m, inner: string) => {
    const raw = String(inner).trim();
    // prefix.type => path
    // e.g. "params.span" => prefix="params", path="span"
    const [prefix, ...rest] = raw.split(".");
    const path = rest.join(".");
    switch (prefix) {
      case "params": {
        const v = _.get(data, `params.${path}`);
        return v ?? _m;
      }
      case "param_labels": {
        const v = _.get(data, `param_labels.${path}`);
        return v ?? _m;
      }
      case "correct_answers_labels": {
        const v = _.get(data, `correct_answers_labels.${path}`);
        return v ?? _m;
      }
      case "correct_answers": {
        const v = _.get(data, `correct_answers.${path}`);
        return v ?? _m;
      }
      default:
        return _m; // unknown token preserved
    }
  });
};

/** Escape text for safe attribute usage (basic) */
const escAttr = (s: any) =>
  String(s ?? "")
    .replace(/"/g, "&quot;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");

/** Escape text nodes */
const escText = (s: any) =>
  String(s ?? "")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");

/* =========================
 *  Widget renderers
 * ========================= */

export const pl_symbolic_input = ($: any, qdata: any, el: any): string => {
  const att = $(el).attr() || {};
  const name = att["answers-name"] ?? "symbolic";
  const label = att["label"] ?? "Answer";

  return `
<form class="pl-form pl-form--symbolic answers" action="" method="" name="${escAttr(
    name
  )}">
  <fieldset class="pl-fieldset">
    <legend class="pl-legend">Answer</legend>
    <div class="pl-field">
      <label class="pl-label" for="${escAttr(name)}">${escText(label)}</label>
      <input class="pl-input" type="text" name="${escAttr(name)}" id="${escAttr(
    name
  )}" inputmode="text" />
    </div>
    <div class="pl-feedback" aria-live="polite"></div>
  </fieldset>
</form>`.trim();
};

export const pl_figure = ($: any, qname: string, el: any): string => {
  const att = $(el).attr() || {};
  const nm = att["file-name"] ?? "";
  console.log("This is the question title", qname)
  const imFileName = `/questions/${qname}/${nm}`;
  const imgURL = imageUrl(imFileName);
  return `
<figure class="pl-figure">
  <img src="${escAttr(
    imgURL
  )}" alt="Figure for question" class="pl-figure__img" />
</figure>`.trim();
};

export const pl_quest_prompt = ($: any, _qname: string, el: any): string => {
  const inner = $(el).html() ?? "";
  return `<p class="pl-prompt">${inner}</p>`;
};

/** Adaptive MCA: marks correct answers into data attributes; returns original content wrapped */
export const pl_mca_adaptive = ($: any, qdata: any, el: any): string => {
  const $checkbox = $(el).find("pl-checkbox").first();
  const att = $checkbox.attr() || {};
  const nm = att["answers-name"];
  const $answers = $checkbox.find("pl-answer");

  $answers.each((_i: number, ael: any) => {
    const aAtt = $(ael).attr() || {};
    const choiceName = aAtt["choice-name"];
    const isCorrect = _.get(qdata, ["correct_answers", nm, choiceName], false);
    $(ael).attr("data-correct", String(Boolean(isCorrect)));
  });

  // Hand back the original contents; outer pipeline will replace element
  return `<div class="pl-adaptive pl-adaptive--mca">${
    $checkbox.html() ?? ""
  }</div>`;
};

/** Adaptive MCQ: similar to MCA */
export const pl_mcq_adaptive = ($: any, qdata: any, el: any): string => {
  const $mcq = $(el).find("pl-multiple-choice").first();
  const att = $mcq.attr() || {};
  const nm = att["answers-name"];
  const $answers = $mcq.find("pl-answer");

  $answers.each((_i: number, ael: any) => {
    const aAtt = $(ael).attr() || {};
    const choiceName = aAtt["choice-name"];
    const isCorrect = _.get(qdata, ["correct_answers", nm, choiceName], false);
    $(ael).attr("data-correct", String(Boolean(isCorrect)));
  });

  return `<div class="pl-adaptive pl-adaptive--mcq">${$mcq.html() ?? ""}</div>`;
};

export const pl_checkbox = ($: any, el: any) => {
  const att = $(el).attr() || {};
  const nm = att["answers-name"] ?? "checkbox";
  const children = $(el).children();

  const order = mathhelper.getRandomPermutationRange(children.length);
  const correctAnswers: string[] = [];
  const itemOrder: string[] = [];
  let html = `
<form class="pl-form pl-form--checkbox answers" action="" method="" name="${escAttr(
    nm
  )}">
  <fieldset class="pl-fieldset">
    <legend class="pl-legend">Select all that apply</legend>
    <div class="pl-options">
`.trim();

  order.forEach((idx: number, j: number) => {
    const node = children[idx.toString()];
    const text =
      (node?.children?.[0]?.data
        ? String(node.children[0].data).trim()
        : $(node).text().trim()) || "";
    const id = `child${idx}`;
    const isCorrect = node?.attribs?.["correct"] === "true";
    if (isCorrect) correctAnswers.push(id);
    itemOrder.push(id);

    html += `
      <label class="pl-option">
        <input class="pl-input pl-input--checkbox response" type="checkbox" id="${escAttr(
          id
        )}" name="${escAttr(nm)}" value="${j + 1}" />
        <span class="pl-option__text">${escText(`${j + 1}. ${text}`)}</span>
      </label>`.trim();
  });

  html += `
    </div>
    <div class="pl-feedback" aria-live="polite"></div>
  </fieldset>
</form>`.trim();

  return { name: nm, htmlString: html, correctAnswers, itemOrder };
};

export const pl_multiple_choice = ($: any, el: any) => {
  const att = $(el).attr() || {};
  const nm = att["answers-name"] ?? "mcq";
  const children = $(el).children();

  const order = mathhelper.getRandomPermutationRange(children.length);
  const correctAnswers: string[] = [];
  const itemOrder: string[] = [];
  let html = `
<form class="pl-form pl-form--mcq answers" action="" method="" name="${escAttr(
    nm
  )}">
  <fieldset class="pl-fieldset">
    <legend class="pl-legend">Choose one</legend>
    <div class="pl-options">
`.trim();

  order.forEach((idx: number, j: number) => {
    const node = children[idx.toString()];
    const text =
      (node?.children?.[0]?.data
        ? String(node.children[0].data).trim()
        : $(node).text().trim()) || "";
    const id = `child${idx}`;
    const isCorrect = node?.attribs?.["correct"] === "true";
    if (isCorrect) correctAnswers.push(id);
    itemOrder.push(id);

    html += `
      <label class="pl-option">
        <input class="pl-input pl-input--radio response" type="radio" id="${escAttr(
          id
        )}" name="${escAttr(nm)}" value="${j + 1}" />
        <span class="pl-option__text">${escText(`${j + 1}. ${text}`)}</span>
      </label>`.trim();
  });

  html += `
    </div>
    <div class="pl-feedback" aria-live="polite"></div>
  </fieldset>
</form>`.trim();

  return { name: nm, htmlString: html, correctAnswers, itemOrder };
};

export const pl_static_text = ($: any, _qdata: any, el: any) => {
  const att = $(el).attr() || {};
  return att["name"] ?? "";
};

export const pl_number_input_fixed = ($: any, qdata: any, el: any) => {
  const att = $(el).attr() || {};
  const name = att["answers-name"] ?? "number";
  const label = att["label"] ?? "Answer";
  const digits = att["digits"];
  const fixedVal =
    att["correct-answer-fixed"] ??
    _.get(qdata, ["correct_answers", name], undefined);

  const html = `
<form class="pl-form pl-form--number answers" name="${escAttr(
    name
  )}" action="" method="">
  <fieldset class="pl-fieldset">
    <legend class="pl-legend">Answer</legend>
    <div class="pl-field">
      <label class="pl-label" for="${escAttr(name)}">${escText(label)}</label>
      <input class="pl-input pl-input--number response" type="number" name="${escAttr(
        name
      )}" id="${escAttr(name)}" inputmode="decimal" />
    </div>
    <div class="pl-feedback" aria-live="polite"></div>
  </fieldset>
</form>`.trim();

  return {
    name,
    htmlString: html,
    correctAnswers: fixedVal,
    sigfigs: digits,
  };
};

export const pl_number_input = ($: any, qdata: any, el: any) => {
  const att = $(el).attr() || {};
  const name = att["answers-name"] ?? "number";
  const label = att["label"] ?? "Answer";
  const val =
    att["correct-answer"] ?? _.get(qdata, ["correct_answers", name], undefined);

  const html = `
<form class="pl-form pl-form--number answers" name="${escAttr(
    name
  )}" action="" method="">
  <fieldset class="pl-fieldset">
    <legend class="pl-legend">Answer</legend>
    <div class="pl-field">
      <label class="pl-label" for="${escAttr(name)}">${escText(label)}</label>
      <input class="pl-input pl-input--number response" type="number" name="${escAttr(
        name
      )}" id="${escAttr(name)}" inputmode="decimal" />
    </div>
    <div class="pl-feedback" aria-live="polite"></div>
  </fieldset>
</form>`.trim();

  return html;
};

export const pl_hint = ($: any, _qdata: any, el: any) => {
  const att = $(el).attr() || {};
  const level = att["level"] ?? "default";
  const htmlString = $(el).html() ?? "";
  console.log("Inside the pl hint", htmlString);
  return { htmlString, level };
};

export const pl_matrix_input = ($: any, _qdata: any, el: any) => {
  const att = $(el).attr() || {};
  const name = att["answers-name"] ?? "matrix";
  const label = att["label"] ?? "Matrix";

  const html = `
<form class="pl-form pl-form--matrix answers" name="${escAttr(
    name
  )}" action="" method="">
  <fieldset class="pl-fieldset">
    <legend class="pl-legend">Answer</legend>
    <div class="pl-field">
      <label class="pl-label" for="${escAttr(name)}">${escText(label)}</label>
      <input class="pl-input pl-input--matrix response" type="text" name="${escAttr(
        name
      )}" id="${escAttr(name)}" />
    </div>
    <div class="pl-feedback" aria-live="polite"></div>
  </fieldset>
</form>`.trim();

  return html;
};

export const pl_matrix_latex = ($: any, qdata: any, el: any) => {
  const att = $(el).attr() || {};
  const dp = att["params-name"];
  const val = _.get(qdata, ["params", dp], []);
  return emitLatexMatrix(val);
};

export const emitLatexMatrix = (mat: number[][]): string => {
  if (!Array.isArray(mat) || !Array.isArray(mat[0]))
    return "\\begin{bmatrix}\\end{bmatrix}";
  const rows = mat
    .map((row) =>
      row.map((el) => String(math.round(Number(el) * 100) / 100)).join(" & ")
    )
    .join(" \\\\ ");
  return `\\begin{bmatrix} ${rows} \\end{bmatrix}`;
};

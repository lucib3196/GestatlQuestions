import * as cheerio from "cheerio";
import * as plutil from "./plutil";
import * as math from "mathjs";
import * as mathhelper from "./mathHelpers";

export const processPrairielearnTags = (
  html: string,
  qdata: any,
  qdir: string,
  questionName: string,
  choiceParams: { fracQuestions?: [number, number] } = { fracQuestions: [1, 1] }
) => {
  try {
    const $ = cheerio.load(html, { xmlMode: false });
    let htmlString: string | undefined;
    let formattedSolution: string | undefined;
    const solutionsStrings: Record<string | number, string> = {};
    const answerMeta: Array<Record<string, unknown>> = [];

    // pl-matrix-input
    $("pl-matrix-input").each((_, el) => {
      htmlString = plutil.pl_matrix_input($, qdata, el);
      $(el).before(htmlString).remove();
    });

    // pl-matrix-latex
    $("pl-matrix-latex").each((_, el) => {
      htmlString = plutil.pl_matrix_latex($, qdata, el);
      $(el).before(htmlString).remove();
    });

    // pl-number-input
    $("pl-number-input").each((_, el) => {
      htmlString = plutil.pl_number_input($, qdata, el);
      $(el).before(htmlString).remove();
    });

    // pl-number-input-fixed (collects answers)
    $("pl-number-input-fixed").each((_, el) => {
      const res = plutil.pl_number_input_fixed($, qdata, el);
      htmlString = res.htmlString;
      $(el).before(htmlString).remove();
      const dat = {
        name: res.name,
        correct_answers: res.correctAnswers,
        sigfigs: res.sigfigs,
      };
      answerMeta.push(dat);
    });

    // pl-symbolic-input
    $("pl-symbolic-input").each((_, el) => {
      htmlString = plutil.pl_symbolic_input($, qdata, el);
      $(el).before(htmlString).remove();
    });

    // pl-quest selection
    const $quests = $("pl-quest");
    const numQuestions = $quests.length;

    const [fracMin, fracMax] = choiceParams.fracQuestions ?? [1, 1];
    const minQuestions = Math.max(
      0,
      Math.floor(numQuestions * Math.max(0, fracMin))
    );
    const maxQuestions = Math.min(
      numQuestions,
      Math.ceil(numQuestions * Math.min(1, Math.max(fracMin, fracMax)))
    );
    const numSelQuestions = numQuestions
      ? math.randomInt(minQuestions, maxQuestions + 1)
      : 0;

    const mask = Array(numQuestions)
      .fill(0)
      .map((_, i) => (i < numSelQuestions ? 1 : 0));
    mathhelper.shuffleArray(mask);

    $quests.each((i, el) => {
      if (mask[i] === 1) {
        const cnt = $(el).contents();
        $(el).replaceWith(cnt);
      } else {
        $(el).remove();
      }
    });

    // Adaptive MCQ/MCA (ensure we actually insert transformed HTML)
    $("pl-mcq-adaptive").each((_, el) => {
      const transformed = plutil.pl_mcq_adaptive($, qdata, el);
      $(el).before(transformed).remove();
    });

    $("pl-mca-adaptive").each((_, el) => {
      const transformed = plutil.pl_mca_adaptive($, qdata, el);
      $(el).before(transformed).remove();
    });

    // pl-quest-prompt
    $("pl-quest-prompt").each((_, el) => {
      htmlString = plutil.pl_quest_prompt($, qdata, el);
      $(el).before(htmlString).remove();
    });

    // pl-question-panel: wrap once, then unwrap tag but keep contents
    const $panels = $("pl-question-panel");
    if ($panels.length) {
      $panels.wrapAll('<div class="wrapper"></div>');
      $panels.each((_, el) => {
        const cnt = $(el).contents();
        $(el).replaceWith(cnt);
      });
    }

    // pl-hint (collect solutionsStrings)
    $("pl-hint").each((_, el) => {
      const res = plutil.pl_hint($, qdata, el);

      solutionsStrings[res.level] = res.htmlString;
      formattedSolution = Object.entries(solutionsStrings)
        .map(([_, v]) => `<div class='pl-hint'>${v}</div>`)
        .join("");
      $(el).remove(); // if hints are collected elsewhere
    });

    $("pl-solution-hint").each((_, el) => {
      const res = plutil.pl_hint($, qdata, el);
      if (!res.level) {
      }
      solutionsStrings[res.level] = res.htmlString;
      formattedSolution = Object.entries(solutionsStrings)
        .map(([_, v]) => `<div class='pl-hint'>${v}</div>`)
        .join("");
      $(el).remove(); // if hints are collected elsewhere
    });

    // pl-static-text — wrap THIS element once, quote attribute
    $("pl-static-text").each((_, el) => {
      const dp = plutil.pl_static_text($, qdata, el);
      const $el = $(el);
      $el.wrap(`<div class="static_text" name="${String(dp)}"></div>`);
      const cnt = $el.contents();
      $el.replaceWith(cnt);
    });

    // pl-figure
    $("pl-figure").each((_, el) => {
      htmlString = plutil.pl_figure($, questionName, el);
      $(el).before(htmlString).remove();
    });

    // pl-checkbox (collects answers)
    $("pl-checkbox").each((_, el) => {
      const res = plutil.pl_checkbox($, el);
      htmlString = res.htmlString;
      answerMeta.push({
        name: res.name,
        correct_answers: res.correctAnswers,
        itemOrder: res.itemOrder,
      });
      $(el).before(htmlString).remove();
    });

    // pl-multiple-choice (collects answers)
    $("pl-multiple-choice").each((_, el) => {
      const res = plutil.pl_multiple_choice($, el);
      htmlString = res.htmlString;
      answerMeta.push({
        name: res.name,
        correct_answers: res.correctAnswers,
        itemOrder: res.itemOrder,
      });
      $(el).before(htmlString).remove();
    });
    return {
      answers: answerMeta, // <- flattened
      solution: formattedSolution,
      solutionsStrings: solutionsStrings,
      htmlString: $("body").html() ?? "", // <- inner HTML only
    };
  } catch (error) {
    console.log(error);
  }
};

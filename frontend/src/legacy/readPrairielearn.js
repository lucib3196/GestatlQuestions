import * as cheerio from "cheerio";
import * as plutil from "./plutil.js";
import * as math from "mathjs";
import * as mathhelper from "./mathhelpers.js";
const html = `<pl-question-panel>
  <p>
    A simply supported steel beam with a span of {{params.span}}
    {{params.unitsSpan}} carries a point load of {{params.load}}
    {{params.unitsForce}} at its center.
  </p>
  <p>
    If the beam has a rectangular cross-section of width {{params.width}}
    {{params.unitsDist}} and height {{params.height}} {{params.unitsDist}}, what
    is the maximum bending stress in the beam?
  </p>
</pl-question-panel>

<p>(Give your answer in MPa.)</p>
<pl-number-input
  answers-name="maxBendingStress"
  comparison="sigfig"
  digits="3"
  label="Maximum Bending Stress ($ \sigma_{max} $) = "
></pl-number-input>
`; // your HTML block

export const processPrairielearnTags = (
  html,
  qdata,
  qdir,
  questionName,
  choiceParams
) => {
  const $ = cheerio.load(html, null, false);
  let h;
  let htmlString;

  let ans = {
    answers: [],
  };
  h = $("pl-matrix-input");
  h.each((i, el) => {
    htmlString = plutil.pl_matrix_input($, qdata, el);
    $(el).before(htmlString);
    $(el).remove();
  });

  h = $("pl-matrix-latex");
  h.each((i, el) => {
    htmlString = plutil.pl_matrix_latex($, qdata, el);
    $(el).before(htmlString);
    $(el).remove();
  });

  h = $("pl-number-input");
  h.each((i, el) => {
    htmlString = plutil.pl_number_input($, qdata, el);
    $(el).before(htmlString);
    $(el).remove();
  });

  h = $("pl-number-input-fixed");
  h.each((i, el) => {
    res = plutil.pl_number_input_fixed($, qdata, el);
    htmlString = res["htmlString"];
    $(el).before(htmlString);
    $(el).remove();
    dat = {
      name: res["name"],
      correct_answers: res["correctAnswers"],
      sigfigs: res["sigfigs"],
    };
    ans.answers.push(dat);
  });

  h = $("pl-symbolic-input");
  h.each((i, el) => {
    htmlString = plutil.pl_symbolic_input($, qdata, el);
    $(el).before(htmlString);
    $(el).remove();
  });
  h = $("pl-quest");
  let numQuestions = h.length;
  console.log("This contains ", numQuestions, " questions");
  console.log(choiceParams);
  let minQuestions = math.floor(numQuestions * choiceParams.fracQuestions[0]);
  let maxQuestions = math.ceil(numQuestions * choiceParams.fracQuestions[1]);
  let numSelQuestions = math.randomInt(minQuestions, maxQuestions + 1);
  console.log(
    `min = ${minQuestions}, max = ${maxQuestions}, numSelQuestions = ${numSelQuestions}`
  );
  let selectQuestionsMask = [];
  selectQuestionsMask.length = numQuestions;
  selectQuestionsMask.fill(0);
  for (let i = 0; i < numSelQuestions; i++) {
    selectQuestionsMask[i] = 1;
  }
  console.log("Selection Questions = ", selectQuestionsMask);
  mathhelper.shuffleArray(selectQuestionsMask);
  console.log("Random Selection Array = ", selectQuestionsMask);
  h.each((i, el) => {
    if (selectQuestionsMask[i] == 1) {
      let cnt = $(el).contents();
      let par = $(el).parent();
      $(el).replaceWith(cnt);
    } else {
      $(el).replaceWith("");
    }
  });
  h = $("pl-mcq-adaptive");
  h.each((i, el) => {
    let cnt = $(el).contents();
    htmlString = plutil.pl_mcq_adaptive($, qdata, el);
    let par = $(el).parent();
    $(el).replaceWith(cnt);
  });
  h = $("pl-mca-adaptive");
  h.each((i, el) => {
    let cnt = $(el).contents();
    htmlString = plutil.pl_mca_adaptive($, qdata, el);
    let par = $(el).parent();
    $(el).replaceWith(cnt);
  });
  h = $("pl-quest-prompt");
  h.each((i, el) => {
    htmlString = plutil.pl_quest_prompt($, qdata, el);
    $(el).before(htmlString);
    $(el).remove();
  });
  h = $("pl-question-panel");
  h.wrapAll('<div class="wrapper">');
  h.each((i, el) => {
    let cnt = $(el).contents();
    let par = $(el).parent();
    $(el).replaceWith(cnt);
  });
  let solutionsStrings = {};
  h = $("pl-hint");
  h.each((i, el) => {
    res = plutil.pl_hint($, qdata, el);
    htmlString = res["htmlString"];
    level = res["level"];
    solutionsStrings[level] = htmlString;
  });
  h = $("pl-static-text");
  h.each((i, el) => {
    dp = plutil.pl_static_text($, qdata, el);
    h.wrapAll(`<div class="static_text" name=${dp}>`);
    let cnt = $(el).contents();
    let par = $(el).parent();
    $(el).replaceWith(cnt);
    $(el).remove();
  });

  let im = $("pl-figure");
  im.each((i, el) => {
    // const att = $(el).attr();
    // nm= att['file-name'];
    // imFileName = qdir + '/clientFilesQuestion/' + nm;
    // const htmlString = `<img src="${imFileName}" alt="Picture for problem" width="300" height="300" class="pic" />`;
    htmlString = plutil.pl_figure($, questionName, el);
    $(el).before(htmlString);
    $(el).remove();
  });
  h = $("pl-checkbox");
  h.each((i, el) => {
    res = plutil.pl_checkbox($, el);
    htmlString = res["htmlString"];
    dat = {
      name: res["name"],
      correct_answers: res["correctAnswers"],
      itemOrder: res["itemOrder"],
    };
    ans.answers.push(dat);
    //     console.log(htmlString);
    $(el).before(htmlString);
    $(el).remove();
  });
  h = $("pl-multiple-choice");
  h.each((i, el) => {
    res = plutil.pl_multiple_choice($, el);
    htmlString = res["htmlString"];
    dat = {
      name: res["name"],
      correct_answers: res["correctAnswers"],
      itemOrder: res["itemOrder"],
    };
    ans.answers.push(dat);
    // console.log(htmlString);
    $(el).before(htmlString);
    $(el).remove();
  });
  return {
    answers: ans,
    solutionsStrings: solutionsStrings,
    htmlString: $.html(),
  };
};

const choiceParams = { fracQuestions: [1.0, 1.0] };
const qdata = {
  params: {
    span: 7.013012061759164,
    load: 13005.439244390143,
    width: 0.2564458471123129,
    height: 0.33680705503915653,
    unitsSpan: "m",
    unitsForce: "N",
    unitsDist: "m",
    unitsStress: "MPa",
    intermediate: {
      moment: 22801.825572346017,
      inertia: 0.0008165033378861506,
      sectionModulus: 0.004848493080355609,
    },
  },
  correct_answers: { maxBendingStress: 4.703 },
  nDigits: 3,
  sigfigs: 3,
};
// const data = processPrairielearnTags(html, qdata, "", "", choiceParams);

// console.log(plutil.replace_params(data.htmlString, qdata));
// console.log(data);
// Mark this as a module
export {};

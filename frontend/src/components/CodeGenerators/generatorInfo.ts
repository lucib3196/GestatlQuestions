export type Example = {
  name: string;
  text: string;
};

export type GeneratorConfig = {
  name: string;
  description: string;
  examples: Example[];
  link: string;
};

export const generators: Record<"text" | "image" | "lecture", GeneratorConfig> =
  {
    text: {
      name: "TextGen",
      description:
        "Generate a complete practice module from a single text-based question, perfect for quick question creation.",
      examples: [
        {
          name: "Projectile Motion",
          text: "A ball is thrown horizontally from the top of a 50-meter high building with an initial speed of 15 meters per second. Assuming there is no air resistance, calculate the time it takes for the ball to reach the ground.",
        },
        {
          name: "Spring Oscillation",
          text: "A mass-spring system oscillates with a period of 2 seconds. If the spring constant is 100 N/m, calculate the mass attached to the spring. Assume the motion is simple harmonic.",
        },
        {
          name: "Pressure Calculation",
          text: "A force of 200 Newtons is applied perpendicular to a circular cross-sectional area with a radius of 0.1 meters. Calculate the pressure exerted on the area.",
        },
      ],
      link: "/generators/text_generator",
    },
    image: {
      name: "ImageGen",
      description:
        "Upload an image to create richer, more accurate practice modules—ideal for complex, step-by-step problems.",
      examples: [
        {
          name: "Textbook Solutions",
          text: "Officially published problems and solutions ensure high accuracy.",
        },
        {
          name: "Handwritten Solutions",
          text: "Personal notes or handwritten solutions will be effectively processed.",
        },
        {
          name: "Lecture Materials",
          text: "Slides or instructional content from lectures can be used to create modules.",
        },
      ],
      link: "/generators/image_generator",
    },
    lecture: {
      name: "LectureGen",
      description:
        "Summarize lectures, extract key concepts, and generate complete practice modules from full sets of lecture materials.",
      examples: [
        {
          name: "Fluid Dynamics Lecture",
          text: "Lecture notes on Bernoulli’s equation and flow continuity are transformed into practice problems with worked solutions.",
        },
        {
          name: "Thermodynamics Session",
          text: "A full lecture on refrigeration cycles is condensed into summaries, conceptual questions, and computational modules.",
        },
        {
          name: "Control Systems Slides",
          text: "Slide decks on PID controllers are converted into interactive learning modules with step-by-step examples.",
        },
      ],
      link: "/generators/lecture_generator",
    },
  };

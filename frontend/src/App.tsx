import { MathJaxContext } from "better-react-mathjax";
import QuestionSettingsProvider from "./context/GeneralSettingsContext";
import { AuthProvider } from "./context/AuthContext";
import NavBar from "./components/NavBar/NavBar";
import { ToastContainer } from "react-toastify";
import CodeEditorProvider from "./context/CodeEditorContext";
import { QuestionProvider } from "./context/QuestionContext";
import ChatUI from "./components/ChatUI/ChatUI";
import { QuestionRuntimeProvider } from './context/QuestionAnswerContext';



const config = {
  loader: { load: ["[tex]/ams"] },
  tex: {
    inlineMath: [
      ["$", "$"],
      ["\(", "\)"]
    ],
    displayMath: [
      ["$$", "$$"],
      ["\\[", "\\]"]
    ],
    processEscapes: true,
  },
  options: {
    ignoreHtmlClass: "no-mathjax",
    processHtmlClass: "mathjax-process",
  },
};

function App() {
  return (
    <AuthProvider>
      <MathJaxContext version={3} config={config}>
        <QuestionRuntimeProvider>
          <QuestionSettingsProvider>
            <QuestionProvider>
              <CodeEditorProvider>
                {/* Main Content */}
                <NavBar />
                <ToastContainer />
                <ChatUI />
                {/* <LecturePage /> */}
                {/* <LegacyQuestion /> */}
                {/* End of Main Content */}
              </CodeEditorProvider>
            </QuestionProvider>
          </QuestionSettingsProvider>
        </QuestionRuntimeProvider>
      </MathJaxContext>
    </AuthProvider>
  );
}

export default App;

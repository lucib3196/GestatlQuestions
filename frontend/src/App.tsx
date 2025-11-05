import { MathJaxContext } from "better-react-mathjax";
import QuestionSettingsProvider from "./context/GeneralSettingsContext";
import { AuthProvider } from "./context/AuthContext";
import NavBar from "./components/NavBar/NavBar";
import { ToastContainer } from "react-toastify";
import CodeEditorProvider from "./context/CodeEditorContext";
import { LecturePage } from "./pages/LecturePage";
import { QuestionProvider } from "./context/QuestionContext";

const config = {
  loader: { load: ["[tex]/ams"] },
  tex: {
    inlineMath: [["$", "$"]],
    displayMath: [["$$", "$$"]],
  },
};

function App() {
  return (
    <AuthProvider>
      <MathJaxContext version={3} config={config}>
        <QuestionSettingsProvider>
          <QuestionProvider>
            <CodeEditorProvider>
              {/* Main Content */}
              <NavBar />
              <ToastContainer />
              <LecturePage />
              {/* <LegacyQuestion /> */}
              {/* End of Main Content */}
            </CodeEditorProvider>
          </QuestionProvider>
        </QuestionSettingsProvider>
      </MathJaxContext>
    </AuthProvider>
  );
}

export default App;

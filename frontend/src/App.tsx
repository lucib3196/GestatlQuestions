import { MathJaxContext } from "better-react-mathjax";
import QuestionProvider from "./context/QuestionFilterContext";
import QuestionSettingsProvider from "./context/GeneralSettingsContext";
import RunningQuestionProvider from "./context/QuestionSelectionContext";
import { AuthProvider } from "./context/AuthContext";
import { QuestionDBProvider } from "./context/QuestionContext";
import NavBar from "./components/NavBar/NavBar";
import { ToastContainer } from "react-toastify";
import LogsProvider from "./context/CodeLogsContext";
import QuestionSelectionProvider from "./context/QuestionSelectionContext";
import { LecturePage } from "./pages/LecturePage";
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
      <QuestionSelectionProvider>
        <QuestionDBProvider>
          <MathJaxContext version={3} config={config}>
            <QuestionProvider>
              <QuestionSettingsProvider>
                <RunningQuestionProvider>
                  <LogsProvider>
                    {/* Main Content */}
                    <NavBar />
                    <ToastContainer />
                    <LecturePage />
                    {/* <LegacyQuestion /> */}
                    {/* End of Main Content */}
                  </LogsProvider>
                </RunningQuestionProvider>
              </QuestionSettingsProvider>
            </QuestionProvider>
          </MathJaxContext>
        </QuestionDBProvider>
      </QuestionSelectionProvider>
    </AuthProvider>
  );
}

export default App;

import { MathJaxContext } from "better-react-mathjax";
import QuestionSettingsProvider from "./context/GeneralSettingsContext";
import RunningQuestionProvider from "./context/SelectedQuestionContext";
import { AuthProvider } from "./context/AuthContext";
import NavBar from "./components/NavBar/NavBar";
import { ToastContainer } from "react-toastify";
import LogsProvider from "./context/CodeLogsContext";
import QuestionSelectionProvider from "./context/SelectedQuestionContext";
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
      <QuestionProvider>
        <QuestionSelectionProvider>
          <MathJaxContext version={3} config={config}>
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
          </MathJaxContext>
        </QuestionSelectionProvider>
      </QuestionProvider>
    </AuthProvider>
  );
}

export default App;

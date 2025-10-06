import { MathJaxContext } from "better-react-mathjax";
import QuestionProvider from "./context/QuestionFilterContext";
import QuestionSettingsProvider from "./context/GeneralSettingsContext";
import RunningQuestionProvider from "./context/RunningQuestionContext";
import { AuthProvider } from "./context/AuthContext";
import { QuestionDBProvider } from "./context/QuestionContext";
import NavBar from "./components/NavBar/NavBar";
import { ToastContainer } from "react-toastify";
import LogsProvider from "./context/CodeLogsContext";
import { QuestionView } from "./pages/QuestionView";


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
      <QuestionDBProvider>
        <MathJaxContext version={3} config={config}>
          <QuestionProvider>
            <QuestionSettingsProvider>
              <RunningQuestionProvider>
                <LogsProvider>
                  {/* Main Content */}
                  <NavBar />
                  <ToastContainer />
                  <QuestionView />
                  {/* <UpdateQuestionMetaForm /> */}

                  {/* <LegacyQuestion /> */}
                  {/* End of Main Content */}
                </LogsProvider>
              </RunningQuestionProvider>
            </QuestionSettingsProvider>
          </QuestionProvider>
        </MathJaxContext>
      </QuestionDBProvider>
    </AuthProvider>
  );
}

export default App;

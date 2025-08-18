

import { MathJaxContext } from "better-react-mathjax";
import QuestionProvider from "./context/QuestionFilterContext";
import QuestionSettingsProvider from "./context/GeneralSettingsContext";
import RunningQuestionProvider from "./context/RunningQuestionContext";
import { AuthProvider } from "./context/AuthContext";
import { QuestionDBProvider } from "./context/QuestionContext";
import NavBar from "./components/NavBar";
import { ToastContainer } from "react-toastify";

const config = {
  loader: { load: ["[tex]/ams"] },
  tex: {
    inlineMath: [["$", "$"]],
    displayMath: [["$$", "$$"]],
  },
};


function App() {

  return (
    <AuthProvider >
      <QuestionDBProvider>
        <MathJaxContext version={3} config={config}>
            <QuestionProvider >
              <QuestionSettingsProvider>
                <RunningQuestionProvider>
                
                  {/* Main Content */}
                  <NavBar />
                  <ToastContainer />
                  {/* End of Main Content */}
                  
                </RunningQuestionProvider>
              </QuestionSettingsProvider>
            </QuestionProvider>
          
        </MathJaxContext>
      </QuestionDBProvider>
    </AuthProvider>
  );
}

export default App;

// import { useEffect, useState } from "react";
// import { onAuthStateChanged } from "firebase/auth";
// import type { User } from "firebase/auth";
// import { auth } from "./config/firebaseClient";
// import { sendRequestToBackend } from "./utils/firestoreAuth";
// const [user, setUser] = useState<User | null>(null);

// useEffect(() => {
//   const unsub = onAuthStateChanged(auth, setUser);
//   return unsub;
// }, []);

// useEffect(() => {
//   const fetchData = async () => {
//     const user = auth.currentUser;
//     if (user) {
//       await sendRequestToBackend();
//     }
//   };
//   fetchData();
// }, [user]);
// import SignUp from "./components/SignUp";

import { MathJaxContext } from "better-react-mathjax";
import QuestionProvider from "./context/QuestionFilterContext";
import QuestionSettingsProvider from "./context/GeneralSettingsContext";
import RunningQuestionProvider from "./context/RunningQuestionContext";
import NavBar from "./components/NavBar";
const config = {
  loader: { load: ["[tex]/ams"] },
  tex: {
    inlineMath: [["$", "$"]],
    displayMath: [["$$", "$$"]],
  },
};


function App() {
  return (
    <MathJaxContext version={3} config={config}>
      <QuestionProvider >
        <QuestionSettingsProvider>
          <RunningQuestionProvider>

            {/* Main Content */}
            <NavBar />

            {/* End of Main Content */}
          </RunningQuestionProvider>
        </QuestionSettingsProvider>
      </QuestionProvider>

    </MathJaxContext>
  );
}

export default App;

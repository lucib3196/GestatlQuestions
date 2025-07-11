import { createUserWithEmailAndPassword } from "firebase/auth";
import { doc, setDoc } from "firebase/firestore";
import { auth, db } from "../config/firebaseClient";

export async function signUpUser(
  email: string,
  password: string,
  role: string
) {
  const userCredential = await createUserWithEmailAndPassword(
    auth,
    email,
    password
  );

  const user = userCredential.user;

  await setDoc(doc(db, "users", user.uid), {
    email,
    role,
    createdAt: new Date(),
  });
}

export async function sendRequestToBackend() {
  const user = auth.currentUser;
  if (user) {
    const idToken = await user.getIdToken();

    const response = await fetch("http://localhost:8000/auth/userid", {
      method: "GET",
      headers: {
        Authorization: `Bearer ${idToken}`,
      },
    });

    const data = await response.json();
    console.log("Response:", data);
    return data
  }
}

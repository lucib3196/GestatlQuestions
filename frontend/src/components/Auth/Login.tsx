import React, { useContext, useState, useRef, useEffect } from "react";
import { AuthContext } from "../../context/AuthContext";

import { CloseButton } from "../CloseButton";

function UserLoggedIn(): React.ReactNode {
    const { logout, message } = useContext(AuthContext);
    return (
        <div className="self-start space-y-2 text-black">
            <p className="text-lg ">Thanks for logging in</p>
            <h1 className="font-bold text-2xl">Username: {message?.username}</h1>
            <p
                className="text-blue-500 hover:text-blue-700 hover:font-bold cursor-pointer"
                onClick={logout}
            >
                Log Out?
            </p>
        </div>
    );
}


function PromptUser() {
    const [errorMessage, setErrorMessage] = useState("");
    const [signUp, setSignUp] = useState(false);
    const [signUpSuccess, setSignUpSuccess] = useState(false);

    const handleSignUpSuccess = () => {
        setSignUp(false);
        setSignUpSuccess(true);
        setErrorMessage(""); // clear any leftover errors
    };

    if (!signUp) {
        return (
            <>
                <h2 className="mt-10 text-center text-2xl font-bold tracking-tight text-black my-2">
                    Log in to Your Account
                </h2>

                {signUpSuccess && (
                    <p className="text-green-600 text-sm text-center my-2">
                        ✅ Sign-up successful! Please log in.
                    </p>
                )}

                {errorMessage && (
                    <p className="text-red-500 text-sm text-center my-2">
                        {errorMessage}
                    </p>
                )}

                <LogInForm setErrorMessage={setErrorMessage} />

                <div className="flex justify-start items-center mt-4">
                    <p className="text-xl text-black">
                        Don’t have an account?{" "}
                        <span
                            onClick={() => {
                                setSignUp(true);
                                setSignUpSuccess(false); // reset success message
                            }}
                            className="text-blue-500 hover:text-blue-700 hover:font-bold cursor-pointer"
                        >
                            Sign Up
                        </span>
                    </p>
                </div>
            </>
        );
    }

    return (
        <>
            <h2 className="mt-10 text-center text-2xl font-bold tracking-tight text-black my-2">
                Sign Up
            </h2>

            {errorMessage && (
                <p className="text-red-500 text-sm text-center my-2">
                    {errorMessage}
                </p>
            )}

            <SignUpForm
                setErrorMessage={setErrorMessage}
                onSuccess={handleSignUpSuccess} // 👈 pass success handler
            />
        </>
    );
}


type ModalProps = {
    setShowModal: (visible: boolean) => void;
    children: React.ReactNode;
};

function LogInContainer({
    setShowModal,
    children,
}: ModalProps): React.ReactNode {
    const modalRef = useRef<HTMLDivElement>(null);
    useEffect(() => {
        function handleClickOutside(event: MouseEvent) {
            if (
                modalRef.current &&
                !modalRef.current.contains(event.target as Node)
            ) {
                setShowModal(false);
            }
        }

        document.addEventListener("mousedown", handleClickOutside);
        return () => {
            document.removeEventListener("mousedown", handleClickOutside);
        };
    }, [setShowModal]);

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            <div className="bg-gray-100 w-full max-w-3xl h-auto max-h-[90vh] rounded-lg shadow-2xl overflow-y-auto p-6 sm:p-8">
                <div className="flex flex-col space-y-4">
                    <div className="flex justify-end">
                        <CloseButton onClick={() => setShowModal(false)} />
                    </div>
                    <div className="w-full">
                        {children}
                    </div>
                </div>
            </div>
        </div>
    );
}

type LogInPageProps = {
    showModal: boolean;
    setShowModal: (visible: boolean) => void;
};

function LogInPage({ showModal, setShowModal }: LogInPageProps): React.ReactNode {
    const { isLoggedIn } = useContext(AuthContext);
    console.log("Status", isLoggedIn)
    return (
        <>
            {showModal && (
                <LogInContainer setShowModal={setShowModal}>
                    {isLoggedIn ? <UserLoggedIn /> : <PromptUser />}
                </LogInContainer>
            )}
        </>
    );
}
export default LogInPage;

import { useState } from "react";
import { MyModal } from "../Generic/MyModal";
import QuestionCreationForm from "./QuestionForm";
import { TableToolBarButton } from "../QuestionTable/TableToolBarButtons";
import { FiUpload } from "react-icons/fi";
function Header() {
    return (
        <div className="text-center py-6">
            <h1 className="text-2xl md:text-3xl font-bold text-gray-800">
                Create a Question
                <span className="text-indigo-500"> or Upload from Files</span>
            </h1>
            <p className="mt-2 text-sm md:text-base text-gray-500">
                Start from scratch or import existing files
            </p>
            ;
        </div>
    );
}




export default function CreateQuestion() {
    const [showPopUp, setShowPopUp] = useState(false);

    return (
        <>
            <TableToolBarButton
                value="Upload Question"
                className="border-indigo-600 text-indigo-700 hover:bg-indigo-200 "
                onClick={() => setShowPopUp(prev => !prev)}
                icon={<FiUpload className="self-center" />}
            />
            {showPopUp && (
                <MyModal variant="large" setShowModal={setShowPopUp}>
                    <Header />
                    <QuestionCreationForm onFinish={() => setShowPopUp(false)} />
                </MyModal>
            )}
        </>
    );
}

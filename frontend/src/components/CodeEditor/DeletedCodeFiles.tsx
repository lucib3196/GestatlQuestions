import { MyButton } from "../Base/Button";


export function DeleteCodeFile({
    questionId,
    filename,
    onSubmit,
}: {
    questionId: string;
    filename: string;
    onSubmit: (questionId: string, filename: string) => void;
}) {
    return (
        <div className="flex flex-col items-center justify-center w-full ">
            <h1 className="text-lg font-semibold text-gray-900 mb-2">
                Delete File
            </h1>
            <p className="text-sm text-gray-600 mb-4 text-center">
                Are you sure you want to delete <span className="font-medium">{filename}</span>?
            </p>

            <div className="flex gap-3 w-full justify-center">
                <MyButton
                    name="Cancel"
                    onClick={() => window.history.back()}
                />
                <MyButton
                    name="Delete"
                    onClick={() => onSubmit(questionId, filename)}
                />
            </div>
        </div>
    );
}

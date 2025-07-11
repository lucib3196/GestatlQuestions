type CorrectIndicatorProps = {
    answeredCorrectly: boolean;
    submitted: boolean;
};

function CorrectIndicator({ answeredCorrectly, submitted }: CorrectIndicatorProps) {
    if (!submitted) return null;

    return (
        <div
            className={`flex items-center justify-center ${answeredCorrectly ? "text-green-600" : "text-red-600"
                } font-semibold mt-2`}
            role="status"
            aria-live="polite"
        >
            {answeredCorrectly ? "✅ Correct" : "❌ Incorrect"}
        </div>
    );
}


export default CorrectIndicator
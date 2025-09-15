type ErrorProps = {
    error: string;
};

export const Error = ({ error }: ErrorProps) => {
    return (
        <div className="w-full h-full mx-auto my-8 px-4 ">
            <div className="rounded-lg border border-red-300 bg-red-50 text-red-800 font-semibold p-4 shadow-sm">
                {error}
            </div>
        </div>
    );
};

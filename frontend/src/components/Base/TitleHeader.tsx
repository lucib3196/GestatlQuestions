
type HeaderProps = {
    value: string
}

export function TitleHeader({ value }: HeaderProps) {
    return (
        <div className="flex flex-col items-center text-center space-y-1">
            <h1 className="text-xl font-semibold tracking-tight">{value}</h1>
            <div className="w-16 h-[2px] bg-gray-300 rounded" />
        </div>
    );
}
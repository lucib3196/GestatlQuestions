import { CiCircleQuestion } from "react-icons/ci"
import { useState } from "react"

type PopUpHelpProps = {
    message: string
}
const PopUpHelp: React.FC<PopUpHelpProps> = ({ message }) => {
    const [showMessage, setShowMessage] = useState(false)
    return (
        <div className="relative " role="tooltip">
            <CiCircleQuestion size={20} onMouseEnter={() => setShowMessage(true)} onMouseLeave={() => setShowMessage(false)} />
            {showMessage && <div className="absolute border rounded-md max-w-sm break-words whitespace-pre-wrap px-4 py-2 bg-gray-100 text-gray-800 bottom-full left-1/2 -translate-x-1/2 mb-2 shadow-md">{message}</div>}
        </div>

    )
}

export default PopUpHelp
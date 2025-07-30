
import { useEffect, useRef } from "react";
import { CloseButton } from "../CloseButton";



type ModalProps = {
    setShowModal: (visible: boolean) => void;
    children: React.ReactNode;
};


export function MyModal({ setShowModal, children }: ModalProps) {
    const modalRef = useRef<HTMLDivElement>(null)


    useEffect(() => {
        function handleClickOutside(event: MouseEvent) {
            if (modalRef.current && !modalRef.current.contains(event.target as Node)) {
                setShowModal(false);
            }
        }

        document.addEventListener("mousedown", handleClickOutside);
        return () => {
            document.removeEventListener("mousedown", handleClickOutside);
        }
    }, [setShowModal])
    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-opacity-50">
            <div ref={modalRef} className="bg-white rounded-lg shadow-lg p-8 min-w-[500px] min-h-[300px] flex flex-col">
                <div className="self-end"> <CloseButton onClick={() => setShowModal(false)} /></div>
                {children}
            </div>

        </div>
    )
}
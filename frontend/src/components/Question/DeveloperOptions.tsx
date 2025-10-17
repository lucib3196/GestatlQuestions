import { MyButton } from "../Base/Button";

export default function DeveloperOptions() {
    return (
        <div className="my-10 grid grid-cols-3 gap-10 mb-10">
            <MyButton name={"Edit Code"} color="secondary" />
            <MyButton name={"Submit Review"} color="primary" />
        </div>
    );
}

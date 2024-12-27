
export default function Header()
{

    return (
        <header className="bg-blue-500 w-full flex justify-between">
            <div className="bg-slate-300">
                Page title
            </div>
            <nav className="bg-green-400">
                <ul className="flex w-full">
                    <li>
                        Some 1
                    </li>
                    <li>
                        Some 2
                    </li>
                    <li>
                        Some 3
                    </li>
                </ul>
            </nav>
        </header>
    )
}
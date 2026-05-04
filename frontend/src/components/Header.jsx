import Logo from "./Logo";
import ThemeToggle from "./ThemeToggle";
import UserMenu from "./UserMenu";

export default function Header({ left, right }) {
  return (
    <header className="border-b border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900 px-4 sm:px-6 py-3 sm:py-3.5 flex justify-between items-center gap-2">
      <div className="flex items-center gap-2 sm:gap-3 min-w-0">
        <Logo size={28} />
        {left}
      </div>
      <div className="flex items-center gap-1.5 sm:gap-2 flex-shrink-0">
        {right}
        <ThemeToggle />
        <UserMenu />
      </div>
    </header>
  );
}

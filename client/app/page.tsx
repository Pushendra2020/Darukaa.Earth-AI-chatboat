import Chat from "../components/Chat";

export default function Home() {
  return (
    <main className="min-h-screen bg-[radial-gradient(circle_at_top,_rgba(15,118,110,0.2),transparent_30%),linear-gradient(180deg,#f5f8f4_0%,#eef7f1_100%)] px-4 py-6 md:px-8">
      <div className="mx-auto flex w-full max-w-6xl flex-col gap-5">
        <header className="overflow-hidden rounded-[28px] border border-emerald-200/80 bg-white/70 px-5 py-5 shadow-[0_20px_60px_rgba(10,88,66,0.08)] backdrop-blur-md md:px-7">
          <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
            <div className="flex items-center gap-4">
              <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-br from-emerald-500 to-teal-700 text-xl font-bold text-white shadow-lg shadow-emerald-500/30">
                D
              </div>
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.24em] text-emerald-700/80">
                  Biodiversity intelligence
                </p>
                <h1 className="text-2xl font-black tracking-tight text-slate-900 md:text-3xl">
                  Darukaa.Earth
                </h1>
              </div>
            </div>

            <div className="flex flex-wrap items-center gap-2 text-sm text-slate-700">
              <span className="rounded-full border border-emerald-200 bg-emerald-50 px-3 py-1.5 font-medium text-emerald-800">
                Live ecosystem analysis
              </span>
              <span className="rounded-full border border-slate-200 bg-slate-50 px-3 py-1.5 font-medium">
                Evidence-based
              </span>
            </div>
          </div>
        </header>

        <div className="h-[680px] md:h-[780px]">
          <Chat />
        </div>
      </div>
    </main>
  );
}

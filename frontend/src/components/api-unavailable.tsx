export function ApiUnavailable() {
  return (
    <main className="grid min-h-screen place-items-center px-6">
      <section className="max-w-lg rounded-2xl border border-amber-400/30 bg-amber-400/10 p-8">
        <p className="text-sm font-semibold uppercase tracking-widest text-amber-300">
          API unavailable
        </p>
        <h1 className="mt-3 text-3xl font-semibold text-white">CloudPulse cannot load status data</h1>
        <p className="mt-4 text-slate-300">
          Confirm that FastAPI is running on port 8000, then inspect the backend terminal logs.
        </p>
      </section>
    </main>
  );
}

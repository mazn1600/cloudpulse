import type { DashboardResponse, Deployment } from "@/lib/types";

interface DashboardProps {
  dashboard: DashboardResponse;
  deployments: Deployment[];
}

export function Dashboard({ dashboard, deployments }: DashboardProps) {
  return (
    <main className="mx-auto min-h-screen max-w-6xl px-6 py-10">
      <header className="mb-10 flex items-end justify-between gap-6">
        <div>
          <p className="text-sm font-semibold uppercase tracking-[0.24em] text-cyan-400">
            Infrastructure learning environment
          </p>
          <h1 className="mt-3 text-4xl font-semibold tracking-tight text-white">
            CloudPulse
          </h1>
        </div>
        <span className="rounded-full border border-emerald-400/30 bg-emerald-400/10 px-4 py-2 text-sm text-emerald-300">
          {dashboard.status}
        </span>
      </header>

      <section aria-label="System metrics" className="grid gap-4 md:grid-cols-3">
        <Metric label="CPU usage" value={`${dashboard.metrics.cpu_percent}%`} />
        <Metric label="Memory usage" value={`${dashboard.metrics.memory_percent}%`} />
        <Metric label="Requests/min" value={String(dashboard.metrics.requests_per_minute)} />
      </section>

      <section className="mt-8 grid gap-6 lg:grid-cols-2">
        <Panel title="Service health">
          <ul className="space-y-3">
            {dashboard.services.map((service) => (
              <li key={service.name} className="flex justify-between border-b border-white/10 pb-3">
                <span className="capitalize text-slate-200">{service.name}</span>
                <span className="text-slate-400">{service.status}</span>
              </li>
            ))}
          </ul>
        </Panel>

        <Panel title="Recent deployments">
          {deployments.length === 0 ? (
            <p className="text-slate-400">No deployments recorded.</p>
          ) : (
            <ul className="space-y-3">
              {deployments.map((deployment) => (
                <li key={deployment.id} className="border-b border-white/10 pb-3">
                  <div className="flex justify-between">
                    <span className="font-medium text-white">{deployment.version}</span>
                    <span className="text-emerald-300">{deployment.status}</span>
                  </div>
                  <p className="mt-1 text-sm text-slate-400">{deployment.environment}</p>
                </li>
              ))}
            </ul>
          )}
        </Panel>
      </section>
    </main>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <article className="rounded-2xl border border-white/10 bg-white/5 p-6">
      <p className="text-sm text-slate-400">{label}</p>
      <p className="mt-3 text-3xl font-semibold text-white">{value}</p>
    </article>
  );
}

function Panel({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="rounded-2xl border border-white/10 bg-white/5 p-6">
      <h2 className="mb-5 text-lg font-semibold text-white">{title}</h2>
      {children}
    </section>
  );
}

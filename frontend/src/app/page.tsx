import { ApiUnavailable } from "@/components/api-unavailable";
import { Dashboard } from "@/components/dashboard";
import { getDashboard, getDeployments } from "@/lib/api";

async function loadData() {
  try {
    const [dashboard, deployments] = await Promise.all([
      getDashboard(),
      getDeployments(),
    ]);
    return { dashboard, deployments };
  } catch {
    return null;
  }
}

export default async function Home() {
  const data = await loadData();
  if (!data) {
    return <ApiUnavailable />;
  }
  return <Dashboard dashboard={data.dashboard} deployments={data.deployments} />;
}

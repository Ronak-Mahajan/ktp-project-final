import DashboardPageLayout from "@/components/dashboard/layout";
import DashboardChart from "@/components/dashboard/chart";
import BracketsIcon from "@/components/icons/brackets";

export default function DashboardOverview() {
  return (
    <DashboardPageLayout
      header={{
        title: "SpaceX Launches vs Atlantic Hurricanes",
        description: "Correlation Analysis Dashboard",
        icon: BracketsIcon,
      }}
    >
      <div className="grid gap-6">
        <div className="rounded-lg border-2 border-border bg-card p-6">
          <h2 className="text-lg font-semibold mb-4">Correlation Analysis</h2>
          <div className="h-[300px] flex items-center justify-center border-2 border-dashed border-border rounded-md">
            <p className="text-muted-foreground">Correlation graph will be displayed here</p>
          </div>
        </div>
        
        <div className="rounded-lg border-2 border-border bg-card p-6">
          <h2 className="text-lg font-semibold mb-4">Time Series Data</h2>
          <DashboardChart />
        </div>
      </div>
    </DashboardPageLayout>
  );
}

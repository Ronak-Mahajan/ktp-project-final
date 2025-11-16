import DashboardPageLayout from "@/components/dashboard/layout";
import CorrelationCharts from "@/components/dashboard/correlation-charts";
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
      <CorrelationCharts />
    </DashboardPageLayout>
  );
}

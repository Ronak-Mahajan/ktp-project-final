"use client";

import * as React from "react";
import { XAxis, YAxis, CartesianGrid, Line, LineChart, ReferenceLine } from "recharts";
import {
  ChartConfig,
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
} from "@/components/ui/chart";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

// Get API URL from environment variable, with fallback for local development
const getApiUrl = () => {
  if (process.env.NEXT_PUBLIC_API_URL) {
    return process.env.NEXT_PUBLIC_API_URL;
  }
  // Fallback to localhost for local development
  if (typeof window !== 'undefined' && window.location.hostname === 'localhost') {
    return 'http://localhost:8000';
  }
  // In production without env var, try to infer from current host
  return '';
};

const API_BASE_URL = getApiUrl();

type TimeSeriesData = {
  time: string;
  x: number | null;
  y: number | null;
};

type ResidualData = {
  time: string;
  residual: number | null;
};

type CorrelationData = {
  timeSeries: TimeSeriesData[];
  residuals: ResidualData[];
  correlation: number;
  totalPoints: number;
  overlappingPoints: number;
  tradeOpportunities: number;
};

const timeSeriesChartConfig = {
  x: {
    label: "X (yes_bid_close_x)",
    color: "var(--chart-1)",
  },
  y: {
    label: "Y (yes_bid_close_y)",
    color: "var(--chart-2)",
  },
} satisfies ChartConfig;

const residualsChartConfig = {
  residual: {
    label: "Residual",
    color: "var(--chart-3)",
  },
} satisfies ChartConfig;

export default function CorrelationCharts() {
  const [data, setData] = React.useState<CorrelationData | null>(null);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState<string | null>(null);

  React.useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        const response = await fetch(`${API_BASE_URL}/api/v1/correlation`);
        if (!response.ok) {
          throw new Error(`Failed to fetch data: ${response.statusText}`);
        }
        const result = await response.json();
        setData(result);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to fetch correlation data");
        console.error("Error fetching correlation data:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString("en-US", { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-[400px]">
        <p className="text-muted-foreground">Loading correlation data...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-[400px]">
        <div className="text-center">
          <p className="text-destructive mb-2">Error loading data</p>
          <p className="text-sm text-muted-foreground">{error}</p>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="flex items-center justify-center h-[400px]">
        <p className="text-muted-foreground">No data available</p>
      </div>
    );
  }

  // Prepare data for charts
  const timeSeriesChartData = data.timeSeries.map((item) => ({
    time: formatDate(item.time),
    timestamp: item.time,
    x: item.x ?? 0,
    y: item.y ?? 0,
  }));

  const residualsChartData = data.residuals.map((item) => ({
    time: formatDate(item.time),
    timestamp: item.time,
    residual: item.residual ?? 0,
  }));

  return (
    <div className="grid gap-6">
      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Correlation</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{data.correlation.toFixed(4)}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Total Points</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{data.totalPoints}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Overlapping Points</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{data.overlappingPoints}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Trade Opportunities</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{data.tradeOpportunities}</div>
          </CardContent>
        </Card>
      </div>

      {/* X and Y Time Series Chart */}
      <Card>
        <CardHeader>
          <CardTitle>X and Y Time Series (Overlapping Periods Only)</CardTitle>
          <CardDescription>Price movements over time for both series</CardDescription>
        </CardHeader>
        <CardContent>
          <ChartContainer config={timeSeriesChartConfig} className="h-[400px] w-full">
            <LineChart
              data={timeSeriesChartData}
              margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--muted))" opacity={0.3} />
              <XAxis
                dataKey="time"
                tickLine={false}
                tickMargin={12}
                strokeWidth={1.5}
                className="text-xs fill-muted-foreground"
                angle={-45}
                textAnchor="end"
                height={80}
              />
              <YAxis
                tickLine={false}
                axisLine={false}
                tickMargin={8}
                className="text-xs fill-muted-foreground"
              />
              <ChartTooltip
                content={
                  <ChartTooltipContent
                    indicator="line"
                    className="min-w-[200px] px-4 py-3"
                  />
                }
              />
              <Line
                type="monotone"
                dataKey="x"
                stroke="var(--color-x)"
                strokeWidth={2}
                dot={false}
                activeDot={{ r: 4 }}
                name="X (yes_bid_close_x)"
              />
              <Line
                type="monotone"
                dataKey="y"
                stroke="var(--color-y)"
                strokeWidth={2}
                dot={false}
                activeDot={{ r: 4 }}
                name="Y (yes_bid_close_y)"
              />
            </LineChart>
          </ChartContainer>
        </CardContent>
      </Card>

      {/* Residuals Chart */}
      <Card>
        <CardHeader>
          <CardTitle>Residuals Over Time (Overlapping Periods Only)</CardTitle>
          <CardDescription>Residuals from linear regression model</CardDescription>
        </CardHeader>
        <CardContent>
          <ChartContainer config={residualsChartConfig} className="h-[400px] w-full">
            <LineChart
              data={residualsChartData}
              margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--muted))" opacity={0.3} />
              <XAxis
                dataKey="time"
                tickLine={false}
                tickMargin={12}
                strokeWidth={1.5}
                className="text-xs fill-muted-foreground"
                angle={-45}
                textAnchor="end"
                height={80}
              />
              <YAxis
                tickLine={false}
                axisLine={false}
                tickMargin={8}
                className="text-xs fill-muted-foreground"
              />
              <ReferenceLine y={0} stroke="var(--destructive)" strokeDasharray="5 5" />
              <ChartTooltip
                content={
                  <ChartTooltipContent
                    indicator="line"
                    className="min-w-[200px] px-4 py-3"
                  />
                }
              />
              <Line
                type="monotone"
                dataKey="residual"
                stroke="var(--color-residual)"
                strokeWidth={2}
                dot={false}
                activeDot={{ r: 4 }}
                name="Residual"
              />
            </LineChart>
          </ChartContainer>
        </CardContent>
      </Card>
    </div>
  );
}


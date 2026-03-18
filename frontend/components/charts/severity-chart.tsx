"use client";

import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend } from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface SeverityChartProps {
  data: { name: string; value: number }[];
}

const COLORS = {
  CRITICAL: "#ef4444",
  HIGH: "#fb923c",
  MEDIUM: "#facc15",
  LOW: "#4ade80"
};

export function SeverityChart({ data }: SeverityChartProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Incident Severity Distribution</CardTitle>
      </CardHeader>
      <CardContent className="h-[320px]">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie data={data} dataKey="value" nameKey="name" innerRadius={65} outerRadius={95} paddingAngle={3}>
              {data.map((entry) => (
                <Cell key={entry.name} fill={COLORS[entry.name as keyof typeof COLORS] ?? "#38bdf8"} />
              ))}
            </Pie>
            <Tooltip />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}


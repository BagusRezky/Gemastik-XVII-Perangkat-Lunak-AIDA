import { PieChart, Pie, Tooltip } from "recharts";

const data = [
  { name: "Mobile", value: 240 },
  { name: "Desktop", value: 32 },
  { name: "Tablet", value: 24 },
];

function MyPieChart() {
  return (
    <div className="bg-white shadow rounded-lg">
      <PieChart width={200} height={200}>
        <Pie
          data={data}
          dataKey="value"
          nameKey="name"
          cx="50%"
          cy="50%"
          outerRadius={80}
          fill="#8884d8"
        />
        <Tooltip />
      </PieChart>
    </div>
  );
}

export default MyPieChart;

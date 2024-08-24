
import {
  LineChart,
  Line,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
} from "recharts";

const data = [
  { name: "Jan", value: 400 },
  { name: "Feb", value: 300 },
  { name: "Mar", value: 500 },
  { name: "Apr", value: 200 },
  { name: "May", value: 300 },
  { name: "Jun", value: 400 },
];

function LineGraph() {
  return (
    <div className="bg-white shadow rounded-lg p-4">
      <h4 className="font-bold text-gray-600">
        Total Interaksi yang Melewati Billboard per Bulan
      </h4>
      <LineChart width={1100} height={300} data={data}>
        <Line type="monotone" dataKey="value" stroke="#8884d8" />
        <CartesianGrid stroke="#ccc" />
        <XAxis dataKey="name" />
        <YAxis />
        <Tooltip />
      </LineChart>
    </div>
  );
}

export default LineGraph;

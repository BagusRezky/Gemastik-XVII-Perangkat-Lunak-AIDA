import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip } from "recharts";

const data = [
  { name: "B1", value: 300 },
  { name: "B2", value: 200 },
  { name: "B3", value: 400 },
  { name: "B4", value: 500 },
  { name: "B5", value: 700 },
  { name: "B6", value: 600 },
];

function BarGraph() {
  return (
    <div className="bg-white shadow rounded-lg p-4">
      <h4 className="font-bold text-gray-600">
        Jumlah Interaksi per Billboard
      </h4>
      <BarChart width={400} height={300} data={data}>
        <Bar dataKey="value" fill="#82ca9d" />
        <CartesianGrid stroke="#ccc" />
        <XAxis dataKey="name" />
        <YAxis />
        <Tooltip />
      </BarChart>
    </div>
  );
}

export default BarGraph;

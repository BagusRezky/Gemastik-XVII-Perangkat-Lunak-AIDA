import { useParams } from "react-router-dom";

function BillboardReport() {
  const { billboardName } = useParams(); // Retrieves the billboardName from the URL

  // Simulate fetching data based on billboardName
  const data = [
    { date: "01/01/2024", interactions: 1250, location: "Jl. Bunga Mawar" },
    { date: "02/01/2024", interactions: 700, location: "Jl. Bunga Mawar" },
    // Add more data corresponding to the specific billboard
  ];

  return (
    <div className="p-4">
      <h2 className="text-lg font-bold mb-4">Report {billboardName}</h2>
      <table className="min-w-full">
        <thead>
          <tr>
            <th>Nama Billboard</th>
            <th>Tanggal</th>
            <th>Total Interaksi</th>
            <th>Lokasi</th>
          </tr>
        </thead>
        <tbody>
          {data.map((item, index) => (
            <tr key={index}>
              <td>{billboardName}</td>
              <td>{item.date}</td>
              <td>{item.interactions}</td>
              <td>{item.location}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default BillboardReport;

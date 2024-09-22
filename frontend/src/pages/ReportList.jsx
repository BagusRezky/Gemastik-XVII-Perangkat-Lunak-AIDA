import ReportItem from "../components/ReportItem";
function ReportList() {
  const reports = [
    { id: 1, name: "Billboard A", address: "Jl. Bunga Mawar" },
    // { id: 2, name: "Billboard B", address: "Jl. Bunga Melati" },
    // { id: 3, name: "Billboard C", address: "Jl. Danau Toba" },
    // { id: 4, name: "Billboard D", address: "Jl. Bunga Tulip" },
    // { id: 5, name: "Billboard E", address: "Jl. Bunga Matahari" },
    // { id: 6, name: "Billboard F", address: "Jl. Jakarta" },
  ];

  return (
    <div className="p-4">
      <h2 className="text-lg font-bold mb-4">All Report</h2>
      {reports.map((report) => (
        <ReportItem
          key={report.id}
          name={report.name}
          address={report.address}
        />
      ))}
    </div>
  );
}

export default ReportList;
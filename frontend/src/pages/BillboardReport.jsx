import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import axios from "axios";
import jsPDF from "jspdf";
import "jspdf-autotable";

function BillboardReport() {
  const { billboardName } = useParams();
  const [data, setData] = useState([]);
  const [filteredData, setFilteredData] = useState([]);
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get(
          `http://localhost:3000/interactions/BillboardA`
        );
        setData(response.data);
        setFilteredData(response.data); // Inisialisasi dengan semua data
      } catch (error) {
        console.error("Error fetching data:", error);
      }
    };

    fetchData();
  }, [billboardName]);

  // Fungsi untuk memfilter data berdasarkan tanggal
  const handleFilter = () => {
    if (startDate && endDate) {
      const filtered = data.filter((item) => {
        const itemDate = new Date(item.timestamp).toISOString().split("T")[0];
        return itemDate >= startDate && itemDate <= endDate;
      });
      setFilteredData(filtered);
    } else {
      setFilteredData(data); // Jika tanggal tidak di-set, tampilkan semua data
    }
  };

  // Fungsi untuk mengunduh PDF berdasarkan data yang difilter
  const downloadPDF = () => {
    const doc = new jsPDF();

    doc.text(`Report for ${billboardName}`, 20, 10);

    const tableColumn = [
      "Tanggal",
      "Jumlah Kendaraan Kebawah",
      "Jumlah Kendaraan Keatas",
    ];
    const tableRows = [];

    filteredData.forEach((item) => {
      const itemData = [
        new Date(item.timestamp).toLocaleDateString(),
        item.going_down,
        item.going_up,
      ];
      tableRows.push(itemData);
    });

    doc.autoTable({
      head: [tableColumn],
      body: tableRows,
      startY: 20,
    });

    doc.save(`report_${billboardName}.pdf`);
  };

  return (
    <div className="p-4">
      <h2 className="text-lg font-bold mb-4">Report {billboardName}</h2>

      <div className="mb-4">
        <label className="mr-2">Start Date:</label>
        <input
          type="date"
          value={startDate}
          onChange={(e) => setStartDate(e.target.value)}
          className="border p-1 mr-4"
        />
        <label className="mr-2">End Date:</label>
        <input
          type="date"
          value={endDate}
          onChange={(e) => setEndDate(e.target.value)}
          className="border p-1 mr-4"
        />
        <button
          onClick={handleFilter}
          className="bg-blue-500 text-white p-2 rounded"
        >
          Filter
        </button>
      </div>

      <button
        onClick={downloadPDF}
        className="mb-4 bg-blue-500 text-white p-2 rounded"
      >
        Download PDF
      </button>

      <table className="min-w-full">
        <thead>
          <tr>
            <th>Tanggal</th>
            <th>Jumlah Kendaraan Kebawah</th>
            <th>Jumlah Kendaraan Keatas</th>
          </tr>
        </thead>
        <tbody>
          {filteredData.map((item, index) => (
            <tr key={index}>
              <td>{new Date(item.timestamp).toLocaleDateString()}</td>
              <td>{item.going_down}</td>
              <td>{item.going_up}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default BillboardReport;

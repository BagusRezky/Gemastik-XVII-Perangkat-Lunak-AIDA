import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import axios from "axios";
import jsPDF from "jspdf";
import "jspdf-autotable";

function BillboardReport() {
  const { billboardName } = useParams();
  const [data, setData] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get(
          `http://localhost:3000/interactions/BillboardA`
        );
        setData(response.data);
      } catch (error) {
        console.error("Error fetching data:", error);
      }
    };

    fetchData();
  }, [billboardName]);

  const downloadPDF = () => {
    const doc = new jsPDF();

    doc.text(`Report for ${billboardName}`, 20, 10);

    const tableColumn = ["Tanggal", "Total Interaksi"];
    const tableRows = [];

    data.forEach((item) => {
      const itemData = [
        new Date(item.timestamp).toLocaleDateString(),
        item.interactions,
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
            <th>Total Interaksi</th>
          </tr>
        </thead>
        <tbody>
          {data.map((item, index) => (
            <tr key={index}>
              <td>{new Date(item.timestamp).toLocaleDateString()}</td>
              <td>{item.interactions}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default BillboardReport;

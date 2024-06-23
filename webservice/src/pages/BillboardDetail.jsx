import { useParams } from "react-router-dom";
import Rectangle215 from "../assets/Rectangle215.png"; // example image, replace with actual path

function BillboardDetail() {
  const { id } = useParams();

  // Fetch billboard data based on id or use dummy data for now
  const billboard = {
    id,
    image: Rectangle215, // updated path to the uploaded image
    size: "4x8",
    address: "Jl. Raya Bogor, No. 5, Jakarta",
    interactions: 2,
    date: "Kamis, 7 Februari 2024",
    time: "13.40",
    location: "Jl. Soekarno Hatta",
  };

  return (
    <div>
      <h2 className="text-2xl font-bold mb-4">Billboard Detail</h2>
      <div className="flex flex-wrap justify-around items-center mt-2">
        <img src={billboard.image} alt="Billboard" width={850} height={200} />
        {/* <div className="absolute top-0 left-0 p-4 text-yellow-500 text-lg">
            <p>{`going down: ${billboard.interactions}`}</p>
            <p>{`going up: ${billboard.interactions - 15}`}</p>
            <p className="mt-20">{`1 line`}</p>
            <p className="mt-2">{`2 line`}</p>
          </div> */}

        <div className="bg-gray-100 p-9 rounded">
          <p className="text-md mb-2">{`Hari/Tanggal: ${billboard.date}`}</p>
          <p className="text-md mb-2">{`Lokasi: ${billboard.location}`}</p>
          <p className="text-md mb-2">{`Waktu: ${billboard.time}`}</p>
          <div className="mt-10 text-center">
            <p className="text-2xl font-bold">Jumlah Interaksi</p>
            <p className="text-5xl font-bold">{billboard.interactions}</p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default BillboardDetail;

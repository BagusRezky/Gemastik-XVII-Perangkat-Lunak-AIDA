import BillboardItem from "../components/BillboardItem";
import Rectangle215 from "../assets/Rectangle215.png";

function AllBillboard() {

    const billboards = [
        {
          id: 1,
          image: Rectangle215,
          size: "4x8",
          address: "Jl. Raya Bogor, No. 5, Jakarta"
        },
        {
          id: 2,
          image: Rectangle215,
          size: "4x8",
          address: "Jl. Raya Bogor, No. 5, Jakarta"
        },
        {
          id: 3,
          image: Rectangle215,
          size: "4x8",
          address: "Jl. Raya Bogor, No. 5, Jakarta"
        },
        {
          id: 4,
          image: Rectangle215,
          size: "4x8",
          address: "Jl. Raya Bogor, No. 5, Jakarta"
        },
        {
          id: 5,
          image: Rectangle215,
          size: "4x8",
          address: "Jl. Raya Bogor, No. 5, Jakarta"
        },
        {
          id: 6,
          image: Rectangle215,
          size: "4x8",
          address: "Jl. Raya Bogor, No. 5, Jakarta"
        },
        {
          id: 7,
          image: Rectangle215,
          size: "4x8",
          address: "Jl. Raya Bogor, No. 5, Jakarta"
        },
        {
          id: 8,
          image: Rectangle215,
          size: "4x8",
          address: "Jl. Raya Bogor, No. 5, Jakarta"
        },
      ];

    return (
      <div>
        <h2 className="text-2xl font-bold text-gray-600">All Billboards</h2>
        <div className="p-8">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-3 gap-3 p-3">
            {billboards.map((billboard) => (
              <BillboardItem
                key={billboard.id}
                image={billboard.image}
                size={billboard.size}
                address={billboard.address}
              />
            ))}
          </div>
        </div>
      </div>
    );
}

export default AllBillboard;
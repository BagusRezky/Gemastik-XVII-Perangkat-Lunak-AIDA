import StatsCard from "../components/StatsCard";
import LineGraph from "../components/LineGraph";
import BarGraph from "../components/BarGraph";
import PieChart from "../components/PieChart";

function DashboardContainer() {
  return (
    <div>
    <h2 className="text-2xl font-bold text-gray-600">Dashboard</h2>
      <div className="p-8">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatsCard
            title="Total Interactions"
            value="7,265"
            percentage="11.02%"
          />
          <StatsCard
            title="Total Engagement"
            value="3,671"
            percentage="-0.23%"
          />
          <StatsCard
            title="Total Billboard Views"
            value="156"
            percentage="+85.02%"
          />
          <StatsCard title="Total Travel" value="2,318" percentage="4.03%" />
        </div>
        <div className="p-8">
          <LineGraph />
        </div>
        <div className="flex flex-wrap justify-around items-center mt-4">
          <BarGraph />
          <PieChart />
        </div>
      </div>
    </div>
  );
}

export default DashboardContainer;

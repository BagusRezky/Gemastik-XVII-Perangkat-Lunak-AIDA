import PropTypes from "prop-types";

function StatsCard({ title, value, percentage }) {
  return (
    <div className="bg-white shadow rounded-lg p-4">
      <h4 className="font-bold text-gray-600">{title}</h4>
      <div className="text-3xl font-bold">
        {value}
        <span className="text-sm font-normal text-gray-500 ml-2">
          {percentage}
        </span>
      </div>
    </div>
  );
}


// Define PropTypes for StatsCard
StatsCard.propTypes = {
  title: PropTypes.string.isRequired,  // title must be a string and is required
  value: PropTypes.string.isRequired,  // value must be a string and is required
  percentage: PropTypes.string  // percentage must be a string but is not required
};

export default StatsCard;

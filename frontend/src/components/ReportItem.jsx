import PropTypes from "prop-types";
import { Link } from "react-router-dom";

function ReportItem({ name, address }) {
  return (
    <div className="flex justify-between items-center bg-gray-100 rounded-lg p-3 my-2 shadow-sm">
      <div>
        <span className="font-semibold">{name}</span>
        <span className="text-gray-600 ml-4">{address}</span>
      </div>
      <div>
        
        <Link
          to={`/report/${name}`}
          className="text-green-500 hover:text-green-700"
        >
          Report
        </Link>
      </div>
    </div>
  );
}

ReportItem.propTypes = {
  name: PropTypes.string.isRequired,
  address: PropTypes.string.isRequired,
};

export default ReportItem;

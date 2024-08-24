import db from "../../config/db.js";

const getLatestInteraction = (req, res) => {
  const query = "SELECT * FROM interactions ORDER BY id DESC LIMIT 1";
  db.query(query, (err, result) => {
    if (err) {
      res.status(500).send(err);
    } else {
      res.send(result[0]);
    }
  });
};

const getInteractionByBillboardName = (req, res) => {
  const { billboardName } = req.params;
  const query =
    "SELECT timestamp, going_down as interactions FROM interactions WHERE billboard_name = ?";
  db.query(query, [billboardName], (err, results) => {
    if (err) {
      res.status(500).send(err);
    } else {
      res.send(results);
    }
  });
};

export default { getLatestInteraction, getInteractionByBillboardName };

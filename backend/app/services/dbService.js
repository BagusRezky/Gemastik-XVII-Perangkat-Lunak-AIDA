import db from "../../config/db.js";

const saveToDatabase = (goingDown, goingUp, billboardName) => {
  const query =
    "INSERT INTO interactions (going_down, going_up, billboard_name) VALUES (?, ?, ?)";
  console.log("Saving data to database:", goingDown, goingUp, billboardName);
  db.query(query, [goingDown, goingUp, billboardName], (err) => {
    if (err) {
      console.error("Error saving data to database:", err);
    } else {
      console.log("Data saved to database");
    }
  });
};

export default { saveToDatabase };
